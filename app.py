import os
import shutil
import logging
import traceback
from flask import Flask, request, render_template, send_file, jsonify
from MasterPipeline import HighFidelityConverter

# Initialize Flask app
app = Flask(__name__)

# Configure Logging for Google Cloud
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniJAX_Server")

# Cloud Run uses /tmp as the only writable partition
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_ZIP_DIR = '/tmp/packages'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_ZIP_DIR, exist_ok=True)


@app.route('/')
def index():
    """Renders the main upload interface."""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """
    Handles file upload, triggers MasterPipeline,
    and returns a ZIP containing all JATS/PDF assets.
    """
    if 'file' not in request.files:
        logger.error("No file part in request")
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        logger.error("No file selected")
        return "No file selected", 400

    # 1. Save the incoming DOCX
    docx_filename = file.filename
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    file.save(docx_path)
    logger.info(f"Received file: {docx_filename}")

    try:
        # 2. Initialize and Run the MasterPipeline
        converter = HighFidelityConverter(docx_path)
        output_folder = converter.run_pipeline()

        # 3. Create a ZIP package of the output directory
        # This includes article.xml, article.html, published_article.pdf, and media/ folder
        base_name = docx_filename.rsplit('.', 1)[0]
        zip_filename = f"JATS_Package_{base_name}"
        zip_full_path = os.path.join(OUTPUT_ZIP_DIR, zip_filename)

        # Clean up existing zip if it exists
        if os.path.exists(zip_full_path + ".zip"):
            os.remove(zip_full_path + ".zip")

        logger.info("Zipping conversion assets...")
        shutil.make_archive(zip_full_path, 'zip', output_folder)

        # 4. Return the ZIP file to the user
        return send_file(
            zip_full_path + ".zip",
            as_attachment=True,
            download_name=f"{zip_filename}.zip",
            mimetype='application/zip'
        )

    except Exception as e:
        # Log the full error to Cloud Run logs for debugging
        error_details = traceback.format_exc()
        logger.error(f"Conversion System Failure:\n{error_details}")

        # Return a user-friendly error message
        return f"Conversion failed: {str(e)}", 500

    finally:
        # Cleanup: Remove the uploaded DOCX to save memory
        if os.path.exists(docx_path):
            os.remove(docx_path)


@app.route('/health')
def health():
    """Health check endpoint for Cloud Run."""
    return "Healthy", 200


if __name__ == '__main__':
    # Cloud Run provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)