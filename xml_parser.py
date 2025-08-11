import os
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2 import sql

def flatten_xml(element, parent_key='', result=None):
    """Recursively flatten XML into a dict with full tag paths."""
    if result is None:
        result = {}

    # Add attributes
    for attr, value in element.attrib.items():
        result[f"{parent_key}_attr_{attr}" if parent_key else f"attr_{attr}"] = value

    # Add text content
    text = (element.text or '').strip()
    if text:
        result[parent_key] = text

    # Process children
    for child in element:
        child_key = f"{parent_key}__{child.tag}" if parent_key else child.tag
        flatten_xml(child, child_key, result)

    return result


def parse_xml_to_postgres(xml_file, db_config, table_name="xml_data"):
    """Parse XML file and insert data into PostgreSQL, replacing old table."""
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    tree = ET.parse(xml_file)
    root = tree.getroot()

    rows = []
    flat = flatten_xml(root)
    if flat:
        rows.append(flat)

    if not rows:
        conn.close()
        return "No data found in XML", table_name

    all_columns = sorted({col for row in rows for col in row.keys()})
    safe_columns = [col.replace('.', '__') for col in all_columns]

    # Drop existing table to avoid mismatch
    cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name)))

    # Create new table
    col_defs = ", ".join(f'"{col}" TEXT' for col in safe_columns)
    cur.execute(sql.SQL("CREATE TABLE {} ({})").format(sql.Identifier(table_name), sql.SQL(col_defs)))

    # Insert data
    for row in rows:
        values = [row.get(col, None) for col in all_columns]
        placeholders = ", ".join(["%s"] * len(all_columns))
        cur.execute(
            sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(sql.Identifier(c) for c in safe_columns),
                sql.SQL(placeholders)
            ),
            values
        )

    conn.commit()
    conn.close()
    return f"Inserted {len(rows)} row(s) into {table_name}", table_name
