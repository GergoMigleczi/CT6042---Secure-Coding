
"""
PURPOSE:
Generate and save a dispatch label for a paid customer order.

SECURITY CONTEXT:
The Order System uses an independently installed third-party
package to generate dispatch labels.
"""

from pathlib import Path
from dispatch_labels import generate_label


def main():
    """
    PURPOSE: Generate a dispatch label for a sample paid order.
    SECURITY: Uses fictional order data for this controlled experiment.
    """

    order = {
        "order_id": "ORD-1001",
        "customer": "Alice Smith",
        "delivery_address": "123 Example Street, Bristol",
        "payment_status": "PAID"
    }

    # STEP: Store generated labels in the Order System's output directory.
    target_location = Path(__file__).resolve().parent / "dispatch_labels"

    file_path = generate_label(order, target_location)

    print(f"Dispatch label saved to: {file_path}")


if __name__ == "__main__":
    main()
