"""In-memory storage for orders. Data is lost when the application restarts."""


class InMemoryStorage:
    """Store orders in a Python dictionary."""

    def __init__(self):
        self._orders = {}

    def save_order(self, order_id: str, order_data: dict):
        self._orders[order_id] = order_data.copy()

    def get_order(self, order_id: str):
        order = self._orders.get(order_id)
        return order.copy() if order else None

    def get_all_orders(self):
        return {k: v.copy() for k, v in self._orders.items()}

    def clear(self):
        self._orders = {}

    def delete_order(self, order_id: str):
        self._orders.pop(order_id, None)
