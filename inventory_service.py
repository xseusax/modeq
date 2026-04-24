from flask import Flask, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)
CORS(app)

INVENTORY_FILE = "inventory.xml"


def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        root = ET.Element("Inventory")
        tree = ET.ElementTree(root)
        tree.write(INVENTORY_FILE)
        return root

    tree = ET.parse(INVENTORY_FILE)
    return tree.getroot()


def save_inventory(root):
    tree = ET.ElementTree(root)
    tree.write(INVENTORY_FILE)


@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.json

    root = load_inventory()

    product = ET.SubElement(root, "Product")
    ET.SubElement(product, "ID").text = data["id"]
    ET.SubElement(product, "Name").text = data["name"]
    ET.SubElement(product, "Price").text = str(data["price"])
    ET.SubElement(product, "Stock").text = str(data["stock"])

    save_inventory(root)

    return {"status": "success", "message": "Product added"}


@app.route('/inventory', methods=['GET'])
def get_inventory():
    root = load_inventory()
    return Response(ET.tostring(root, encoding="unicode"), mimetype="application/xml")


if __name__ == "__main__":
    app.run(port=5001, debug=True)