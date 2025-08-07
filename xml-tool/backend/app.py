from flask import Flask, request, jsonify
from flask_cors import CORS
from xml_parser import parse_xml_and_insert_to_db
import os

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'xml_converter',
    'user': 'postgres',
    'password': 'Srushti01$'
}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.xml'):
        # Save file
        filepath = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)

        # Parse and insert into DB
        parse_xml_and_insert_to_db(filepath, db_config)

        return jsonify({'message': '✅ XML file successfully uploaded and data inserted into PostgreSQL!'})
    else:
        return jsonify({'error': 'Only XML files are allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)
