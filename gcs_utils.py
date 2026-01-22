"""
Google Cloud Storage utilities for persisting OmniJAX application data.
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class GCSHandler:
    """
    Handler for Google Cloud Storage operations.
    
    This class provides methods to upload files and save metrics to GCS.
    If GCS is not configured (via GCS_BUCKET_NAME env var), operations are
    logged but skipped to maintain compatibility with development environments.
    """
    
    def __init__(self):
        """
        Initialize the GCS handler.
        
        Reads the GCS_BUCKET_NAME environment variable. If not set,
        defaults to 'omnijaxstorage'.
        """
        self.bucket_name = os.environ.get('GCS_BUCKET_NAME', 'omnijaxstorage')
        self.client = None
        self.bucket = None
        self.enabled = False
        
        try:
            from google.cloud import storage
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            self.enabled = True
            logger.info(f"GCS enabled with bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            logger.warning("Falling back to local-only mode")
    
    def upload_file(self, local_path: str, destination_blob_name: str) -> bool:
        """
        Upload a file to Google Cloud Storage.
        
        Args:
            local_path: Path to the local file to upload
            destination_blob_name: Destination path in the GCS bucket
            
        Returns:
            bool: True if upload succeeded, False otherwise
        """
        if not self.enabled:
            logger.debug(f"GCS disabled, skipping upload of {local_path}")
            return False
        
        if not os.path.exists(local_path):
            logger.error(f"Local file not found: {local_path}")
            return False
        
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(local_path)
            
            file_size_mb = os.path.getsize(local_path) / (1024 * 1024)
            logger.info(
                f"Uploaded {local_path} to gs://{self.bucket_name}/{destination_blob_name} "
                f"({file_size_mb:.2f} MB)"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to GCS: {e}")
            return False
    
    def save_metrics(self, conversion_id: str, metrics_dict: Dict[str, Any]) -> bool:
        """
        Save conversion metrics as a JSON object in GCS.
        
        Args:
            conversion_id: Unique identifier for the conversion
            metrics_dict: Dictionary containing metrics data
            
        Returns:
            bool: True if save succeeded, False otherwise
        """
        if not self.enabled:
            logger.debug(f"GCS disabled, skipping metrics save for {conversion_id}")
            return False
        
        try:
            # Add timestamp to metrics if not present
            if 'timestamp' not in metrics_dict:
                metrics_dict['timestamp'] = datetime.utcnow().isoformat()
            
            # Create blob name for metrics
            blob_name = f"metrics/{conversion_id}_metrics.json"
            blob = self.bucket.blob(blob_name)
            
            # Upload metrics as JSON
            metrics_json = json.dumps(metrics_dict, indent=2)
            blob.upload_from_string(
                metrics_json,
                content_type='application/json'
            )
            
            logger.info(
                f"Saved metrics to gs://{self.bucket_name}/{blob_name}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save metrics for {conversion_id} to GCS: {e}")
            return False
