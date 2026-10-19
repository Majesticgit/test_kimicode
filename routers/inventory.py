"""Inventory endpoints: public stock queries."""
from fastapi import APIRouter, HTTPException, status

from models.fruit import FruitType
from models.responses import InventoryItemResponse
from services.store import store

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryItemResponse])
def get_inventory() -> list[InventoryItemResponse]:
    """Return current stock levels and unit prices for all fruits."""
    return store.get_inventory()


@router.get("/{fruit_type}", response_model=InventoryItemResponse)
def get_fruit_stock(fruit_type: FruitType) -> InventoryItemResponse:
    """Return current stock level and unit price for a single fruit."""
    for item in store.get_inventory():
        if item.fruit_type == fruit_type:
            return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Fruit type '{fruit_type.value}' not found",
    )
