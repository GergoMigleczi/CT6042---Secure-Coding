
"""
PURPOSE: Test payment confirmation security before and after mitigation.

SECURITY CONTEXT:
    The vulnerable Invoice System uses an exposed HMAC signing secret.
    The mitigated version loads a newly rotated secret from configuration.

    These tests demonstrate whether the original compromised key can still
    authenticate fraudulent payment notifications.

NOTE: Flask's test client sends simulated POST requests without running a server.
"""

import hashlib
import hmac

import invoice_system_vulnerable as vulnerable
import invoice_system_mitigated as mitigated


# ATTACK: Original signing secret obtained from the vulnerable source code.
COMPROMISED_SECRET = b"demo-payment-secret-123"


def create_payload(secret):
    """
    PURPOSE: Generate a signed payment confirmation for testing.

    INPUTS: HMAC signing secret.
    RETURNS: Payment notification containing the payment data and signature.
    """

    payment = {
        "reference": "INV-1001",
        "amount": 15000,
        "status": "PAID"
    }

    message = (
        f"{payment['reference']}|"
        f"{payment['amount']}|"
        f"{payment['status']}"
    )

    signature = hmac.new(
        secret,
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return {
        "payment": payment,
        "signature": signature
    }



def test_compromised_key_vulnerable():
    """
    PURPOSE: Demonstrate that the vulnerable system accepts a forged payment.

    TEST: A notification signed with the exposed key should be accepted,
    allowing an attacker to mark an unpaid invoice as paid.
    """

    # STEP: Reset the invoice before testing.
    vulnerable.INVOICES["INV-1001"]["status"] = "UNPAID"

    # ATTACK: Generate a fraudulent notification using the compromised secret.
    payload = create_payload(COMPROMISED_SECRET)

    response = vulnerable.app.test_client().post(
        "/payment-confirmation",
        json=payload
    )

    # TEST: Confirm that the forged payment is accepted.
    assert response.status_code == 200
    assert vulnerable.INVOICES["INV-1001"]["status"] == "PAID"


def test_compromised_key_mitigated():
    """
    PURPOSE: Verify that key rotation prevents the original attack.

    TEST: The mitigated system should reject notifications signed with
    the previously compromised secret.
    """

    # STEP: Reset the invoice before testing.
    mitigated.INVOICES["INV-1001"]["status"] = "UNPAID"

    # ATTACK: Repeat the original attack using the old compromised secret.
    payload = create_payload(COMPROMISED_SECRET)

    response = mitigated.app.test_client().post(
        "/payment-confirmation",
        json=payload
    )

    # TEST: Confirm that the old signing key is no longer trusted.
    assert response.status_code == 401
    assert mitigated.INVOICES["INV-1001"]["status"] == "UNPAID"


def test_legitimate_payment_after_mitigation():
    """
    PURPOSE: Verify that legitimate payments still work after mitigation.

    TEST: A notification signed with the new configured key should be accepted.
    """

    # STEP: Reset the invoice before testing.
    mitigated.INVOICES["INV-1001"]["status"] = "UNPAID"

    # NOTE: Simulates the legitimate provider using the current shared key.
    payload = create_payload(mitigated.PAYMENT_SECRET)

    response = mitigated.app.test_client().post(
        "/payment-confirmation",
        json=payload
    )

    # TEST: Confirm that the mitigated system still processes valid payments.
    assert response.status_code == 200
    assert mitigated.INVOICES["INV-1001"]["status"] == "PAID"


def test_invalid_invoice_reference():
    """
    PURPOSE: Verify that payments referencing nonexistent invoices are rejected.

    TEST: A valid HMAC signature must not allow a nonexistent invoice
    reference to be processed.
    """

    # STEP: Reset the existing invoice before testing.
    mitigated.INVOICES["INV-1001"]["status"] = "UNPAID"

    # TEST: Generate a valid signature for an invoice that does not exist.
    payload = create_payload(mitigated.PAYMENT_SECRET)
    payload["payment"]["reference"] = "INV-9999"

    # Recalculate the HMAC so the reference is covered by a valid signature.
    message = "INV-9999|15000|PAID"
    payload["signature"] = hmac.new(
        mitigated.PAYMENT_SECRET,
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    response = mitigated.app.test_client().post(
        "/payment-confirmation",
        json=payload
    )

    # TEST: Confirm that the unknown invoice is rejected.
    assert response.status_code == 404
    assert mitigated.INVOICES["INV-1001"]["status"] == "UNPAID"


def test_incorrect_payment_amount():
    """
    PURPOSE: Verify that the payment amount matches the outstanding invoice.

    TEST: A valid HMAC signature must not allow an incorrect payment
    amount to mark an invoice as paid.
    """

    # STEP: Reset the invoice before testing.
    mitigated.INVOICES["INV-1001"]["status"] = "UNPAID"

    # TEST: Generate a valid signature for an incorrect payment amount.
    payload = create_payload(mitigated.PAYMENT_SECRET)
    payload["payment"]["amount"] = 10000

    # Recalculate the HMAC to authenticate the modified payment information.
    message = "INV-1001|10000|PAID"
    payload["signature"] = hmac.new(
        mitigated.PAYMENT_SECRET,
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    response = mitigated.app.test_client().post(
        "/payment-confirmation",
        json=payload
    )

    # TEST: Confirm that the payment is rejected and the invoice remains unpaid.
    assert response.status_code == 400
    assert mitigated.INVOICES["INV-1001"]["status"] == "UNPAID"
