import os
import shutil
import logging
import traceback
from flask import Flask, request, render_template, send_file, jsonify
from datetime import datetime
from MasterPipeline import HighFidelityConverter

app = Flask(__name__)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OmniJAX_Server")

# Cloud Run writable paths
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_ZIP_DIR = '/tmp/packages'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_ZIP_DIR, exist_ok=True)


# Health check endpoint for Cloud Run
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "OmniJAX",
        "version": "1.3.0",
        "timestamp": datetime.utcnow().isoformat(),
        "jats_compliance": "1.3 OASIS",
        "features": ["JATS XML", "Dual PDF", "PMC Validation", "AI Repair"]
    }), 200


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    start_time = datetime.now()

    if 'file' not in request.files:
        logger.error("No file uploaded")
        return jsonify({
            "error": "No file uploaded",
            "status": "failed"
        }), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("No file selected")
        return jsonify({
            "error": "No file selected",
            "status": "failed"
        }), 400

    # Validate file extension
    if not file.filename.lower().endswith('.docx'):
        logger.error(f"Invalid file type: {file.filename}")
        return jsonify({
            "error": "Only .docx files are supported",
            "status": "failed"
        }), 400

    # Save uploaded file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    docx_path = os.path.join(UPLOAD_FOLDER, safe_filename)

    try:
        file.save(docx_path)
        file_size_mb = os.path.getsize(docx_path) / (1024 * 1024)
        logger.info(f"Received: {file.filename} ({file_size_mb:.2f} MB)")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return jsonify({
            "error": f"File save failed: {str(e)}",
            "status": "failed"
        }), 500

    try:
        # Run the full pipeline
        logger.info("Starting conversion pipeline...")
        converter = HighFidelityConverter(docx_path)
        output_folder = converter.run_pipeline()

        # Package all outputs into ZIP
        base_name = os.path.splitext(safe_filename)[0]
        zip_filename = f"JATS_Package_{base_name}"
        zip_full_path = os.path.join(OUTPUT_ZIP_DIR, zip_filename)

        # Clean existing zip
        if os.path.exists(zip_full_path + ".zip"):
            os.remove(zip_full_path + ".zip")

        # Create ZIP archive
        shutil.make_archive(zip_full_path, 'zip', output_folder)
        zip_file_path = zip_full_path + ".zip"
        zip_size_mb = os.path.getsize(zip_file_path) / (1024 * 1024)

        logger.info(f"Package created: {zip_file_path} ({zip_size_mb:.2f} MB)")

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Send the ZIP file
        return send_file(
            zip_file_path,
            as_attachment=True,
            download_name=f"{zip_filename}.zip",
            mimetype='application/zip',
            max_age=0
        )

    except subprocess.CalledProcessError as e:
        logger.error(f"Conversion process error: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        return jsonify({
            "error": f"Conversion process failed: {str(e)}",
            "details": e.stderr if hasattr(e, 'stderr') else None,
            "status": "failed"
        }), 500

    except Exception as e:
        # Log full traceback for debugging
        error_trace = traceback.format_exc()
        logger.error(f"Conversion failed: {str(e)}\n{error_trace}")

        return jsonify({
            "error": f"Conversion failed: {str(e)}",
            "traceback": error_trace if app.debug else None,
            "status": "failed"
        }), 500

    finally:
        # Clean up uploaded DOCX
        if os.path.exists(docx_path):
            try:
                os.remove(docx_path)
                logger.info(f"Cleaned up: {docx_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {docx_path}: {e}")

        # Optional: Clean old files from /tmp
        cleanup_old_files(UPLOAD_FOLDER, hours=1)
        cleanup_old_files(OUTPUT_ZIP_DIR, hours=1)


def cleanup_old_files(directory, hours=1):
    """Clean up files older than specified hours."""
    try:
        now = datetime.now()
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_age = now - datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_age.total_seconds() > (hours * 3600):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up old file: {file_path}")
    except Exception as e:
        logger.debug(f"Cleanup warning: {e}")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    logger.info(f"Starting OmniJAX Server on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"JATS Schema: Loaded from local repository")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )