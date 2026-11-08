
"""
PURPOSE:
Fuzzes vulnerable and mitigated order-processing programs.

SECURITY CONTEXT:
Uses identical random inputs and AddressSanitizer to compare
memory-safety failures before and after mitigation.
"""

import random
import string
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VULNERABLE = ROOT / "receive_order_fuzz"
SAFE = ROOT / "receive_order_safe_fuzz"

CHARACTERS = string.ascii_letters + string.digits + " ,\t"
ITERATIONS = 1000


def run_program(program, order_id, customer_name, workdir):
    """PURPOSE: Executes a program with isolated file output."""
    return subprocess.run(
        [str(program), order_id, customer_name],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=workdir,
    )


def is_memory_error(result):
    """PURPOSE: Identifies AddressSanitizer memory-access errors."""
    return (
        "ERROR: AddressSanitizer:" in result.stderr
        and (
            "buffer-overflow" in result.stderr
            or "use-after-free" in result.stderr
            or "SEGV" in result.stderr
        )
    )


def test_fuzzing():
    rng = random.Random(42)

    results = {
        "vulnerable_memory_errors": 0,
        "safe_memory_errors": 0,
        "safe_accepted": 0,
        "safe_rejected": 0,
    }

    first_failure = None

    # STEP: Isolate generated CSV files from the project.
    with tempfile.TemporaryDirectory() as temp_dir:

        for i in range(ITERATIONS):
            order_id = "".join(
                rng.choices(
                    CHARACTERS,
                    k=rng.randint(1, 100)
                )
            )

            customer_name = "".join(
                rng.choices(
                    CHARACTERS,
                    k=rng.randint(1, 150)
                )
            )

            vulnerable = run_program(
                VULNERABLE, order_id, customer_name, temp_dir
            )

            safe = run_program(
                SAFE, order_id, customer_name, temp_dir
            )

            # TEST: Record confirmed sanitizer findings.
            if is_memory_error(vulnerable):
                results["vulnerable_memory_errors"] += 1

                if first_failure is None:
                    first_failure = {
                        "iteration": i + 1,
                        "order_id": order_id,
                        "customer_name": customer_name,
                        "asan_report": vulnerable.stderr,
                    }

            if is_memory_error(safe):
                results["safe_memory_errors"] += 1

            if safe.returncode == 0:
                results["safe_accepted"] += 1
            else:
                results["safe_rejected"] += 1

            if (i + 1) % 100 == 0:
                print(
                    f"Completed {i + 1}/{ITERATIONS} iterations",
                    flush=True
                )

        # TEST: Replay the first failing input against both versions.
        if first_failure is not None:
            order_id = first_failure["order_id"]
            customer_name = first_failure["customer_name"]

            vulnerable_replay = run_program(
                VULNERABLE, order_id, customer_name, temp_dir
            )
            safe_replay = run_program(
                SAFE, order_id, customer_name, temp_dir
            )

            print("\nFIRST DETECTED FAILURE")
            print("------------------------------")
            print("Iteration:", first_failure["iteration"])
            print("Order ID:", repr(order_id))
            print("Customer:", repr(customer_name))
            print("Vulnerable replay exit:", vulnerable_replay.returncode)
            print("Safe replay exit:", safe_replay.returncode)
            print("Safe replay output:", safe_replay.stdout.strip())

            # TEST: Confirm the failing input reproduces the vulnerability.
            assert is_memory_error(vulnerable_replay)

            # TEST: Confirm the mitigation prevents the same memory error.
            assert not is_memory_error(safe_replay)

        print("\nFUZZING RESULTS")
        print("------------------------------")

        for key, value in results.items():
            print(f"{key}: {value}")

        assert results["safe_memory_errors"] == 0
        assert results["safe_accepted"] + results["safe_rejected"] == ITERATIONS
        assert first_failure is not None
