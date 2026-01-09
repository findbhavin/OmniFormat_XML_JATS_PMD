import os
import traceback
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
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    docx_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(docx_path)

    try:
        converter = HighFidelityConverter(docx_path)
        output_dir = converter.run_pipeline()

        # Zip the results
        import shutil
        zip_path = os.path.join(UPLOAD_FOLDER, "jats_package")
        if os.path.exists(zip_path + ".zip"):
            os.remove(zip_path + ".zip")
        shutil.make_archive(zip_path, 'zip', output_dir)

        return send_file(zip_path + ".zip", as_attachment=True)

    except Exception as e:
        # THIS IS THE KEY: It prints the full error stack to the logs
        error_details = traceback.format_exc()
        print(f"!!! CONVERSION ERROR !!!\n{error_details}")
        return f"Conversion failed: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)