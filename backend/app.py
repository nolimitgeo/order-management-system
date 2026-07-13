from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    order_data = request.json
    try:
        order_tracker.add_order(order_data['order_id'], order_data['item_name'], order_data['quantity'], order_data['customer_id'], order_data.get('status','pending'))
        return jsonify({'order_id': order_data['order_id']}), 201 # 201 Created
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 # 400 Bad Request

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    try:
        order = order_tracker.get_order_by_id(order_id)
        return jsonify(order), 200 # 200 OK
    except ValueError as e:
        return jsonify({'error': str(e)}), 404 # 404 Not Found

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    new_status = request.json['new_status']
    try:
        order_tracker.update_order_status(order_id,new_status)
        return jsonify({'status': new_status}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get('status')
    #if status to filter by
    if status:
        orders = order_tracker.list_orders_by_status(status)
        return jsonify(list(orders.values())), 200 # 200 OK
    else:
        orders = order_tracker.list_all_orders()
        return jsonify(list(orders.values())), 200 # 200 OK

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8080)
