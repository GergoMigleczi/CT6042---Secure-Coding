
"""
PURPOSE:
Automates vulnerability, mitigation and regression testing
for the fictional Dispatch System.

SECURITY CONTEXT:
Compares the vulnerable and mitigated C implementations
using isolated test data and a shared label generator.
"""

import subprocess
from pathlib import Path

import pytest


SOURCE_DIR = Path(__file__).resolve().parent

# ATTACK: Fill the 32-byte name buffer and overwrite the
# adjacent dispatch status with Y and a null terminator.
MALICIOUS_NAME = "A" * 32 + "Y"


@pytest.fixture(scope="session")
def executables(tmp_path_factory):
    """
    PURPOSE: Compiles the three C programs once per test session.
    RETURNS: Paths to the compiled executables.
    """
    build_dir = tmp_path_factory.mktemp("build")

    sources = {
        "vulnerable": "receive_order.c",
        "safe": "receive_order_safe.c",
        "labels": "generate_label.c",
    }

    compiled = {}

    for name, source in sources.items():
        executable = build_dir / name

        subprocess.run(
            [
                "clang",
                "-std=c11",
                "-O0",
                "-g",
                "-Wall",
                "-Wextra",
                str(SOURCE_DIR / source),
                "-o",
                str(executable),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        compiled[name] = executable

    return compiled


def run_program(executable, directory, *arguments):
    """
    PURPOSE: Executes a C program with the supplied arguments.
    RETURNS: Completed process containing output and exit status.
    """
    return subprocess.run(
        [str(executable), *arguments],
        cwd=directory,
        capture_output=True,
        text=True,
        timeout=10,
    )


def read_orders(directory):
    """
    PURPOSE: Reads the simulated dispatch database.
    RETURNS: CSV records, or an empty list if no database exists.
    """
    database = directory / "orders.csv"

    if not database.exists():
        return []

    return database.read_text().splitlines()


def assert_success(result):
    """
    PURPOSE: Verifies that a C program completed successfully.
    INPUTS: Completed subprocess result.
    """
    assert result.returncode == 0, (
        f"Exit code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


# ============================================================
# A. VULNERABILITY DEMONSTRATION
# ============================================================

def test_vulnerable_overflow_corrupts_dispatch_status(
    executables, tmp_path
):
    """
    TEST: Confirm that an oversized customer name changes
    the dispatch status to Y without payment.
    """
    result = run_program(
        executables["vulnerable"],
        tmp_path,
        "1001",
        MALICIOUS_NAME,
    )

    assert result.returncode == 0
    assert "Ready to ship: Y" in result.stdout
    assert read_orders(tmp_path)[0].endswith(",Y")


def test_vulnerable_overflow_generates_unauthorised_label(
    executables, tmp_path
):
    """
    TEST: Confirm that a corrupted dispatch status causes
    the label generator to release an unpaid order.
    """
    run_program(
        executables["vulnerable"],
        tmp_path,
        "1002",
        MALICIOUS_NAME,
    )

    result = run_program(
        executables["labels"],
        tmp_path,
    )

    # ATTACK: The order has not been paid, but a label exists.
    assert result.returncode == 0
    assert (tmp_path / "label_1002.txt").exists()


# ============================================================
# B. MITIGATION VERIFICATION
# ============================================================


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



# ============================================================
# C. REGRESSION TESTING
# ============================================================

@pytest.mark.parametrize("receiver", ["vulnerable", "safe"])
def test_normal_order_is_saved_on_hold(
    executables, tmp_path, receiver
):
    """
    TEST: Confirm that both implementations accept a legitimate
    order and initially mark it as not ready for shipment.
    """
    result = run_program(
        executables[receiver],
        tmp_path,
        "3001",
        "John Smith",
    )

    assert_success(result)
    assert read_orders(tmp_path) == ["3001,John Smith,N"]


@pytest.mark.parametrize("receiver", ["vulnerable", "safe"])
def test_unpaid_order_does_not_generate_label(
    executables, tmp_path, receiver
):
    """
    TEST: Confirm that legitimate unpaid orders do not generate
    dispatch labels in either implementation.
    """
    receive_result = run_program(
        executables[receiver],
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


@pytest.mark.parametrize("receiver", ["vulnerable", "safe"])
def test_paid_order_generates_label(
    executables, tmp_path, receiver
):
    """
    TEST: Confirm that both implementations support legitimate
    payment confirmation and subsequent label generation.
    """
    receive_result = run_program(
        executables[receiver],
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


@pytest.mark.parametrize("receiver", ["vulnerable", "safe"])
def test_duplicate_label_is_not_generated(
    executables, tmp_path, receiver
):
    """
    TEST: Confirm that repeated label-generation runs do not
    overwrite an existing label in either implementation.
    """
    receive_result = run_program(
        executables[receiver],
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
