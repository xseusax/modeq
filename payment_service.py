from flask import Flask, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
import uuid
import os

app = Flask(__name__)
CORS(app)

RECEIPTS_FILE = "receipts.xml"


def load_receipts():
    if not os.path.exists(RECEIPTS_FILE):
        root = ET.Element("Receipts")
        ET.ElementTree(root).write(RECEIPTS_FILE)
        return root
    return ET.parse(RECEIPTS_FILE).getroot()


def save_receipts(root):
    ET.ElementTree(root).write(RECEIPTS_FILE)


@app.route('/process_payment', methods=['POST'])
def pay():
    root = ET.fromstring(request.data)

    amount = float(root.find('Amount').text)
    product = root.find('ProductName').text
    qty = int(root.find('Quantity').text)

    receipts = load_receipts()

    receipt = ET.SubElement(receipts, "Receipt")
    ET.SubElement(receipt, "TransactionID").text = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    ET.SubElement(receipt, "ProductName").text = product
    ET.SubElement(receipt, "Quantity").text = str(qty)
    ET.SubElement(receipt, "Amount").text = str(amount)
    ET.SubElement(receipt, "Status").text = "Success" if amount > 0 else "Failed"

    save_receipts(receipts)

    return Response(ET.tostring(receipt, encoding="unicode"), mimetype="application/xml")


@app.route('/receipts', methods=['GET'])
def get_receipts():
    root = load_receipts()
    return Response(ET.tostring(root, encoding="unicode"), mimetype="application/xml")


if __name__ == "__main__":
    app.run(port=5002, debug=True)