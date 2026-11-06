"""PURPOSE: Receive payment confirmations for fictional invoices.

SECURITY CONTEXT: The Invoice System checks a provider's HMAC-SHA256 signature
before marking an invoice paid. This version intentionally exposes the key.
NOTE: Local teaching demonstration; no real payment provider is contacted.
"""

import hashlib
import hmac
import os
from dotenv import load_dotenv

from flask import Flask, jsonify, request


app = Flask(__name__)

# MITIGATION: Load configuration from the .env file.
load_dotenv()

# MITIGATION: Retrieve the signing secret without embedding it in source code.
PAYMENT_SECRET = os.environ["PAYMENT_SECRET"].encode("utf-8")

# NOTE: Amounts are in pence; the in-memory data resets on restart.
INVOICES = {"INV-1001": {"amount": 15000, "status": "UNPAID"},
            "INV-1002": {"amount": 20000, "status": "UNPAID"},
            "INV-1003": {"amount": 5000, "status": "UNPAID"},
            "INV-1004": {"amount": 7500, "status": "UNPAID"}}


def verify_payment(payment, received_signature):
    """PURPOSE: Check that the provider's signature matches the payment data.

    INPUTS: Payment reference, amount, status and received hexadecimal HMAC.
    RETURNS: True if the signature matches; otherwise False.
    """
    # SECURITY: Both parties must sign the same fields in the same order.
    message = f"{payment['reference']}|{payment['amount']}|{payment['status']}"
    expected_signature = hmac.new(
        PAYMENT_SECRET, message.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # SECURITY: Compare tags without an ordinary timing-sensitive comparison.
    return hmac.compare_digest(expected_signature, received_signature)


def process_payment(payment, signature):
    """PURPOSE: Authenticate a notification and update its invoice.

    RETURNS: A message and HTTP status code.
    """
    # SECURITY: Authentication takes place before any invoice is updated.
    if not verify_payment(payment, signature):
        return "Invalid payment signature", 401

    invoice = INVOICES.get(payment["reference"])
    if invoice is None:
        return "Invoice not found", 404

    # SECURITY: A valid signature alone does not prove this invoice is payable.
    if type(payment["amount"]) is not int or payment["amount"] != invoice["amount"]:
        return "Incorrect payment amount", 400
    if payment["status"] != "PAID":
        return "Payment not completed", 400

    invoice["status"] = "PAID"
    return "Invoice marked as PAID", 200


@app.post("/payment-confirmation")
def payment_confirmation():
    """PURPOSE: Accept a signed JSON payment notification over HTTP POST."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(message="Invalid JSON request"), 400

    payment = body.get("payment")
    signature = body.get("signature")

    # SECURITY: Reject incomplete or incorrectly typed incoming data.
    if (
        not isinstance(payment, dict)
        or not isinstance(signature, str)
        or not isinstance(payment.get("reference"), str)
        or type(payment.get("amount")) is not int
        or not isinstance(payment.get("status"), str)
    ):
        return jsonify(message="Invalid payment notification"), 400

    message, status = process_payment(payment, signature)
    print("Current invoices:", INVOICES)
    return jsonify(message=message), status


if __name__ == "__main__":
    # NOTE: Localhost only; debug mode is deliberately disabled.
    print("Initial invoices:", INVOICES)
    app.run(host="127.0.0.1", port=5000, debug=False)
