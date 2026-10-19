"""JSON-backed store with inventory and order history."""
import json
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, List

from models.customer import CustomerInfo
from models.fruit import FruitType
from models.requests import OrderCreateRequest, RestockRequest, SetStockRequest
from models.responses import InventoryItemResponse, OrderItemResponse, OrderResponse

DATA_PATH = Path(__file__).parent.parent / "data" / "store.json"

_INITIAL_INVENTORY = {
    FruitType.WHITE_PEACH.value: {"quantity": 1000, "unit_price": 3.5},
    FruitType.RED_APPLE.value: {"quantity": 1000, "unit_price": 2.0},
    FruitType.WATERMELON.value: {"quantity": 1000, "unit_price": 5.0},
}


class Store:
    """Thread-safe singleton store persisted to JSON."""

    _instance = None
    _init_lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_store()
        return cls._instance

    def _init_store(self) -> None:
        self._lock = Lock()
        self._data = self._load()

    def _load(self) -> dict:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not DATA_PATH.exists():
            return {"inventory": deepcopy(_INITIAL_INVENTORY), "orders": []}
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self) -> None:
        """Atomic write to avoid corrupting the JSON file."""
        temp_path = DATA_PATH.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        temp_path.replace(DATA_PATH)

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------
    def get_inventory(self) -> List[InventoryItemResponse]:
        with self._lock:
            return [
                InventoryItemResponse(
                    fruit_type=FruitType(fruit),
                    quantity=info["quantity"],
                    unit_price=info["unit_price"],
                )
                for fruit, info in self._data["inventory"].items()
            ]

    def get_stock(self, fruit_type: FruitType) -> int:
        with self._lock:
            return self._data["inventory"][fruit_type.value]["quantity"]

    def restock(self, request: RestockRequest) -> InventoryItemResponse:
        with self._lock:
            item = self._data["inventory"][request.fruit_type.value]
            item["quantity"] += request.quantity
            self._save()
            return InventoryItemResponse(
                fruit_type=request.fruit_type,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )

    def reset_inventory(self) -> List[InventoryItemResponse]:
        """Reset all fruit quantities to the initial 1000 units."""
        with self._lock:
            for fruit in _INITIAL_INVENTORY:
                self._data["inventory"][fruit]["quantity"] = _INITIAL_INVENTORY[fruit]["quantity"]
            self._save()
            return [
                InventoryItemResponse(
                    fruit_type=FruitType(fruit),
                    quantity=info["quantity"],
                    unit_price=info["unit_price"],
                )
                for fruit, info in self._data["inventory"].items()
            ]

    def set_stock(self, request: SetStockRequest) -> InventoryItemResponse:
        """Set the exact stock level for a specific fruit type."""
        with self._lock:
            item = self._data["inventory"][request.fruit_type.value]
            item["quantity"] = request.quantity
            self._save()
            return InventoryItemResponse(
                fruit_type=request.fruit_type,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------
    def create_order(self, request: OrderCreateRequest) -> OrderResponse:
        with self._lock:
            # Aggregate quantities per fruit and enforce the 20-per-type limit.
            aggregated: Dict[str, int] = {}
            for item in request.items:
                aggregated[item.fruit_type.value] = min(
                    aggregated.get(item.fruit_type.value, 0) + item.quantity, 20
                )

            # Drop zero-quantity lines so they do not affect stock or totals.
            aggregated = {k: v for k, v in aggregated.items() if v > 0}

            if not aggregated:
                raise ValueError("No valid items in order")

            # Check stock availability before deducting.
            out_of_stock = []
            for fruit, qty in aggregated.items():
                available = self._data["inventory"][fruit]["quantity"]
                if available < qty:
                    out_of_stock.append(
                        f"{fruit}: requested {qty}, available {available}"
                    )
            if out_of_stock:
                raise ValueError("Out of stock: " + "; ".join(out_of_stock))

            # Deduct stock and guarantee non-negative quantities.
            for fruit, qty in aggregated.items():
                self._data["inventory"][fruit]["quantity"] = max(
                    self._data["inventory"][fruit]["quantity"] - qty, 0
                )

            # Build the confirmed order.
            order_id = str(uuid.uuid4())[:8]
            created_at = datetime.now(timezone.utc).isoformat()
            order_items: List[OrderItemResponse] = []
            total_amount = 0.0

            for fruit, qty in aggregated.items():
                unit_price = self._data["inventory"][fruit]["unit_price"]
                subtotal = round(qty * unit_price, 2)
                total_amount += subtotal
                order_items.append(
                    OrderItemResponse(
                        fruit_type=FruitType(fruit),
                        quantity=qty,
                        unit_price=unit_price,
                        subtotal=subtotal,
                    )
                )

            total_amount = round(total_amount, 2)
            order_record = {
                "order_id": order_id,
                "customer": request.customer.model_dump(),
                "items": [item.model_dump() for item in order_items],
                "total_amount": total_amount,
                "status": "confirmed",
                "created_at": created_at,
            }

            self._data["orders"].append(order_record)
            self._save()

            return OrderResponse(
                order_id=order_id,
                customer=request.customer,
                items=order_items,
                total_amount=total_amount,
                status="confirmed",
                created_at=created_at,
            )

    def list_orders(self) -> List[OrderResponse]:
        with self._lock:
            return [self._record_to_response(record) for record in self._data["orders"]]

    def get_order(self, order_id: str) -> OrderResponse:
        with self._lock:
            for record in self._data["orders"]:
                if record["order_id"] == order_id:
                    return self._record_to_response(record)
            raise KeyError(f"Order {order_id} not found")

    @staticmethod
    def _record_to_response(record: dict) -> OrderResponse:
        return OrderResponse(
            order_id=record["order_id"],
            customer=CustomerInfo(**record["customer"]),
            items=[OrderItemResponse(**item) for item in record["items"]],
            total_amount=record["total_amount"],
            status=record["status"],
            created_at=record["created_at"],
        )


store = Store()
