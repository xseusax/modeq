from flask import Flask, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

@app.route("/process_payment", methods=["POST"])
def pay():
    root = ET.fromstring(request.data)

    amount = float(root.find("Amount").text)
    product = root.find("ProductName").text
    qty = int(root.find("Quantity").text)

    res = ET.Element("PaymentResponse")

    if amount > 0 and qty > 0:
        ET.SubElement(res, "Status").text = "Success"
        ET.SubElement(res, "TransactionID").text = f"TXN-{abs(hash(product+str(amount))) % 999999}"
        ET.SubElement(res, "Amount").text = str(amount)
    else:
        ET.SubElement(res, "Status").text = "Failed"
        ET.SubElement(res, "Message").text = "Invalid payment"

    return Response(ET.tostring(res, encoding="unicode"),
                    mimetype="application/xml")


if __name__ == "__main__":
    app.run(port=5002, debug=True)