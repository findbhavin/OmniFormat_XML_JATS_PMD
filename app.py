import os
import shutil
import logging
import traceback
import subprocess
import threading
from datetime import datetime
from flask import Flask, request, render_template, send_file, jsonify, abort
from MasterPipeline import HighFidelityConverter

app = Flask(__name__)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("OmniJAX_Server")

# Cloud Run writable paths
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_ZIP_DIR = '/tmp/packages'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_ZIP_DIR, exist_ok=True)

# In-memory progress store (for single-instance deployments)
# NOTE: For multi-instance deployments, use Redis or a job queue system
conversion_progress = {}


def cleanup_old_progress_entries():
    """Clean up old progress entries to prevent memory leaks."""
    try:
        now = datetime.now()
        to_delete = []
        for conversion_id, progress in conversion_progress.items():
            # Remove entries older than 1 hour
            if "start_time" in progress:
                age = (now - progress["start_time"]).total_seconds()
                if age > 3600:  # 1 hour
                    to_delete.append(conversion_id)
        
        for conversion_id in to_delete:
            del conversion_progress[conversion_id]
            logger.debug(f"Cleaned up old progress entry: {conversion_id}")
            
    except Exception as e:
        logger.warning(f"Progress cleanup error: {e}")


# Health check endpoint for Cloud Run
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Cloud Run and load balancers."""
    try:
        # Check if required tools are available
        pandoc_version = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            text=True
        )

        health_info = {
            "status": "healthy",
            "service": "OmniJAX",
            "version": "1.3.0",
            "timestamp": datetime.utcnow().isoformat(),
            "jats_compliance": "1.3 OASIS",
            "features": [
                "JATS XML Generation",
                "Dual PDF Output",
                "PMC/NLM Validation",
                "AI Content Repair",
                "Media Extraction"
            ],
            "dependencies": {
                "pandoc": pandoc_version.stdout.split('\n')[0] if pandoc_version.returncode == 0 else "unavailable",
                "python": "3.11",
                "vertexai": "1.71.1",
                "weasyprint": "61.2"
            },
            "environment": {
                "upload_folder_exists": os.path.exists(UPLOAD_FOLDER),
                "output_folder_exists": os.path.exists(OUTPUT_ZIP_DIR),
                "free_disk_space": shutil.disk_usage('/tmp').free // (1024 * 1024)  # MB
            }
        }

        return jsonify(health_info), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route('/version', methods=['GET'])
def version():
    """Return version information."""
    return jsonify({
        "name": "OmniJAX",
        "version": "1.3.0",
        "description": "Professional JATS XML & Dual PDF Engine",
        "jats_schema": "1.3 OASIS Publishing",
        "author": "OmniJAX Team",
        "license": "Proprietary"
    }), 200


@app.route('/')
def index():
    """Serve the main upload page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Failed to render index: {e}")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>OmniJAX - JATS 1.3 High-Fidelity Converter</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .container { background: white; padding: 3rem; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.1); width: 450px; text-align: center; }
                h1 { color: #1a73e8; margin-bottom: 1rem; }
                .status { color: #d93025; padding: 1rem; background: #fce8e6; border-radius: 6px; margin: 1rem 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>OmniJAX</h1>
                <p>Professional JATS XML & Dual PDF Engine</p>
                <div class="status">
                    Service temporarily unavailable. Please check back soon.
                </div>
                <p><a href="/health">Check service health</a></p>
            </div>
        </body>
        </html>
        """, 500


def run_conversion_background(conversion_id, docx_path, safe_filename, original_filename):
    """Run conversion in background thread with progress tracking."""
    try:
        # Update progress: starting
        conversion_progress[conversion_id]["status"] = "processing"
        conversion_progress[conversion_id]["message"] = "Starting conversion pipeline..."
        conversion_progress[conversion_id]["progress"] = 10
        
        logger.info(f"[{conversion_id}] Starting conversion pipeline...")
        converter = HighFidelityConverter(docx_path)
        output_folder = converter.run_pipeline()
        
        # Update progress: packaging
        conversion_progress[conversion_id]["progress"] = 80
        conversion_progress[conversion_id]["message"] = "Packaging output files..."

        # Package all outputs into ZIP
        base_name = os.path.splitext(safe_filename)[0]
        zip_filename = f"OmniJAX_{base_name}"
        zip_full_path = os.path.join(OUTPUT_ZIP_DIR, zip_filename)

        # Clean existing zip if exists
        if os.path.exists(zip_full_path + ".zip"):
            try:
                os.remove(zip_full_path + ".zip")
            except:
                pass

        # Create ZIP archive
        shutil.make_archive(zip_full_path, 'zip', output_folder)
        zip_file_path = zip_full_path + ".zip"
        zip_size = os.path.getsize(zip_file_path)
        zip_size_mb = zip_size / (1024 * 1024)

        logger.info(f"[{conversion_id}] Package created: {zip_file_path} ({zip_size_mb:.2f} MB)")

        # Calculate processing time
        processing_time = (datetime.now() - conversion_progress[conversion_id]["start_time"]).total_seconds()

        # Update progress: completed
        conversion_progress[conversion_id]["status"] = "completed"
        conversion_progress[conversion_id]["message"] = "Conversion completed successfully!"
        conversion_progress[conversion_id]["progress"] = 100
        conversion_progress[conversion_id]["download_filename"] = f"OmniJAX_{original_filename.rsplit('.', 1)[0]}.zip"
        conversion_progress[conversion_id]["download_path"] = zip_file_path
        conversion_progress[conversion_id]["file_size_mb"] = zip_size_mb
        conversion_progress[conversion_id]["processing_time"] = processing_time

        logger.info(f"[{conversion_id}] Conversion completed in {processing_time:.2f} seconds")

    except Exception as e:
        # Log full traceback for debugging
        error_trace = traceback.format_exc()
        logger.error(f"[{conversion_id}] Conversion failed: {str(e)}\n{error_trace}")

        # Update progress: failed
        conversion_progress[conversion_id]["status"] = "failed"
        conversion_progress[conversion_id]["message"] = f"Conversion failed: {str(e)}"
        conversion_progress[conversion_id]["error"] = str(e)
        conversion_progress[conversion_id]["progress"] = 0

    finally:
        # Clean up uploaded DOCX
        cleanup_file(docx_path, conversion_id, "uploaded DOCX")

        # Clean up old files to prevent disk space issues
        cleanup_old_files(UPLOAD_FOLDER, hours=1, conversion_id=conversion_id)
        cleanup_old_files(OUTPUT_ZIP_DIR, hours=1, conversion_id=conversion_id)


@app.route('/convert', methods=['POST'])
def convert():
    """Handle file upload and start async conversion."""
    conversion_id = datetime.now().strftime("%Y%m%d_%H%M%S_") + os.urandom(4).hex()

    logger.info(f"[{conversion_id}] Conversion request started")

    if 'file' not in request.files:
        logger.error(f"[{conversion_id}] No file uploaded")
        return jsonify({
            "error": "No file uploaded",
            "conversion_id": conversion_id,
            "status": "failed",
            "timestamp": datetime.utcnow().isoformat()
        }), 400

    file = request.files['file']

    if file.filename == '':
        logger.error(f"[{conversion_id}] No file selected")
        return jsonify({
            "error": "No file selected",
            "conversion_id": conversion_id,
            "status": "failed",
            "timestamp": datetime.utcnow().isoformat()
        }), 400

    # Validate file extension
    if not file.filename.lower().endswith('.docx'):
        logger.error(f"[{conversion_id}] Invalid file type: {file.filename}")
        return jsonify({
            "error": "Only .docx files are supported",
            "conversion_id": conversion_id,
            "status": "failed",
            "timestamp": datetime.utcnow().isoformat()
        }), 400

    # Save uploaded file with unique name
    safe_filename = f"{conversion_id}_{file.filename.replace(' ', '_').replace('/', '_')}"
    docx_path = os.path.join(UPLOAD_FOLDER, safe_filename)

    try:
        # Save file in chunks to handle large files
        file.save(docx_path)
        file_size = os.path.getsize(docx_path)
        file_size_mb = file_size / (1024 * 1024)

        # Check file size limit
        if file_size > MAX_FILE_SIZE:
            os.remove(docx_path)
            logger.error(f"[{conversion_id}] File too large: {file_size_mb:.2f} MB")
            return jsonify({
                "error": f"File too large ({file_size_mb:.1f} MB). Maximum size is 50 MB.",
                "conversion_id": conversion_id,
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }), 400

        logger.info(f"[{conversion_id}] File saved: {file.filename} ({file_size_mb:.2f} MB)")

        # Initialize progress tracking
        conversion_progress[conversion_id] = {
            "status": "queued",
            "message": "File uploaded, queued for conversion...",
            "progress": 0,
            "filename": file.filename,
            "file_size_mb": file_size_mb,
            "start_time": datetime.now(),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Start background conversion
        thread = threading.Thread(
            target=run_conversion_background,
            args=(conversion_id, docx_path, safe_filename, file.filename)
        )
        thread.daemon = True
        thread.start()

        # Return 202 Accepted with conversion_id
        return jsonify({
            "conversion_id": conversion_id,
            "status": "accepted",
            "message": "File uploaded successfully, conversion started",
            "filename": file.filename,
            "timestamp": datetime.utcnow().isoformat()
        }), 202

    except Exception as e:
        logger.error(f"[{conversion_id}] Failed to save file: {e}")
        return jsonify({
            "error": f"File save failed: {str(e)}",
            "conversion_id": conversion_id,
            "status": "failed",
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route('/status/<conversion_id>', methods=['GET'])
def get_status(conversion_id):
    """Get conversion status for polling."""
    # Clean up old progress entries periodically
    cleanup_old_progress_entries()
    
    if conversion_id not in conversion_progress:
        return jsonify({
            "error": "Conversion ID not found",
            "conversion_id": conversion_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 404

    status_data = conversion_progress[conversion_id].copy()
    # Don't include start_time in response (not JSON serializable)
    if "start_time" in status_data:
        del status_data["start_time"]
    
    status_data["conversion_id"] = conversion_id
    return jsonify(status_data), 200


@app.route('/download/<conversion_id>', methods=['GET'])
def download_result(conversion_id):
    """Download the conversion result."""
    if conversion_id not in conversion_progress:
        return jsonify({
            "error": "Conversion ID not found",
            "conversion_id": conversion_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 404

    progress = conversion_progress[conversion_id]
    
    if progress["status"] != "completed":
        return jsonify({
            "error": "Conversion not completed yet",
            "conversion_id": conversion_id,
            "status": progress["status"],
            "timestamp": datetime.utcnow().isoformat()
        }), 400

    if "download_path" not in progress or not os.path.exists(progress["download_path"]):
        return jsonify({
            "error": "Download file not found",
            "conversion_id": conversion_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 404

    # Prepare response
    response = send_file(
        progress["download_path"],
        as_attachment=True,
        download_name=progress["download_filename"],
        mimetype='application/zip'
    )

    # Add headers for monitoring
    response.headers['X-Conversion-ID'] = conversion_id
    response.headers['X-Processing-Time'] = f"{progress.get('processing_time', 0):.2f}s"
    response.headers['X-File-Size'] = f"{progress.get('file_size_mb', 0):.2f}MB"

    return response


def cleanup_file(file_path, conversion_id, file_type):
    """Clean up a single file with error handling."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"[{conversion_id}] Cleaned up {file_type}: {file_path}")
    except Exception as e:
        logger.warning(f"[{conversion_id}] Failed to cleanup {file_type} {file_path}: {e}")


def cleanup_old_files(directory, hours=1, conversion_id=None):
    """Clean up files older than specified hours."""
    try:
        now = datetime.now()
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    file_age = now - datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_age.total_seconds() > (hours * 3600):
                        os.remove(file_path)
                        if conversion_id:
                            logger.debug(f"[{conversion_id}] Cleaned up old file: {file_path}")
                except (OSError, FileNotFoundError):
                    pass  # File might have been deleted by another process
    except Exception as e:
        if conversion_id:
            logger.debug(f"[{conversion_id}] Cleanup warning: {e}")


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/health", "/version", "/convert", "/status/<conversion_id>", "/download/<conversion_id>"],
        "timestamp": datetime.utcnow().isoformat()
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "error": "Method not allowed",
        "message": "The HTTP method is not supported for this endpoint",
        "timestamp": datetime.utcnow().isoformat()
    }), 405


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 errors (file too large)."""
    return jsonify({
        "error": "Request entity too large",
        "message": f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024 * 1024)} MB",
        "timestamp": datetime.utcnow().isoformat()
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.utcnow().isoformat(),
        "support": "Check /health endpoint for service status"
    }), 500


@app.before_request
def log_request_info():
    """Log request information for debugging."""
    if request.endpoint and request.endpoint != 'health':
        logger.debug(f"Request: {request.method} {request.path}")
        logger.debug(f"Headers: {dict(request.headers)}")


@app.after_request
def log_response_info(response):
    """Log response information for debugging."""
    if request.endpoint and request.endpoint != 'health':
        logger.debug(f"Response: {response.status}")
    return response


def check_environment():
    """Check if required environment is properly set up."""
    logger.info("Checking environment setup...")

    # Check required directories
    required_dirs = [UPLOAD_FOLDER, OUTPUT_ZIP_DIR]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")

    # Check JATS schema files
    schema_files = [
        "JATS-journalpublishing-oasis-article1-3-mathml2.xsd",
        "JATS-journalpublishing-oasis-article1-3-elements.xsd",
        "module-oasis.xsd"
    ]

    for schema_file in schema_files:
        if os.path.exists(schema_file):
            logger.info(f"✓ JATS schema found: {schema_file}")
        else:
            logger.warning(f"⚠ JATS schema missing: {schema_file}")

    # Check templates
    if os.path.exists("templates/style.css"):
        logger.info("✓ CSS template found")
    else:
        logger.warning("⚠ CSS template missing")

    # Check pandoc
    try:
        pandoc_result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        if pandoc_result.returncode == 0:
            version_line = pandoc_result.stdout.split('\n')[0]
            logger.info(f"✓ {version_line}")
        else:
            logger.error("❌ Pandoc not found or not working")
    except Exception as e:
        logger.error(f"❌ Failed to check pandoc: {e}")

    logger.info("Environment check completed")


if __name__ == '__main__':
    # Run environment check
    check_environment()

    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.environ.get("PORT", 8080))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    logger.info(f"Starting OmniJAX Server")
    logger.info(f"  Port: {port}")
    logger.info(f"  Debug: {debug_mode}")
    logger.info(f"  Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"  Max file size: {MAX_FILE_SIZE // (1024 * 1024)} MB")
    logger.info("=" * 50)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )