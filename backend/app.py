"""Flask API and static file server for the Order Tracker application."""

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.exceptions import BadRequest

from backend.in_memory_storage import InMemoryStorage
from backend.order_tracker import OrderTracker

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


def get_json_data(required_fields=None):
    """Parse and validate a JSON request body."""
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Request must be JSON")
    if required_fields:
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")
    return data


def error_response(error_message, status_code):
    """Return a consistent JSON error response."""
    return jsonify({'error': error_message}), status_code


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return error_response(e.description, 400)


@app.errorhandler(ValueError)
def handle_value_error(e):
    message = str(e)
    if 'already exists' in message:
        return error_response(message, 400)
    if 'does not exist' in message:
        return error_response(message, 404)
    return error_response(message, 400)


@app.errorhandler(404)
def handle_not_found(e):
    if request.path.startswith('/api/'):
        return error_response('Resource not found', 404)
    return e


@app.errorhandler(405)
def handle_method_not_allowed(e):
    if request.path.startswith('/api/'):
        return error_response('Method not allowed', 405)
    return e


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/api/orders', methods=['POST'])
def add_order_api():
    order_data = get_json_data(['order_id', 'item_name', 'quantity', 'customer_id'])
    order_tracker.add_order(
        order_data['order_id'],
        order_data['item_name'],
        order_data['quantity'],
        order_data['customer_id'],
        order_data.get('status', 'pending'),
    )
    return jsonify({'order_id': order_data['order_id']}), 201


@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    return jsonify(order), 200


@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    body = get_json_data(['new_status'])
    new_status = body['new_status']
    order_tracker.update_order_status(order_id, new_status)
    return jsonify({'status': new_status}), 200


@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get('status')
    if status:
        orders = order_tracker.list_orders_by_status(status)
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(list(orders.values())), 200


@app.route('/api/orders/<string:order_id>', methods=['DELETE'])
def delete_order_api(order_id):
    order_tracker.delete_order(order_id)
    return jsonify({'message': f"Order {order_id} deleted successfully"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8080)
