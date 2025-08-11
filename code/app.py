import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from xml_parser import parse_xml_to_postgres
from exporter import export_table_to_excel

# Flask setup
app = Flask(__name__)
CORS(app)

# Paths
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
EXPORT_FOLDER = os.path.join(os.path.dirname(__file__), "exports")

# Database config
DB_CONFIG = {
    "host": "localhost",
    "database": "xml_converter",
    "user": "postgres",
    "password": "Srushti01$",
    "port": "5432"
}

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload():
    """Upload XML and insert into PostgreSQL."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".xml"):
        return jsonify({"error": "Only XML files are allowed"}), 400

    saved_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(saved_path)

    message, table_name = parse_xml_to_postgres(saved_path, DB_CONFIG)
    return jsonify({"message": message, "table": table_name})


@app.route("/download-excel", methods=["GET"])
def download_excel():
    """Export PostgreSQL table to Excel and return file."""
    try:
        out_path, table_name = export_table_to_excel(EXPORT_FOLDER, DB_CONFIG)
        return send_file(out_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
