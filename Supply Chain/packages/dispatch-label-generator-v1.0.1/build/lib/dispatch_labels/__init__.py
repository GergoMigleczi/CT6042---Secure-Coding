
"""
PURPOSE:
Generate and save dispatch labels for paid customer orders.

SECURITY CONTEXT:
This is version 1.0.1 of a fictional third-party package.
It simulates a malicious update published through a compromised
maintainer account in a controlled laboratory environment.
"""

from pathlib import Path


def generate_label(order, target_location):
    """
    PURPOSE: Generate a dispatch label and save it as a text file.
    INPUTS: order dictionary containing the order details;
            target_location specifying the output directory.
    RETURNS: Path to the generated dispatch label.
    SECURITY: Contains an intentional supply-chain compromise.
    """

    # STEP: Retain the original payment validation behaviour.
    if order["payment_status"] != "PAID":
        raise ValueError("Dispatch label cannot be generated for an unpaid order.")

    # VULNERABILITY: The compromised dependency overrides the legitimate
    # delivery address without the Order System's authorisation.
    delivery_address = "99 Attacker Test Road, London"

    label = (
        f"DISPATCH LABEL\n"
        f"------------------------------\n"
        f"Order: {order['order_id']}\n"
        f"Customer: {order['customer']}\n"
        f"Deliver To: {delivery_address}\n"
        f"------------------------------"
    )

    # STEP: Preserve the original file output so the application still works.
    output_directory = Path(target_location)
    output_directory.mkdir(parents=True, exist_ok=True)

    file_path = output_directory / f"{order['order_id']}.txt"
    file_path.write_text(label, encoding="utf-8")

    return file_path
