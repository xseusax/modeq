from flask import Flask, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
import uuid
import os

app = Flask(__name__)
CORS(app)

ORDERS_FILE = "orders.xml"
INVENTORY_FILE = "inventory.xml"


def load_xml(file):
    if not os.path.exists(file):
        root = ET.Element("Root")
        ET.ElementTree(root).write(file)
        return root
    return ET.parse(file).getroot()


def save_xml(file, root):
    ET.ElementTree(root).write(file)


@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.json

    product = data["product"]
    qty = int(data["quantity"])

    inventory = load_xml(INVENTORY_FILE)
    orders = load_xml(ORDERS_FILE)

    # find product
    for item in inventory.findall("Product"):
        if item.find("Name").text == product:
            stock = int(item.find("Stock").text)

            if stock < qty:
                return {"status": "failed", "message": "Not enough stock"}

            item.find("Stock").text = str(stock - qty)

    # create order
    order = ET.SubElement(orders, "Order")
    ET.SubElement(order, "OrderID").text = str(uuid.uuid4())
    ET.SubElement(order, "Product").text = product
    ET.SubElement(order, "Quantity").text = str(qty)
    ET.SubElement(order, "Status").text = "Pending"

    save_xml(INVENTORY_FILE, inventory)
    save_xml(ORDERS_FILE, orders)

    return {"status": "success", "message": "Order created"}


@app.route('/orders', methods=['GET'])
def get_orders():
    root = load_xml(ORDERS_FILE)
    return Response(ET.tostring(root, encoding="unicode"), mimetype="application/xml")


if __name__ == "__main__":
    app.run(port=5000, debug=True)