"""Admin endpoints: inventory management and full order overview."""
from fastapi import APIRouter, HTTPException, status

from models.requests import RestockRequest, SetStockRequest
from models.responses import InventoryItemResponse, OrderResponse
from services.store import store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/restock", response_model=InventoryItemResponse)
def restock_fruit(request: RestockRequest) -> InventoryItemResponse:
    """Add stock for a specific fruit type."""
    return store.restock(request)


@router.post("/stock", response_model=InventoryItemResponse)
def set_fruit_stock(request: SetStockRequest) -> InventoryItemResponse:
    """Set the exact stock level for a specific fruit type."""
    return store.set_stock(request)


@router.get("/orders", response_model=list[OrderResponse])
def admin_list_orders() -> list[OrderResponse]:
    """Admin view of all orders."""
    return store.list_orders()


@router.post("/reset-inventory", response_model=list[InventoryItemResponse])
def reset_inventory() -> list[InventoryItemResponse]:
    """Reset inventory back to the default 1000 units per fruit (dev helper)."""
    return store.reset_inventory()
