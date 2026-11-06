
"""
PURPOSE:
Test a third-party package update before approving installation.

SECURITY CONTEXT:
Candidate packages are installed in an isolated temporary environment.
Updates that fail security regression tests are rejected.
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
TEST_DIRECTORY = PROJECT_ROOT / "tests"


def run_command(command):
    """
    PURPOSE: Execute a command and return whether it succeeded.
    RETURNS: True for exit code zero; otherwise False.
    """

    result = subprocess.run(command, check=False)
    return result.returncode == 0


def verify_update(package_path):
    """
    PURPOSE: Validate a candidate package using automated tests.
    INPUTS: Path to the candidate Python wheel.
    RETURNS: True if installation and all tests succeed.
    SECURITY: A failed installation or test prevents approval.
    """

    package = Path(package_path).resolve()

    if not package.is_file() or package.suffix != ".whl":
        print("REJECTED: Candidate must be an existing wheel file.")
        return False

    # STEP: Create an isolated environment for the candidate dependency.
    with tempfile.TemporaryDirectory() as temporary_directory:
        environment = Path(temporary_directory) / "venv"
        venv.create(environment, with_pip=True)

        python = environment / "bin" / "python"

        # STEP: Install pytest in the isolated testing environment.
        if not run_command([
            str(python), "-m", "pip", "install", "pytest"
        ]):
            return False

        # STEP: Install the candidate without accessing package indexes.
        if not run_command([
            str(python), "-m", "pip", "install",
            "--no-index", "--no-deps", str(package)
        ]):
            return False

        print("\nRunning dependency security tests...\n")

        # TEST: Execute regression tests against the candidate package.
        return run_command([
            str(python), "-m", "pytest",
            str(TEST_DIRECTORY), "-v", "-rA"
        ])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_update.py <package.whl>")
        sys.exit(2)

    approved = verify_update(sys.argv[1])

    if approved:
        print("\nAPPROVED: Candidate passed the security tests.")
        sys.exit(0)

    print("\nREJECTED: Candidate failed verification.")
    sys.exit(1)
