import os
import shutil
import traceback
import logging
from flask import Flask, request, render_template, send_file
from MasterPipeline import HighFidelityConverter

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_ZIP_DIR = '/tmp/packages'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_ZIP_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniJAX_Server")


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
        output_folder = converter.run_pipeline()

        # Zip all assets
        zip_path = os.path.join(OUTPUT_ZIP_DIR, f"Package_{file.filename.split('.')[0]}")
        shutil.make_archive(zip_path, 'zip', output_folder)

        return send_file(zip_path + ".zip", as_attachment=True)
    except Exception as e:
        logger.error(traceback.format_exc())
        return f"Conversion failed: {str(e)}", 500
    finally:
        # CRITICAL: If you delete this, your server will eventually run out of disk space
        if os.path.exists(docx_path):
            os.remove(docx_path)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)