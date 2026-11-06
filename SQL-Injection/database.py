
"""
PURPOSE:
Creates and initialises the Order Processing System database.

SECURITY CONTEXT:
Contains fictional customer orders for the SQL injection demonstration.
No real customer information is stored.
"""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "orders.db"


def initialise_database():
    """
    PURPOSE: Creates the orders table and inserts sample orders.
    SECURITY: Uses fixed SQL statements and fictional test data.
    """

    # STEP: Open the database, creating the file if it does not exist.
    with sqlite3.connect(DATABASE_PATH) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                reference TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                product TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)

        # STEP: Add fictional orders for the vulnerability demonstration.
        # Existing records are preserved if this script is run again.
        connection.executemany("""
            INSERT OR IGNORE INTO orders
            (reference, customer_name, product, quantity, total, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("ORD-1001", "Alice Smith", "Laptop", 1, 799.99, "Processing"),
            ("ORD-1002", "Bob Jones", "Monitor", 2, 349.98, "Dispatched"),
            ("ORD-1003", "Charlie Brown", "Keyboard", 1, 59.99, "Delivered"),
            ("ORD-1004", "Alice Smith", "Mouse", 1, 24.99, "Processing")
        ])

        connection.commit()

    print("Database initialised successfully.")


def search_orders(reference):
    """
    PURPOSE: Retrieves orders matching the supplied reference.
    INPUTS: reference entered by the customer.
    RETURNS: A list of matching order records.
    SECURITY: Intentionally vulnerable to SQL injection.
    """

    with sqlite3.connect(DATABASE_PATH) as connection:

        # Allow columns to be accessed by name instead of index.
        connection.row_factory = sqlite3.Row

        # VULNERABILITY: User input is inserted directly into the SQL query.
        # Crafted input can modify the WHERE condition.
        query = f"SELECT * FROM orders WHERE reference = '{reference}'"

        cursor = connection.execute(query)

        return cursor.fetchall()


def search_orders_safe(reference):
    """
    PURPOSE: Retrieves orders matching the supplied reference.
    INPUTS: reference entered by the customer.
    RETURNS: A list of matching order records.
    SECURITY: Uses a parameterised query to prevent SQL injection.
    """

    with sqlite3.connect(DATABASE_PATH) as connection:

        connection.row_factory = sqlite3.Row

        # MITIGATION: Parameter binding separates user input from SQL syntax.
        query = "SELECT * FROM orders WHERE reference = ?"

        cursor = connection.execute(query, (reference,))

        return cursor.fetchall()




if __name__ == "__main__":
    initialise_database()
