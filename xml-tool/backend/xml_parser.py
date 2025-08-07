# backend/xml_parser.py
import xml.etree.ElementTree as ET
import psycopg2
import re

def sanitize_identifier(name):
    return re.sub(r'\W|^(?=\d)', '_', name)

def flatten_element(element):
    """Convert one XML element into a flat dict"""
    row = {}
    for child in element:
        tag = sanitize_identifier(child.tag)
        if len(child):
            row.update(flatten_element(child))
        elif child.attrib:
            for attr_name, attr_val in child.attrib.items():
                row[f"{tag}_{sanitize_identifier(attr_name)}"] = attr_val
        else:
            row[tag] = child.text
    return row

def parse_xml_and_insert_to_db(xml_path, db_config):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    table_name = sanitize_identifier(root.tag)

    rows = [flatten_element(child) for child in root]
    if not rows:
        raise Exception("No valid data found in XML.")

    col_names = sorted(set().union(*[row.keys() for row in rows]))

    # Fill missing columns with None
    for row in rows:
        for col in col_names:
            row.setdefault(col, None)
    col_values = [[row[col] for col in col_names] for row in rows]

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    cur.execute(f'DROP TABLE IF EXISTS "{table_name}";')

    create_query = f"""
        CREATE TABLE "{table_name}" (
            {', '.join([f'"{col}" TEXT' for col in col_names])}
        );
    """
    cur.execute(create_query)

    insert_query = f"""
        INSERT INTO "{table_name}" ({', '.join([f'"{col}"' for col in col_names])})
        VALUES ({', '.join(['%s'] * len(col_names))});
    """
    cur.executemany(insert_query, col_values)

    conn.commit()
    cur.close()
    conn.close()

    return f"✅ Inserted {len(rows)} rows into table '{table_name}'"
