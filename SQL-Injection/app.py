
"""
PURPOSE:
Provides the web interface for the Order Processing System.

SECURITY CONTEXT:
Demonstrates an intentionally vulnerable order search endpoint.
The application is intended for local testing only.
"""

from flask import Flask, render_template, request
from database import search_orders, search_orders_safe

app = Flask(__name__)


@app.route("/")
def home():
    """PURPOSE: Displays the Order Processing System homepage."""
    return render_template("index.html")


@app.route("/orders/search")
def search():
    """
    PURPOSE: Searches for orders using a customer-supplied reference.
    INPUTS: The reference query parameter from the HTTP GET request.
    RETURNS: An HTML page displaying the matching orders.
    """

    reference = request.args.get("reference", "")

    orders = search_orders_safe(reference)

    return render_template(
        "search_results.html",
        reference=reference,
        orders=orders
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1")
