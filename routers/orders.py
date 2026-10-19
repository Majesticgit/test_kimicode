"""Customer order endpoints: create and view orders."""
from fastapi import APIRouter, HTTPException, status

from models.requests import OrderCreateRequest
from models.responses import OrderResponse
from services.store import store

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(request: OrderCreateRequest) -> OrderResponse:
    """Place a new order and deduct stock atomically."""
    try:
        return store.create_order(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.get("", response_model=list[OrderResponse])
def list_orders() -> list[OrderResponse]:
    """Return the full order history."""
    return store.list_orders()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str) -> OrderResponse:
    """Return a single order by ID."""
    try:
        return store.get_order(order_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
