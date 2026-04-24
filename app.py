from flask import Flask
from flask_cors import CORS

from routes.inventory import inventory_bp
from routes.orders import orders_bp
from routes.payment import payment_bp

app = Flask(__name__)
CORS(app)

# Register routes
app.register_blueprint(inventory_bp, url_prefix="/inventory")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(payment_bp, url_prefix="/payment")

@app.route("/")
def home():
    return {"message": "ModeQ API is running 🚀"}

if __name__ == "__main__":
    app.run(debug=True)