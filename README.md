
# Reflection

## Design decision: thin API, exceptions in OrderTracker

I kept business rules in `OrderTracker` and treated the Flask routes as a thin layer: parse the request, call the tracker, return JSON + an HTTP status.

A trade-off there is how “not found” / “duplicate” is signaled. `OrderTracker` raises `ValueError`; the API catches it and maps it to HTTP (`404` for missing orders, `400` for duplicates). That keeps the tracker reusable and testable without Flask, but it means every route that can fail that way needs a matching `try`/`except`. If I had returned `None` instead of raising, the API could use simple `if`/`else` checks—but unit tests already expected exceptions, and exceptions make invalid cases hard to ignore.

Another small API decision: list endpoints convert the tracker’s order **dict** into a **list** of order objects (`list(orders.values())`) so the frontend and tests can use array indexing (`response.json[0]['order_id']`). Storage stays keyed by ID; HTTP clients get a list.

## Testing insight: the filter test that exposed a create bug

`test_list_orders_by_status_api_matching` failed with `assert 2 == 1` even though the query param `status=pending` was correct. Print debugging showed both orders were saved as `"pending"`, including the one the test created with `"status": "shipped"`.

The list/filter logic was fine. The real bug was in `add_order_api`: it never passed `status` into `order_tracker.add_order`, so the default `"pending"` always won. Fixing create (forwarding `status` from the JSON) made the filter test pass. That reinforced that a failing “later” test can point at an earlier layer—and that tests + prints beat guessing.

## Next steps

If I continued this project, I would:

1. **Persistent storage** — replace (or back) `InMemoryStorage` with something like SQLite so orders survive server restarts.
2. **A DELETE endpoint** — e.g. `DELETE /api/orders/<order_id>` with tracker support, API tests for success and not-found, and a simple UI control to remove an order.

.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```
