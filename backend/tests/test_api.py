import pytest
from backend.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

def test_add_order_api_success(client):
    order_data = {
        "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 201
    assert response.json['order_id'] == "API001"

def test_get_order_api_success(client):
    client.post('/api/orders', json={
        "order_id": "GET001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.get('/api/orders/GET001')
    assert response.status_code == 200
    assert response.json['order_id'] == "GET001"

def test_get_order_api_not_found(client):
    response = client.get('/api/orders/NONEXISTENT')
    assert response.status_code == 404

def test_update_order_status_api_success(client):
    client.post('/api/orders', json={
        "order_id": "UPDATE001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.put('/api/orders/UPDATE001/status', json={"new_status": "shipped"})
    assert response.status_code == 200
    assert response.json['status'] == "shipped"

def test_list_all_orders_api_with_data(client):
    client.post('/api/orders', json={"order_id": "LST001", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    client.post('/api/orders', json={"order_id": "LST002", "item_name": "Item B", "quantity": 2, "customer_id": "C2"})
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.json) == 2

def test_list_orders_by_status_api_matching(client):
    client.post('/api/orders', json={"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"})
    client.post('/api/orders', json={"order_id": "S002", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"})
    response = client.get('/api/orders?status=pending')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['order_id'] == "S001"

def test_delete_order_api_success(client):
    client.post('/api/orders', json={"order_id": "DEL001", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    response = client.delete('/api/orders/DEL001')
    assert response.status_code == 200
    assert response.json['message'] == "Order DEL001 deleted successfully"
    assert client.get('/api/orders/DEL001').status_code == 404

def test_delete_order_api_not_found(client):
    response = client.delete('/api/orders/NONEXISTENT')
    assert response.status_code == 404
    assert response.json['error'] == "Order with ID 'NONEXISTENT' does not exist."

def test_add_order_api_missing_json(client):
    response = client.post('/api/orders', data='not json', content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json

def test_add_order_api_missing_field(client):
    response = client.post('/api/orders', json={"order_id": "X"})  # missing item_name, etc.
    assert response.status_code == 400
    assert 'error' in response.json

def test_api_unknown_route(client):
    response = client.get('/api/does-not-exist')
    assert response.status_code == 404
    assert response.json['error'] == 'Resource not found'