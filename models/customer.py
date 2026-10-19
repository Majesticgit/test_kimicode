"""Customer information models."""
from pydantic import BaseModel, Field


class CustomerInfo(BaseModel):
    """Customer details captured at checkout."""

    name: str = Field(..., min_length=1, max_length=100, description="Customer full name")
    phone: str = Field(..., min_length=5, max_length=20, description="Contact phone number")
    address: str = Field(..., min_length=1, max_length=300, description="Delivery address")
