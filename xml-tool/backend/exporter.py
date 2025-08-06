# backend/exporter.py
import pandas as pd
import psycopg2

DB_CONFIG = {
    'dbname': 'xml_converter',
    'user': 'postgres',
    'password': 'Srushti01$',
    'host': 'localhost',
    'port': 5432
}

def export_table_to_excel():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = cursor.fetchall()

    if not tables:
        raise Exception("No tables found.")

    last_table = tables[-1][0]
    df = pd.read_sql_query(f"SELECT * FROM {last_table};", conn)
    filepath = f"exports/{last_table}.xlsx"
    df.to_excel(filepath, index=False)

    cursor.close()
    conn.close()
    return filepath
