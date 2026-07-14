# Order Tracker

A small full-stack order management app: Flask API backend, in-memory storage, and a simple HTML/JS frontend.

## Quick start

```bash
cd "order tracker"
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements-dev.txt
python -m backend.app
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser.

Run tests:

```bash
pytest
```

## Docker (optional)

Docker packages the app into a **container** — a small, isolated environment with Python and your code already set up. Anyone with Docker can run the app the same way without installing Python or creating a venv locally.

### Docker Compose (easiest)

**Docker Compose** is a small config file that describes how to run your container(s). Instead of typing a long `docker build` + `docker run` command each time, you run:

```bash
docker compose up --build
```

Compose reads `docker-compose.yml`, builds the image if needed, starts the container, and wires up port 8080. Stop with `Ctrl+C`, or run detached with `docker compose up -d` and stop later with `docker compose down`.

Open [http://127.0.0.1:8080](http://127.0.0.1:8080).

### Plain Docker commands

Build the image (from the `order tracker` directory):

```bash
docker build -t order-tracker .
```

Run the container:

```bash
docker run --rm -p 8080:8080 order-tracker
```

- `docker build` reads the `Dockerfile` and creates an image (a snapshot of your app + dependencies).
- `docker run` starts a container from that image. `-p 8080:8080` maps port 8080 on your machine to port 8080 inside the container.
- `docker compose up` does both steps from `docker-compose.yml` in one command.

### Why two requirements files?

| File | Used by | Contains |
|------|---------|----------|
| `backend/requirements.txt` | Docker / running the app | Flask only |
| `backend/requirements-dev.txt` | Local development | Flask + pytest |

The Docker image only needs what runs the server. **pytest is for testing**, not for serving requests — leaving it out makes the image smaller and builds slightly faster.

**pytest still works on your machine.** Install with `pip install -r backend/requirements-dev.txt` in your venv and run `pytest` as usual. Docker and local dev are separate paths:

- **Local:** venv + `requirements-dev.txt` → run app + run tests
- **Docker:** `requirements.txt` → run app only inside the container

## Project structure

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── Dockerfile
├── docker-compose.yml
├── openapi.yaml
├── pytest.ini
└── README.md
```

## API reference

**Base URL:** `http://127.0.0.1:8080`

All API responses use JSON. Errors return a consistent shape:

```json
{"error": "Human-readable message"}
```

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request (invalid JSON, missing fields, duplicate order) |
| 404 | Not found |
| 405 | Method not allowed |

OpenAPI spec: see [openapi.yaml](openapi.yaml).

### Order object

```json
{
  "order_id": "ORD001",
  "item_name": "Laptop",
  "quantity": 1,
  "customer_id": "CUST001",
  "status": "pending"
}
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/orders` | Create an order |
| GET | `/api/orders` | List all orders (optional `?status=` filter) |
| GET | `/api/orders/{order_id}` | Get one order |
| PUT | `/api/orders/{order_id}/status` | Update order status |
| DELETE | `/api/orders/{order_id}` | Delete an order |

---

### Create order — `POST /api/orders`

**Request body:**

```json
{
  "order_id": "ORD001",
  "item_name": "Laptop",
  "quantity": 1,
  "customer_id": "CUST001",
  "status": "pending"
}
```

`status` is optional (defaults to `"pending"`).

```bash
curl -X POST http://127.0.0.1:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ORD001","item_name":"Laptop","quantity":1,"customer_id":"CUST001"}'
```

**Response `201`:**

```json
{"order_id": "ORD001"}
```

---

### List orders — `GET /api/orders`

```bash
curl http://127.0.0.1:8080/api/orders
```

Filter by status:

```bash
curl "http://127.0.0.1:8080/api/orders?status=pending"
```

**Response `200`:** array of order objects.

---

### Get one order — `GET /api/orders/{order_id}`

```bash
curl http://127.0.0.1:8080/api/orders/ORD001
```

**Response `200`:** order object. **Response `404`:** order not found.

---

### Update status — `PUT /api/orders/{order_id}/status`

**Request body:**

```json
{"new_status": "shipped"}
```

```bash
curl -X PUT http://127.0.0.1:8080/api/orders/ORD001/status \
  -H "Content-Type: application/json" \
  -d '{"new_status":"shipped"}'
```

**Response `200`:**

```json
{"status": "shipped"}
```

---

### Delete order — `DELETE /api/orders/{order_id}`

```bash
curl -X DELETE http://127.0.0.1:8080/api/orders/ORD001
```

**Response `200`:**

```json
{"message": "Order ORD001 deleted successfully"}
```

---

## Reflection

### Design decision: thin API, exceptions in OrderTracker

Business rules live in `OrderTracker`; Flask routes parse the request, call the tracker, and return JSON + an HTTP status.

`OrderTracker` raises `ValueError` for invalid cases (duplicate ID, missing order). Centralized Flask error handlers map those to HTTP status codes (`400` for duplicates/validation, `404` for not found). List endpoints return `list(orders.values())` so clients get an array while storage stays keyed by ID.

### Testing insight: the filter test that exposed a create bug

`test_list_orders_by_status_api_matching` failed with `assert 2 == 1` even though the query param `status=pending` was correct. Print debugging showed both orders were saved as `"pending"`, including the one the test created with `"status": "shipped"`.

The list/filter logic was fine. The real bug was in `add_order_api`: it never passed `status` into `order_tracker.add_order`, so the default `"pending"` always won. Fixing create (forwarding `status` from the JSON) made the filter test pass.

### Next steps

1. **Persistent storage** — replace (or back) `InMemoryStorage` with SQLite so orders survive server restarts.
2. **Custom exception types** — replace message-based error mapping with `OrderNotFoundError` / `DuplicateOrderError`.
