"""
Windows script to import orders from CSV into Access 97 database.

Requirements:
- Python 3.x
- pyodbc library (pip install pyodbc)
- Microsoft Access Driver installed on Windows
- Access 97 database file accessible

Usage:
    python write_to_access.py export_orders_20251128_040000.csv
"""

import pyodbc
import csv
import sys
import os
from datetime import datetime


# Configuration - adjust these values
ACCESS_DB_PATH = r'C:\path\to\baecker.mdb'  # Path to Access 97 database
ACCESS_TABLE_NAME = 'Bestellungen'  # Table name in Access database


def get_access_connection():
    """
    Create connection to Access 97 database.
    """
    try:
        # Connection string for Access 97 (.mdb)
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb)};'
            f'DBQ={ACCESS_DB_PATH};'
        )
        
        conn = pyodbc.connect(conn_str)
        print(f"✓ Connected to Access database: {ACCESS_DB_PATH}")
        return conn
    except pyodbc.Error as e:
        print(f"✗ Error connecting to Access database: {e}")
        sys.exit(1)


def create_table_if_not_exists(cursor):
    """
    Create the Bestellungen table if it doesn't exist.
    
    Note: This is a simple example. Adjust fields as needed.
    """
    try:
        # Check if table exists
        cursor.execute(f"SELECT * FROM {ACCESS_TABLE_NAME}")
        print(f"✓ Table '{ACCESS_TABLE_NAME}' exists")
    except pyodbc.Error:
        print(f"  Creating table '{ACCESS_TABLE_NAME}'...")
        
        create_table_sql = f"""
        CREATE TABLE {ACCESS_TABLE_NAME} (
            ID AUTOINCREMENT PRIMARY KEY,
            order_id INTEGER,
            user_id INTEGER,
            user_email TEXT(255),
            user_first_name TEXT(100),
            user_last_name TEXT(100),
            sku TEXT(50),
            product_name TEXT(200),
            quantity INTEGER,
            unit_price_cents INTEGER,
            placed_at DATETIME,
            order_total_cents INTEGER,
            imported_at DATETIME
        )
        """
        
        try:
            cursor.execute(create_table_sql)
            cursor.commit()
            print(f"✓ Table '{ACCESS_TABLE_NAME}' created")
        except pyodbc.Error as e:
            print(f"✗ Error creating table: {e}")
            print("  Please create the table manually or adjust the schema.")


def import_csv_to_access(csv_filepath):
    """
    Import orders from CSV into Access database.
    """
    if not os.path.exists(csv_filepath):
        print(f"✗ CSV file not found: {csv_filepath}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"  IMPORT ORDERS FROM CSV TO ACCESS")
    print(f"{'='*60}\n")
    print(f"CSV file: {csv_filepath}")
    print(f"Access DB: {ACCESS_DB_PATH}")
    print(f"Table: {ACCESS_TABLE_NAME}\n")
    
    # Connect to database
    conn = get_access_connection()
    cursor = conn.cursor()
    
    # Ensure table exists
    create_table_if_not_exists(cursor)
    
    # Read CSV and insert data
    imported_count = 0
    errors = []
    
    with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Insert SQL
                insert_sql = f"""
                INSERT INTO {ACCESS_TABLE_NAME} (
                    order_id, user_id, user_email, user_first_name, user_last_name,
                    sku, product_name, quantity, unit_price_cents, placed_at,
                    order_total_cents, imported_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(insert_sql, (
                    int(row['order_id']),
                    int(row['user_id']),
                    row['user_email'],
                    row['user_first_name'],
                    row['user_last_name'],
                    row['sku'],
                    row['product_name'],
                    int(row['quantity']),
                    int(row['unit_price_cents']),
                    row['placed_at'],
                    int(row['order_total_cents']),
                    datetime.now()
                ))
                
                imported_count += 1
                
            except (ValueError, KeyError) as e:
                error_msg = f"Row {row_num}: Invalid data - {e}"
                errors.append(error_msg)
                print(f"⚠ {error_msg}")
                
            except pyodbc.Error as e:
                error_msg = f"Row {row_num}: Database error - {e}"
                errors.append(error_msg)
                print(f"⚠ {error_msg}")
    
    # Commit changes
    try:
        conn.commit()
        print(f"\n✓ Successfully imported {imported_count} order items")
        
        if errors:
            print(f"\n⚠ {len(errors)} errors occurred:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
    
    except pyodbc.Error as e:
        print(f"\n✗ Error committing transaction: {e}")
        conn.rollback()
        sys.exit(1)
    
    finally:
        cursor.close()
        conn.close()
    
    print(f"\n{'='*60}")
    print(f"  IMPORT COMPLETED")
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python write_to_access.py <csv_file>")
        print("\nExample:")
        print("  python write_to_access.py export_orders_20251128_040000.csv")
        sys.exit(1)
    
    csv_filepath = sys.argv[1]
    import_csv_to_access(csv_filepath)


if __name__ == '__main__':
    main()
