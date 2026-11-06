
"""
PURPOSE:
Tests the mitigated order search functions.

SECURITY CONTEXT:
Verifies that parameterised
queries prevent SQL Injection attack without affecting normal searches.
"""

import pytest
import database


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """
    PURPOSE: Creates an isolated database for each test.
    SECURITY: Prevents tests from modifying the application's database.
    """

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "orders.db"
    )

    database.initialise_database()


def test_safe_search_blocks_injection(test_database):
    """
    PURPOSE: Confirms that parameterised queries prevent SQL injection.
    """

    malicious_input = "' OR ''='"

    results = database.search_orders_safe(malicious_input)

    # TEST: The malicious input must not return any orders.
    assert len(results) == 0


def test_safe_search_legitimate_input(test_database):
    """
    PURPOSE: Confirms that legitimate order searches still work.
    """

    results = database.search_orders_safe("ORD-1001")

    # TEST: Only the requested order should be returned.
    assert len(results) == 1
    assert results[0]["reference"] == "ORD-1001"
    assert results[0]["customer_name"] == "Alice Smith"


def test_safe_search_unknown_reference(test_database):
    """
    PURPOSE: Confirms that unknown references return no results.
    """

    results = database.search_orders_safe("ORD-9999")

    assert len(results) == 0
