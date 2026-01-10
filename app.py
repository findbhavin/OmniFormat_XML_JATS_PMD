import os
import shutil
import logging
import traceback
from flask import Flask, request, render_template, send_file
from MasterPipeline import HighFidelityConverter

# Initialize Flask
app = Flask(__name__)

# Structured logging for Cloud Run context
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniJAX_Server")

# Temporary storage paths
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_ZIP_DIR = '/tmp/packages'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_ZIP_DIR, exist_ok=True)


@app.route('/')
def index():
    """Renders the UI from templates/index.html."""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """
    Main conversion route.
    Collects: article.xml, article.html, published_article.pdf (Rendered),
    direct_from_word.pdf (Direct), and media/ folder.
    """
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    # Save incoming document
    docx_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(docx_path)
    logger.info(f"Processing conversion for: {file.filename}")

    try:
        # Run the full pipeline
        converter = HighFidelityConverter(docx_path)
        output_folder = converter.run_pipeline()

        # Package everything into a single ZIP for the user
        base_name = file.filename.rsplit('.', 1)[0]
        zip_filename = f"Conversion_Package_{base_name}"
        zip_full_path = os.path.join(OUTPUT_ZIP_DIR, zip_filename)

        # Ensure clean state for zip
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
        error_details = traceback.format_exc()
        logger.error(f"PIPELINE CRASH:\n{error_details}")
        return f"Conversion error: {str(e)}", 500

    finally:
        # Memory cleanup
        if os.path.exists(docx_path):
            os.remove(docx_path)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)