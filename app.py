import os
import shutil
from flask import Flask, request, render_template, send_file, jsonify
from MasterPipeline import HighFidelityConverter

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files: return "No file", 400
    file = request.files['file']
    docx_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(docx_path)
    
    try:
        converter = HighFidelityConverter(docx_path)
        output_dir = converter.run_pipeline()
        
        zip_path = os.path.join(UPLOAD_FOLDER, "jats_package")
        shutil.make_archive(zip_path, 'zip', output_dir)
        
        return send_file(zip_path + ".zip", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)