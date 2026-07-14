"""Core business logic for managing customer orders."""


class OrderTracker:
    """Manage customer orders: add, update, retrieve, list, and delete."""

    def __init__(self, storage):
        required_methods = [
            'save_order', 'get_order', 'get_all_orders', 'delete_order',
        ]
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(
                    f"Storage object must implement a callable '{method}' method."
                )
        self.storage = storage

    def add_order(
        self,
        order_id: str,
        item_name: str,
        quantity: int,
        customer_id: str,
        status: str = "pending",
    ):
        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order_data = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order_data)

    def get_order_by_id(self, order_id: str):
        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")
        return order

    def update_order_status(self, order_id: str, new_status: str):
        order = self.get_order_by_id(order_id)
        order["status"] = new_status
        self.storage.save_order(order_id, order)

    def list_all_orders(self):
        return self.storage.get_all_orders()

    def list_orders_by_status(self, status: str):
        return {
            k: v
            for k, v in self.storage.get_all_orders().items()
            if v["status"] == status
        }

    def delete_order(self, order_id: str):
        if not self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' does not exist.")
        self.storage.delete_order(order_id)
