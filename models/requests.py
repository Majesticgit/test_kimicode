"""Pydantic request models for incoming API payloads."""
from typing import List

from pydantic import BaseModel, Field, field_validator

from models.customer import CustomerInfo
from models.fruit import FruitType


class OrderItemRequest(BaseModel):
    """A single fruit line item in a customer order."""

    fruit_type: FruitType
    quantity: int = Field(..., ge=0, description="Number of items (max 20)")

    @field_validator("quantity", mode="after")
    @classmethod
    def clamp_to_customer_limit(cls, value: int) -> int:
        """Enforce the per-fruit online customer limit of 20."""
        return min(value, 20)


class OrderCreateRequest(BaseModel):
    """Payload required to place a new order."""

    customer: CustomerInfo
    items: List[OrderItemRequest] = Field(..., min_length=1, description="At least one item")


class RestockRequest(BaseModel):
    """Admin payload to add stock for a fruit type."""

    fruit_type: FruitType
    quantity: int = Field(..., gt=0, description="Amount to add to inventory")


class SetStockRequest(BaseModel):
    """Admin payload to set the exact stock level for a fruit type."""

    fruit_type: FruitType
    quantity: int = Field(..., ge=0, description="Exact stock level to set")
