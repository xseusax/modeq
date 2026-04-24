from flask import Flask, request, Response, render_template
from flask_cors import CORS
import xml.etree.ElementTree as ET
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

INVENTORY_URL = "https://YOUR-INVENTORY-SERVICE.onrender.com/update_inventory"
PAYMENT_URL = "https://YOUR-PAYMENT-SERVICE.onrender.com/process_payment"

ORDERS_FILE = "orders.xml"
RECEIPTS_FILE = "receipts.xml"

# ---------- XML helpers ----------
def load_xml(file_name, root_tag):
    if os.path.exists(file_name):
        try:
            return ET.parse(file_name).getroot()
        except:
            pass
    return ET.Element(root_tag)

def save_xml(root, file_name):
    ET.indent(root)
    ET.ElementTree(root).write(file_name, encoding="unicode", xml_declaration=True)

# ---------- routes ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/place_order", methods=["POST"])
def place_order():
    xml_data = request.data
    root = ET.fromstring(xml_data)

    product_code = root.find("ProductCode").text
    quantity = int(root.find("Quantity").text)
    customer_name = root.find("CustomerName").text or "Guest"

    # STEP 1: inventory
    inv_resp = requests.post(INVENTORY_URL, data=xml_data,
                             headers={"Content-Type": "application/xml"})
    inv_root = ET.fromstring(inv_resp.content)

    if inv_root.find("Status").text != "Success":
        return Response(inv_resp.content, mimetype="application/xml")

    product_name = inv_root.find("Name").text
    brand = inv_root.find("Brand").text
    price = float(inv_root.find("Price").text)
    stock_left = inv_root.find("RemainingStock").text

    total = price * quantity

    # STEP 2: payment
    pay_xml = ET.Element("Payment")
    ET.SubElement(pay_xml, "Amount").text = str(total)
    ET.SubElement(pay_xml, "ProductName").text = product_name
    ET.SubElement(pay_xml, "Quantity").text = str(quantity)

    pay_resp = requests.post(PAYMENT_URL,
                             data=ET.tostring(pay_xml),
                             headers={"Content-Type": "application/xml"})
    pay_root = ET.fromstring(pay_resp.content)

    if pay_root.find("Status").text != "Success":
        return Response(pay_resp.content, mimetype="application/xml")

    txn = pay_root.find("TransactionID").text
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # STEP 3: save ORDER
    orders_root = load_xml(ORDERS_FILE, "Orders")

    order = ET.SubElement(orders_root, "Order")
    ET.SubElement(order, "TransactionID").text = txn
    ET.SubElement(order, "CustomerName").text = customer_name
    ET.SubElement(order, "ProductName").text = product_name
    ET.SubElement(order, "Quantity").text = str(quantity)
    ET.SubElement(order, "TotalAmount").text = str(total)
    ET.SubElement(order, "Timestamp").text = time

    save_xml(orders_root, ORDERS_FILE)

    # STEP 4: SAVE RECEIPT (NEW FEATURE YOU REQUESTED)
    receipts_root = load_xml(RECEIPTS_FILE, "Receipts")

    receipt = ET.SubElement(receipts_root, "Receipt")
    ET.SubElement(receipt, "TransactionID").text = txn
    ET.SubElement(receipt, "CustomerName").text = customer_name
    ET.SubElement(receipt, "ProductName").text = product_name
    ET.SubElement(receipt, "Brand").text = brand
    ET.SubElement(receipt, "Quantity").text = str(quantity)
    ET.SubElement(receipt, "Price").text = str(price)
    ET.SubElement(receipt, "Total").text = str(total)
    ET.SubElement(receipt, "Timestamp").text = time

    save_xml(receipts_root, RECEIPTS_FILE)

    # RESPONSE
    res = ET.Element("OrderResponse")
    ET.SubElement(res, "Status").text = "Success"
    ET.SubElement(res, "TransactionID").text = txn
    ET.SubElement(res, "RemainingStock").text = stock_left
    ET.SubElement(res, "Message").text = "Order placed + receipt saved"

    return Response(ET.tostring(res, encoding="unicode"),
                    mimetype="application/xml")


@app.route("/order_history")
def history():
    root = load_xml(ORDERS_FILE, "Orders")
    return Response(ET.tostring(root, encoding="unicode"),
                    mimetype="application/xml")


@app.route("/receipts")
def receipts():
    root = load_xml(RECEIPTS_FILE, "Receipts")
    return Response(ET.tostring(root, encoding="unicode"),
                    mimetype="application/xml")


if __name__ == "__main__":
    app.run(port=5000, debug=True)