import os
import shutil
import logging
import traceback
from flask import Flask, request, render_template, send_file
from MasterPipeline import HighFidelityConverter

# Initialize Flask app
app = Flask(__name__)

# Configure structured logging for Google Cloud Run
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniJAX_Server")

# Cloud Run uses /tmp as the only writable partition
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_ZIP_DIR = '/tmp/packages'

# Ensure temporary directories exist at runtime
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_ZIP_DIR, exist_ok=True)


@app.route('/')
def index():
    """
    Renders the main upload interface.
    Flask automatically looks in the /templates folder for index.html.
    """
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """
    Handles file upload, triggers the HighFidelityConverter pipeline,
    and returns a ZIP containing:
    1. article.xml (JATS 1.3 OASIS)
    2. published_article.pdf (Rendered from JATS)
    3. direct_from_word.pdf (Requirement 2: Direct conversion)
    4. media/ (Requirement 3: Image folder)
    5. article.html (Preview file)
    """
    if 'file' not in request.files:
        logger.error("No file part in request")
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        logger.error("No file selected")
        return "No file selected", 400

    # 1. Save the incoming DOCX to the temporary upload folder
    docx_filename = file.filename
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    file.save(docx_path)
    logger.info(f"Received file: {docx_filename}. Starting pipeline...")

    try:
        # 2. Initialize and Run the MasterPipeline
        # This executes the 6 steps including direct PDF and table caption fixes
        converter = HighFidelityConverter(docx_path)
        output_folder = converter.run_pipeline()

        # 3. Create a ZIP package of the output directory
        # The base_name is used to create a unique filename for the user
        base_name = docx_filename.rsplit('.', 1)[0]
        zip_filename = f"JATS_Package_{base_name}"
        zip_full_path = os.path.join(OUTPUT_ZIP_DIR, zip_filename)

        # Clean up existing zip of the same name if it exists from a previous run
        if os.path.exists(zip_full_path + ".zip"):
            os.remove(zip_full_path + ".zip")

        logger.info("Zipping conversion assets into full package...")
        shutil.make_archive(zip_full_path, 'zip', output_folder)

        # 4. Return the ZIP file to the user as an attachment
        return send_file(
            zip_full_path + ".zip",
            as_attachment=True,
            download_name=f"{zip_filename}.zip",
            mimetype='application/zip'
        )

    except Exception as e:
        # Requirement: Do not lose context. Log the full traceback to Cloud Run Logs.
        error_details = traceback.format_exc()
        logger.error(f"PIPELINE CRASH during conversion of {docx_filename}:\n{error_details}")

        # Return a simple error message to the browser
        return f"Conversion failed: {str(e)}", 500

    finally:
        # Cleanup: Remove the uploaded DOCX to save container memory
        if os.path.exists(docx_path):
            try:
                os.remove(docx_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup {docx_path}: {cleanup_error}")


@app.route('/health')
def health():
    """Health check endpoint for Google Cloud Run container monitoring."""
    return "Healthy", 200


if __name__ == '__main__':
    # Cloud Run provides the PORT environment variable (default 8080)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)