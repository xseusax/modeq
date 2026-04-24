<<<<<<< HEAD
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
=======
from flask import Flask, Response, request
from flask_cors import CORS
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

FILE = "inventory.xml"

def load():
    return ET.parse(FILE).getroot()

@app.route("/inventory", methods=["GET"])
def inventory():
    root = load()
    return Response(ET.tostring(root, encoding="unicode"), mimetype="application/xml")


@app.route("/update_inventory", methods=["POST"])
def update():
    root = load()
    req = ET.fromstring(request.data)

    code = req.find("ProductCode").text
    qty = int(req.find("Quantity").text)

    for item in root.findall("Item"):
        if item.find("Code").text == code:
            stock = int(item.find("Stock").text)

            if stock < qty:
                return Response("""
                <Response>
                    <Status>Failed</Status>
                    <Message>Not enough stock</Message>
                </Response>
                """, mimetype="application/xml")

            item.find("Stock").text = str(stock - qty)

            ET.ElementTree(root).write(FILE, encoding="unicode")

            return Response(f"""
            <Response>
                <Status>Success</Status>
                <Name>{item.find('Name').text}</Name>
                <Brand>{item.find('Brand').text}</Brand>
                <Price>{item.find('Price').text}</Price>
                <RemainingStock>{stock - qty}</RemainingStock>
            </Response>
            """, mimetype="application/xml")

    return Response("""
    <Response>
        <Status>Failed</Status>
        <Message>Item not found</Message>
    </Response>
    """, mimetype="application/xml")


if __name__ == "__main__":
>>>>>>> ce45a0404d7d8cdf0354ec5d498e1f2738d63b13
    app.run(port=5001, debug=True)