
"""
PURPOSE:
Verify that the installed dispatch-label package preserves order data.

SECURITY CONTEXT:
These tests detect unauthorised modifications to dispatch labels
introduced by a compromised third-party dependency.
"""

import tempfile
import unittest
from pathlib import Path

from dispatch_labels import generate_label


class DispatchSecurityTests(unittest.TestCase):
    """
    PURPOSE: Verify the security-relevant behaviour of the installed
    dispatch-label package.
    """

    def test_dispatch_label_integrity(self):
        """
        PURPOSE: Verify that all dispatch label fields match the original order.
        TEST: Detect unauthorised changes to the order ID, customer or address.
        """

        order = {
            "order_id": "ORD-1001",
            "customer": "Alice Smith",
            "delivery_address": "123 Example Street, Bristol",
            "payment_status": "PAID"
        }

        # STEP: Generate a label in an isolated temporary directory.
        with tempfile.TemporaryDirectory() as output_directory:
            file_path = generate_label(order, output_directory)
            label = Path(file_path).read_text(encoding="utf-8")

            # TEST: Each label field must match the original order data.
            expected_fields = {
                "Order": order["order_id"],
                "Customer": order["customer"],
                "Deliver To": order["delivery_address"]
            }

            for field, expected_value in expected_fields.items():
                with self.subTest(field=field):
                    self.assertIn(
                        f"{field}: {expected_value}\n",
                        label + "\n",
                        f"SECURITY FAILURE: {field} does not match the order."
                    )

    def test_unpaid_order_rejected(self):
        """
        PURPOSE: Confirm unpaid orders cannot generate dispatch labels.
        TEST: Verify payment validation remains enforced.
        """

        order = {
            "order_id": "ORD-1002",
            "customer": "Bob Jones",
            "delivery_address": "456 Example Road, Bath",
            "payment_status": "PENDING"
        }

        with tempfile.TemporaryDirectory() as output_directory:
            # TEST: Unpaid orders must be rejected.
            with self.assertRaises(ValueError):
                generate_label(order, output_directory)

            # TEST: Rejected orders must not produce a dispatch label.
            self.assertFalse(
                (Path(output_directory) / "ORD-1002.txt").exists()
            )


if __name__ == "__main__":
    unittest.main()
