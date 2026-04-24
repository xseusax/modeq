from flask import Blueprint, request, jsonify
import datetime
import uuid

payment_bp = Blueprint("payment", __name__)

receipts = []

@payment_bp.route("/", methods=["POST"])
def pay():
    data = request.json

    receipt = {
        "transaction_id": str(uuid.uuid4()),
        "customer": data["customer"],
        "item": data["item"],
        "qty": data["qty"],
        "total": data["total"],
        "timestamp": str(datetime.datetime.now())
    }

    receipts.append(receipt)

    return jsonify({
        "status": "success",
        "receipt": receipt
    })

@payment_bp.route("/receipts", methods=["GET"])
def get_receipts():
    return jsonify(receipts)