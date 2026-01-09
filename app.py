import os
import shutil
import traceback
from flask import Flask, request, render_template, send_file
from MasterPipeline import HighFidelityConverter

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files: return "No file uploaded", 400
    file = request.files['file']

    docx_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(docx_path)

    try:
        converter = HighFidelityConverter(docx_path)
        output_dir = converter.run_pipeline()

        # Package everything: XML, HTML, PDF, and Media folder
        zip_name = "manuscript_package"
        zip_path = os.path.join(UPLOAD_FOLDER, zip_name)
        shutil.make_archive(zip_path, 'zip', output_dir)

        return send_file(zip_path + ".zip", as_attachment=True)
    except Exception as e:
        error_log = traceback.format_exc()
        print(error_log)
        return f"Conversion Error: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)