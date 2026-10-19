"""Quick smoke tests for the fruit store API."""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_inventory_initial_stock():
    r = client.get("/inventory")
    assert r.status_code == 200
    inv = {item["fruit_type"]: item for item in r.json()}
    assert inv["white_peach"]["quantity"] == 1000
    assert inv["red_apple"]["quantity"] == 1000
    assert inv["watermelon"]["quantity"] == 1000


def test_create_order_deducts_stock():
    r = client.post(
        "/orders",
        json={
            "customer": {
                "name": "Alice",
                "phone": "+1234567890",
                "address": "123 Orchard Lane",
            },
            "items": [
                {"fruit_type": "white_peach", "quantity": 5},
                {"fruit_type": "red_apple", "quantity": 10},
            ],
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "confirmed"
    assert body["total_amount"] == 5 * 3.5 + 10 * 2.0
    assert any(item["fruit_type"] == "white_peach" and item["quantity"] == 5 for item in body["items"])

    r = client.get("/inventory/white_peach")
    assert r.json()["quantity"] == 995


def test_quantity_clamped_to_twenty():
    r = client.post(
        "/orders",
        json={
            "customer": {
                "name": "Bob",
                "phone": "+1234567890",
                "address": "123 Farm Road",
            },
            "items": [{"fruit_type": "watermelon", "quantity": 999}],
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["items"][0]["quantity"] == 20


def test_out_of_stock():
    client.post("/admin/reset-inventory")
    client.post("/admin/stock", json={"fruit_type": "watermelon", "quantity": 0})
    r = client.post("/orders", json={
        "customer": {"name": "Dave", "phone": "+1234567890", "address": "B"},
        "items": [{"fruit_type": "watermelon", "quantity": 1}],
    })
    assert r.status_code == 422
    assert "Out of stock" in r.json()["detail"]


if __name__ == "__main__":
    test_health()
    test_inventory_initial_stock()
    test_create_order_deducts_stock()
    test_quantity_clamped_to_twenty()
    test_out_of_stock()
    print("All smoke tests passed.")
