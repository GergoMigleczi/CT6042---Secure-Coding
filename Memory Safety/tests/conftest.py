
"""
PURPOSE:
Provides shared compilation and execution utilities for dispatch tests.

SECURITY CONTEXT:
Compiles isolated C implementations and provides access to
the simulated dispatch database.
"""

import subprocess
from pathlib import Path

import pytest


SOURCE_DIR = Path(__file__).resolve().parent.parent

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
