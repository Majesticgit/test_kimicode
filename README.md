# Fresh Fruit Store

A small but complete FastAPI web application that lets customers order three kinds of fruits online while keeping a JSON-backed warehouse inventory.

## Features

- **Frontend**: Simple HTML/CSS/JS shopping page
- **Backend**: FastAPI + Pydantic data validation
- **Fruits**: White Peach, Red Apple, Watermelon
- **Initial stock**: 1000 units per fruit
- **Customer limit**: Max 20 of each fruit per order (clamped automatically)
- **Order flow**: stock check → payment total → deduct stock → confirm order
- **Out-of-stock handling**: clear HTTP 422 error before deducting anything
- **Order history**: list all confirmed orders
- **Admin**: restock inventory or reset to defaults
- **Persistence**: all data saved to `data/store.json`

## Project Structure

```
.
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── models/                 # Pydantic models
│   ├── fruit.py            # FruitType enum
│   ├── customer.py         # CustomerInfo model
│   ├── requests.py         # API request payloads
│   └── responses.py        # API response payloads
├── routers/                # API route modules
│   ├── inventory.py        # GET /inventory
│   ├── orders.py           # POST/GET /orders
│   └── admin.py            # POST /admin/restock, etc.
├── services/               # Business logic + JSON store
│   └── store.py            # Thread-safe Store singleton
├── data/                   # JSON persistence
│   └── store.json
└── static/                 # Frontend assets
    ├── index.html
    ├── style.css
    └── app.js
```

## Run Locally

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the server:

```bash
uvicorn main:app --reload
```

4. Open the shop:

```
http://127.0.0.1:8000/
```

5. Browse the interactive API docs:

```
http://127.0.0.1:8000/docs
```

## Example API Calls

### Get inventory

```bash
curl http://127.0.0.1:8000/inventory
```

### Place an order

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer": {
      "name": "Alice",
      "phone": "+1234567890",
      "address": "123 Orchard Lane"
    },
    "items": [
      {"fruit_type": "white_peach", "quantity": 5},
      {"fruit_type": "red_apple", "quantity": 10}
    ]
  }'
```

### Admin restock

```bash
curl -X POST http://127.0.0.1:8000/admin/restock \
  -H "Content-Type: application/json" \
  -d '{"fruit_type": "watermelon", "quantity": 200}'
```

### Admin set exact stock

```bash
curl -X POST http://127.0.0.1:8000/admin/stock \
  -H "Content-Type: application/json" \
  -d '{"fruit_type": "watermelon", "quantity": 50}'
```

### Reset inventory to defaults

```bash
curl -X POST http://127.0.0.1:8000/admin/reset-inventory
```

### List orders

```bash
curl http://127.0.0.1:8000/orders
```

## Smoke Tests

A small test suite is included:

```bash
python test_smoke.py
```
