from flask import Blueprint, jsonify

inventory_bp = Blueprint("inventory", __name__)

items = [
    {"code": "CCK", "name": "Chocolate Cupcake", "stock": 20, "price": 50},
    {"code": "BBG", "name": "Beef Burger", "stock": 15, "price": 120},
]

@inventory_bp.route("/", methods=["GET"])
def get_inventory():
    return jsonify(items)