import os
from flask import Flask, render_template, redirect, request, session, url_for
import stripe
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRODUCTS = {
    "1": {"name": "Producto A", "price": 1000},
    "2": {"name": "Producto B", "price": 2000},
    "3": {"name": "Producto C", "price": 3000}
}

@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)

@app.route("/add/<id>")
def add_to_cart(id):
    cart = session.get("cart", {})
    cart[id] = cart.get(id, 0) + 1
    session["cart"] = cart
    return redirect(url_for("index"))

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    items = []
    total = 0
    for id, qty in cart.items():
        product = PRODUCTS[id]
        subtotal = product["price"] * qty
        items.append({"id": id, "name": product["name"], "qty": qty, "subtotal": subtotal})
        total += subtotal
    return render_template("cart.html", items=items, total=total)

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    cart = session.get("cart", {})
    line_items = []
    for id, qty in cart.items():
        product = PRODUCTS[id]
        line_items.append({
            "price_data": {
                "currency": "eur",
                "product_data": {"name": product["name"]},
                "unit_amount": product["price"]
            },
            "quantity": qty
        })
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=url_for("success", _external=True),
        cancel_url=url_for("cart", _external=True)
    )
    return redirect(checkout_session.url, code=303)

@app.route("/success")
def success():
    session.pop("cart", None)
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
