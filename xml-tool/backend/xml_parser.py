import xml.etree.ElementTree as ET
import psycopg2
import re

def sanitize_identifier(name):
    return re.sub(r'\W|^(?=\d)', '_', name)

def flatten_xml(element, parent_prefix=''):
    data = {}
    for child in element:
        tag = sanitize_identifier(child.tag)
        key = f"{parent_prefix}{tag}" if parent_prefix else tag

        if len(child):  # has nested children
            data.update(flatten_xml(child, parent_prefix=key + '_'))
        elif child.attrib:
            for attr_name, attr_val in child.attrib.items():
                data[f"{key}_{sanitize_identifier(attr_name)}"] = attr_val
        else:
            data[key] = child.text
    return data

def process_xml_to_postgres(xml_path, db_config):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    table_name = sanitize_identifier(root.tag)
    flat_data = flatten_xml(root)

    if not flat_data:
        raise Exception("No valid data found in XML.")

    col_names = list(flat_data.keys())
    col_values = [list(flat_data.values())]
  

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    cur.execute(f"DROP TABLE IF EXISTS {table_name};")

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

    return f"Inserted 1 row into table '{table_name}'"
