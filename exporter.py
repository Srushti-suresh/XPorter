import os
import time
import psycopg2
import pandas as pd

def export_table_to_excel(export_folder, db_config, table_name="xml_data"):
    """Export PostgreSQL table to Excel with timestamp to avoid file lock issues."""
    conn = psycopg2.connect(**db_config)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()

    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(export_folder, f"{table_name}_{timestamp}.xlsx")

    df.to_excel(out_path, index=False)
    return out_path, table_name
