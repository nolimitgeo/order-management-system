import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#
def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    
    mock_storage.get_order.assert_called_once_with("ORD001")
    mock_storage.save_order.assert_called_once_with(
        "ORD001", 
        {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"}
    )

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")    

    mock_storage.save_order.assert_not_called()

def test_get_order_by_id_returns_correct_order(order_tracker, mock_storage):
    """Tests that get_order_by_id returns the correct order."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"}

    order = order_tracker.get_order_by_id("ORD001")
    mock_storage.get_order.assert_called_once_with("ORD001")
    assert order == {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"}

def test_get_order_by_id_raises_error_if_not_found(order_tracker, mock_storage):
    """Tests that get_order_by_id raises a ValueError if the order is not found."""
    # Simulate that the storage finds no existing order
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError, match="Order with ID 'ORD001' does not exist."):
        order_tracker.get_order_by_id("ORD001")

def test_update_order_status_successfully(order_tracker, mock_storage):
    """Tests that update_order_status updates the status of an existing order."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"}

    order_tracker.update_order_status("ORD001", "shipped")
    mock_storage.save_order.assert_called_once_with(
        "ORD001", 
        {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "shipped"}
    )

def test_update_order_status_raises_error_if_not_found(order_tracker, mock_storage):
    """Tests that update_order_status raises a ValueError if the order is not found."""
    # Simulate that the storage finds no existing order
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError, match="Order with ID 'ORD001' does not exist."):
        order_tracker.update_order_status("ORD001", "shipped")

    mock_storage.save_order.assert_not_called()

def test_list_all_orders_returns_correct_orders(order_tracker, mock_storage):
    """Tests that list_all_orders returns the correct orders."""
    # Simulate that the storage finds existing orders
    mock_storage.get_all_orders.return_value = {
        "ORD001": {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"}, 
        "ORD002": {"order_id": "ORD002", "item_name": "Mouse", "quantity": 2, "customer_id": "CUST002", "status": "shipped"},
        "ORD003": {"order_id": "ORD003", "item_name": "Keyboard", "quantity": 3, "customer_id": "CUST003", "status": "delivered"}
        }

    orders = order_tracker.list_all_orders()
    assert orders == {
        "ORD001": {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"}, 
        "ORD002": {"order_id": "ORD002", "item_name": "Mouse", "quantity": 2, "customer_id": "CUST002", "status": "shipped"},
        "ORD003": {"order_id": "ORD003", "item_name": "Keyboard", "quantity": 3, "customer_id": "CUST003", "status": "delivered"}
        }

def test_list_orders_by_status_returns_correct_orders(order_tracker, mock_storage):
    """Tests that list_orders_by_status returns the correct orders."""
    # Simulate that the storage finds existing orders
    mock_storage.get_all_orders.return_value = {
        "ORD001": {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"}, 
        "ORD002": {"order_id": "ORD002", "item_name": "Mouse", "quantity": 2, "customer_id": "CUST002", "status": "shipped"},
        "ORD003": {"order_id": "ORD003", "item_name": "Keyboard", "quantity": 3, "customer_id": "CUST003", "status": "delivered"}
        }

    orders = order_tracker.list_orders_by_status("shipped")
    assert orders == {
        "ORD002": {"order_id": "ORD002", "item_name": "Mouse", "quantity": 2, "customer_id": "CUST002", "status": "shipped"}
        }

def test_list_orders_by_status_raises_empty_if_not_found(order_tracker, mock_storage):
    """Tests that list_orders_by_status returns an empty dictionary if the orders are not found."""
    # Simulate that the storage finds no existing orders
    mock_storage.get_all_orders.return_value = {}
    assert order_tracker.list_orders_by_status("shipped") == {}