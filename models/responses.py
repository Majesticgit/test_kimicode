"""Pydantic response models returned by API endpoints."""
from typing import List

from pydantic import BaseModel

from models.customer import CustomerInfo
from models.fruit import FruitType


class InventoryItemResponse(BaseModel):
    """Current stock level and pricing for one fruit."""

    fruit_type: FruitType
    quantity: int
    unit_price: float


class OrderItemResponse(BaseModel):
    """A resolved order line including price breakdown."""

    fruit_type: FruitType
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    """Confirmed order returned to the client."""

    order_id: str
    customer: CustomerInfo
    items: List[OrderItemResponse]
    total_amount: float
    status: str
    created_at: str
