from flask import Blueprint, request, jsonify

orders_bp = Blueprint("orders", __name__)

orders = []

@orders_bp.route("/", methods=["POST"])
def create_order():
    data = request.json

    order = {
        "customer": data["customer"],
        "item": data["item"],
        "qty": data["qty"],
        "total": data["qty"] * data["price"]
    }

    orders.append(order)
    return jsonify({"status": "success", "order": order})

@orders_bp.route("/", methods=["GET"])
def get_orders():
    return jsonify(orders)