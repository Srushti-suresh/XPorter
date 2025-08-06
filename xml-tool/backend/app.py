from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import traceback
from plyer import notification
from xml_parser import process_xml_to_postgres
from exporter import export_table_to_excel


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
EXPORT_FOLDER = 'exports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# ✅ Add this
db_config = {
    'dbname': 'xml_converter',
    'user': 'postgres',
    'password': 'Srushti01$',
    'host': 'localhost',
    'port': 5432
}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty file name'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        msg = process_xml_to_postgres(file_path, db_config)

        # ✅ Show notification
        notification.notify(
            title="Upload Successful ✅",
            message=msg,
            timeout=5
        )

        return jsonify({'message': msg}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)