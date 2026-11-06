
"""
PURPOSE:
Verifies the buffer overflow mitigation and regression behaviour.

SECURITY CONTEXT:
Confirms that oversized inputs are rejected without corrupting
dispatch records or preventing legitimate label generation.
"""

from conftest import (
    MALICIOUS_NAME,
    run_program,
    read_orders,
    assert_success,
)


def test_safe_version_rejects_malicious_name(
    executables, tmp_path
):
    """
    TEST: Confirm that the mitigated receiver rejects the
    malicious customer name without saving an order.
    """
    result = run_program(
        executables["safe"],
        tmp_path,
        "2001",
        MALICIOUS_NAME,
    )

    assert result.returncode != 0
    assert read_orders(tmp_path) == []


def test_safe_version_prevents_unauthorised_label(
    executables, tmp_path
):
    """
    TEST: Confirm that a rejected malicious order cannot
    produce a dispatch label, even when the generator runs.
    """
    receive_result = run_program(
        executables["safe"],
        tmp_path,
        "2002",
        MALICIOUS_NAME,
    )

    assert receive_result.returncode != 0
    assert read_orders(tmp_path) == []

    # STEP: Create an empty database so the generator can
    # execute normally without the rejected order.
    database = tmp_path / "orders.csv"
    database.write_text("")

    label_result = run_program(
        executables["labels"],
        tmp_path,
    )

    assert_success(label_result)
    assert not (tmp_path / "label_2002.txt").exists()


def test_safe_version_rejects_oversized_order_id(
    executables, tmp_path
):
    """
    TEST: Confirm that the mitigation also protects the
    fixed-size order ID buffer.
    """
    oversized_id = "1" * 16

    result = run_program(
        executables["safe"],
        tmp_path,
        oversized_id,
        "John Smith",
    )

    assert result.returncode != 0
    assert read_orders(tmp_path) == []


def test_safe_normal_order_is_saved_on_hold(
    executables, tmp_path
):
    """
    TEST: Confirm that a legitimate order is initially
    marked as not ready for shipment.
    """
    result = run_program(
        executables["safe"],
        tmp_path,
        "3001",
        "John Smith",
    )

    assert_success(result)
    assert read_orders(tmp_path) == ["3001,John Smith,N"]

def test_safe_trims_whitespace(
    executables, tmp_path
):
    """
    TEST: Confirm that trimming removes leading and trailing
    whitespace without changing spaces within customer names.
    """
    result = run_program(
        executables["safe"],
        tmp_path,
        "  3005  ",
        "  John Smith  ",
    )

    assert_success(result)
    assert read_orders(tmp_path) == ["3005,John Smith,N"]

def test_safe_unpaid_order_does_not_generate_label(
    executables, tmp_path
):
    """
    TEST: Confirm that a legitimate unpaid order does not
    generate a dispatch label.
    """
    receive_result = run_program(
        executables["safe"],
        tmp_path,
        "3002",
        "Jane Smith",
    )

    assert_success(receive_result)

    label_result = run_program(
        executables["labels"],
        tmp_path,
    )

    assert_success(label_result)
    assert not (tmp_path / "label_3002.txt").exists()


def test_safe_paid_order_generates_label(
    executables, tmp_path
):
    """
    TEST: Confirm that legitimate payment confirmation still
    allows dispatch label generation after mitigation.
    """
    receive_result = run_program(
        executables["safe"],
        tmp_path,
        "3003",
        "Jane Smith",
    )

    assert_success(receive_result)
    assert read_orders(tmp_path) == ["3003,Jane Smith,N"]

    # STEP: Simulate the Invoice System confirming payment.
    database = tmp_path / "orders.csv"
    database.write_text("3003,Jane Smith,Y\n")

    label_result = run_program(
        executables["labels"],
        tmp_path,
    )

    assert_success(label_result)

    label = tmp_path / "label_3003.txt"
    assert label.exists()
    assert "Jane Smith" in label.read_text()


def test_safe_duplicate_label_is_not_generated(
    executables, tmp_path
):
    """
    TEST: Confirm that repeated label-generation runs do not
    overwrite an existing label after mitigation.
    """
    receive_result = run_program(
        executables["safe"],
        tmp_path,
        "3004",
        "John Smith",
    )

    assert_success(receive_result)

    # STEP: Simulate payment confirmation.
    database = tmp_path / "orders.csv"
    database.write_text("3004,John Smith,Y\n")

    first_result = run_program(
        executables["labels"],
        tmp_path,
    )

    assert_success(first_result)

    label = tmp_path / "label_3004.txt"
    assert label.exists()

    original_content = label.read_text()

    second_result = run_program(
        executables["labels"],
        tmp_path,
    )

    assert_success(second_result)

    assert "Labels created: 0" in second_result.stdout
    assert label.read_text() == original_content
