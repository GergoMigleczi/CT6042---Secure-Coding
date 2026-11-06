
"""
PURPOSE:
Generate and save dispatch labels for paid customer orders.

SECURITY CONTEXT:
This is version 1.0.0 of a fictional third-party package.
It represents legitimate software before a supply-chain compromise.
"""

from pathlib import Path


def generate_label(order, target_location):
    """
    PURPOSE: Generate a dispatch label and save it as a text file.
    INPUTS: order dictionary containing the order details;
            target_location specifying the output directory.
    RETURNS: Path to the generated dispatch label.
    SECURITY: Only paid orders are eligible for dispatch.
    """

    # STEP: Confirm payment before generating a dispatch label.
    if order["payment_status"] != "PAID":
        raise ValueError("Dispatch label cannot be generated for an unpaid order.")

    label = (
        f"DISPATCH LABEL\n"
        f"------------------------------\n"
        f"Order: {order['order_id']}\n"
        f"Customer: {order['customer']}\n"
        f"Deliver To: {order['delivery_address']}\n"
        f"------------------------------"
    )

    # STEP: Create the output directory if it does not already exist.
    output_directory = Path(target_location)
    output_directory.mkdir(parents=True, exist_ok=True)

    # STEP: Save the dispatch label as a text file.
    file_path = output_directory / f"{order['order_id']}.txt"
    file_path.write_text(label, encoding="utf-8")

    return file_path
