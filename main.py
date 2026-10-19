"""Fruit Store FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import admin, inventory, orders

app = FastAPI(
    title="Fresh Fruit Store",
    description="Order white peach, red apple, and watermelon online.",
    version="1.0.0",
)

# Allow the simple static frontend to call the API without CORS issues.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(admin.router)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    """Liveness probe."""
    return {"status": "ok"}


# Static frontend files (HTML/CSS/JS)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
