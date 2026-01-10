import os
import shutil
import logging
import traceback
from flask import Flask, request, render_template, send_file
from MasterPipeline import HighFidelityConverter

app = Flask(__name__)

# Cloud Run writable paths
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_ZIP_DIR = '/tmp/packages'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_ZIP_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniJAX_Server")


@app.route('/')
def index():
    # Flask finds index.html in the 'templates' folder automatically
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    docx_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(docx_path)
    logger.info(f"Received file: {file.filename}")

    try:
        # Run 6-step pipeline
        converter = HighFidelityConverter(docx_path)
        output_folder = converter.run_pipeline()

        # Zip all assets: article.xml, both PDFs, and media/ folder
        base_name = file.filename.rsplit('.', 1)[0]
        zip_filename = f"JATS_Package_{base_name}"
        zip_full_path = os.path.join(OUTPUT_ZIP_DIR, zip_filename)

        if os.path.exists(zip_full_path + ".zip"):
            os.remove(zip_full_path + ".zip")

        shutil.make_archive(zip_full_path, 'zip', output_folder)

        return send_file(
            zip_full_path + ".zip",
            as_attachment=True,
            download_name=f"{zip_filename}.zip",
            mimetype='application/zip'
        )

    except Exception as e:
        # Log full traceback for Cloud Run 500 error debugging
        logger.error(traceback.format_exc())
        return f"Conversion failed: {str(e)}", 500

    finally:
        if os.path.exists(docx_path):
            os.remove(docx_path)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)