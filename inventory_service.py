from flask import Flask, request, Response
import xml.etree.ElementTree as ET
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# simple sample inventory
inventory = {
    "C001": {"name": "Chocolate Cupcake", "brand": "SweetDelight", "price": 50, "stock": 20},
    "B001": {"name": "Cheeseburger", "brand": "BurgerLab", "price": 120, "stock": 15},
}

@app.route("/update_inventory", methods=["POST"])
def update():
    root = ET.fromstring(request.data)
    code = root.find("ProductCode").text
    qty = int(root.find("Quantity").text)

    res = ET.Element("InventoryResponse")

    if code in inventory and inventory[code]["stock"] >= qty:
        inventory[code]["stock"] -= qty

        ET.SubElement(res, "Status").text = "Success"
        ET.SubElement(res, "Name").text = inventory[code]["name"]
        ET.SubElement(res, "Brand").text = inventory[code]["brand"]
        ET.SubElement(res, "Price").text = str(inventory[code]["price"])
        ET.SubElement(res, "RemainingStock").text = str(inventory[code]["stock"])
    else:
        ET.SubElement(res, "Status").text = "Failed"
        ET.SubElement(res, "Message").text = "Out of stock or invalid"

    return Response(ET.tostring(res, encoding="unicode"),
                    mimetype="application/xml")


@app.route("/inventory")
def get_inventory():
    root = ET.Element("Inventory")
    for code, item in inventory.items():
        i = ET.SubElement(root, "Item")
        ET.SubElement(i, "Code").text = code
        ET.SubElement(i, "Name").text = item["name"]
        ET.SubElement(i, "Brand").text = item["brand"]
        ET.SubElement(i, "Price").text = str(item["price"])
        ET.SubElement(i, "Stock").text = str(item["stock"])

    return Response(ET.tostring(root, encoding="unicode"),
                    mimetype="application/xml")


if __name__ == "__main__":
    app.run(port=5001, debug=True)