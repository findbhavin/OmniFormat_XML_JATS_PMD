#!/usr/bin/env python3
"""
Conversion ID Lookup Utility for OmniJAX

This script fetches input and output files based on a conversion ID for debugging purposes.
It can retrieve file information from GCS and optionally download files locally.

Usage:
    python tools/fetch_conversion.py <conversion_id>
    python tools/fetch_conversion.py <conversion_id> --download
    python tools/fetch_conversion.py <conversion_id> --download --output-dir /path/to/dir
"""

import sys
import os
import argparse
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConversionFetcher:
    """Fetches conversion data from GCS based on conversion ID."""
    
    def __init__(self, conversion_id: str):
        """
        Initialize the fetcher with a conversion ID.
        
        Args:
            conversion_id: The conversion ID to fetch (format: YYYYMMDD_HHMMSS_<8-char-hex>)
        """
        self.conversion_id = conversion_id
        self.bucket_name = os.environ.get('GCS_BUCKET_NAME', 'omnijaxstorage')
        self.client = None
        self.bucket = None
        self.gcs_enabled = False
        
        self._init_gcs()
    
    def _init_gcs(self):
        """Initialize GCS client."""
        try:
            from google.cloud import storage
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            self.gcs_enabled = True
            logger.info(f"Connected to GCS bucket: {self.bucket_name}")
        except ImportError:
            logger.error("Google Cloud Storage library not installed. Run: pip install google-cloud-storage")
            self.gcs_enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            logger.warning("Some features may not be available without GCS access")
            self.gcs_enabled = False
    
    def get_conversion_info(self) -> Dict[str, Any]:
        """
        Get conversion information including file paths and metrics.
        
        Returns:
            Dictionary containing conversion details
        """
        info = {
            "conversion_id": self.conversion_id,
            "gcs_enabled": self.gcs_enabled,
            "bucket_name": self.bucket_name if self.gcs_enabled else None,
            "input_file": None,
            "output_file": None,
            "metrics": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self.gcs_enabled:
            logger.warning("GCS not available. Cannot fetch file information.")
            return info
        
        # List all blobs with the conversion ID prefix
        try:
            # Find input file
            input_prefix = f"inputs/{self.conversion_id}_"
            input_blobs = list(self.bucket.list_blobs(prefix=input_prefix, max_results=10))
            if input_blobs:
                info["input_file"] = {
                    "gcs_path": f"gs://{self.bucket_name}/{input_blobs[0].name}",
                    "name": input_blobs[0].name,
                    "size_mb": input_blobs[0].size / (1024 * 1024) if input_blobs[0].size else 0,
                    "created": input_blobs[0].time_created.isoformat() if input_blobs[0].time_created else None,
                    "content_type": input_blobs[0].content_type
                }
                logger.info(f"Found input file: {input_blobs[0].name}")
            else:
                logger.warning(f"No input file found with prefix: {input_prefix}")
            
            # Find output file
            output_prefix = f"outputs/OmniJAX_{self.conversion_id}_"
            output_blobs = list(self.bucket.list_blobs(prefix=output_prefix, max_results=10))
            if output_blobs:
                info["output_file"] = {
                    "gcs_path": f"gs://{self.bucket_name}/{output_blobs[0].name}",
                    "name": output_blobs[0].name,
                    "size_mb": output_blobs[0].size / (1024 * 1024) if output_blobs[0].size else 0,
                    "created": output_blobs[0].time_created.isoformat() if output_blobs[0].time_created else None,
                    "content_type": output_blobs[0].content_type
                }
                logger.info(f"Found output file: {output_blobs[0].name}")
            else:
                logger.warning(f"No output file found with prefix: {output_prefix}")
            
            # Find metrics file
            metrics_blob_name = f"metrics/{self.conversion_id}_metrics.json"
            metrics_blob = self.bucket.blob(metrics_blob_name)
            if metrics_blob.exists():
                metrics_json = metrics_blob.download_as_text()
                info["metrics"] = json.loads(metrics_json)
                logger.info(f"Found metrics file: {metrics_blob_name}")
            else:
                logger.warning(f"No metrics file found: {metrics_blob_name}")
        
        except Exception as e:
            logger.error(f"Error fetching conversion info: {e}")
        
        return info
    
    def download_files(self, output_dir: str = "./downloads") -> bool:
        """
        Download input and output files locally.
        
        Args:
            output_dir: Directory to save downloaded files
            
        Returns:
            True if download succeeded, False otherwise
        """
        if not self.gcs_enabled:
            logger.error("GCS not available. Cannot download files.")
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Downloading files to: {output_dir}")
        
        success = True
        info = self.get_conversion_info()
        
        try:
            # Download input file
            if info.get("input_file"):
                input_blob_name = info["input_file"]["name"]
                input_blob = self.bucket.blob(input_blob_name)
                local_input_path = os.path.join(output_dir, os.path.basename(input_blob_name))
                
                logger.info(f"Downloading input file: {input_blob_name}")
                input_blob.download_to_filename(local_input_path)
                logger.info(f"✓ Saved to: {local_input_path}")
            else:
                logger.warning("No input file to download")
                success = False
            
            # Download output file
            if info.get("output_file"):
                output_blob_name = info["output_file"]["name"]
                output_blob = self.bucket.blob(output_blob_name)
                local_output_path = os.path.join(output_dir, os.path.basename(output_blob_name))
                
                logger.info(f"Downloading output file: {output_blob_name}")
                output_blob.download_to_filename(local_output_path)
                logger.info(f"✓ Saved to: {local_output_path}")
            else:
                logger.warning("No output file to download")
                success = False
            
            # Download metrics file if available
            if info.get("metrics"):
                metrics_path = os.path.join(output_dir, f"{self.conversion_id}_metrics.json")
                with open(metrics_path, 'w', encoding='utf-8') as f:
                    json.dump(info["metrics"], f, indent=2)
                logger.info(f"✓ Saved metrics to: {metrics_path}")
        
        except Exception as e:
            logger.error(f"Error downloading files: {e}")
            success = False
        
        return success
    
    def print_summary(self, info: Dict[str, Any]):
        """Print a formatted summary of the conversion information."""
        print("\n" + "=" * 70)
        print(f"CONVERSION ID: {info['conversion_id']}")
        print("=" * 70)
        
        if not info.get("gcs_enabled"):
            print("\n⚠ GCS not available. Limited information available.")
            print("\nTo enable GCS features:")
            print("  1. Install: pip install google-cloud-storage")
            print("  2. Set environment: export GCS_BUCKET_NAME=your-bucket")
            print("  3. Authenticate: gcloud auth application-default login")
            return
        
        # Input file info
        print("\n📥 INPUT FILE:")
        if info.get("input_file"):
            input_info = info["input_file"]
            print(f"  Path:         {input_info['gcs_path']}")
            print(f"  Size:         {input_info['size_mb']:.2f} MB")
            print(f"  Created:      {input_info.get('created', 'N/A')}")
            print(f"  Content Type: {input_info.get('content_type', 'N/A')}")
        else:
            print("  ⚠ Not found")
        
        # Output file info
        print("\n📤 OUTPUT FILE:")
        if info.get("output_file"):
            output_info = info["output_file"]
            print(f"  Path:         {output_info['gcs_path']}")
            print(f"  Size:         {output_info['size_mb']:.2f} MB")
            print(f"  Created:      {output_info.get('created', 'N/A')}")
            print(f"  Content Type: {output_info.get('content_type', 'N/A')}")
        else:
            print("  ⚠ Not found")
        
        # Metrics info
        print("\n📊 CONVERSION METRICS:")
        if info.get("metrics"):
            metrics = info["metrics"]
            print(f"  Status:           {metrics.get('status', 'N/A')}")
            print(f"  Filename:         {metrics.get('filename', 'N/A')}")
            print(f"  Processing Time:  {metrics.get('processing_time_seconds', 'N/A'):.2f}s")
            print(f"  Input Size:       {metrics.get('input_size_mb', 'N/A'):.2f} MB")
            print(f"  Output Size:      {metrics.get('output_size_mb', 'N/A'):.2f} MB")
            print(f"  Timestamp:        {metrics.get('timestamp', 'N/A')}")
            if metrics.get('error'):
                print(f"  ⚠ Error:          {metrics['error']}")
        else:
            print("  ⚠ No metrics available")
        
        print("\n" + "=" * 70 + "\n")


def validate_conversion_id(conversion_id: str) -> bool:
    """
    Validate conversion ID format.
    
    Expected format: YYYYMMDD_HHMMSS_<8-char-hex>
    Example: 20260120_152731_42a34914
    
    Args:
        conversion_id: The conversion ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    parts = conversion_id.split('_')
    if len(parts) != 3:
        return False
    
    # Check date part (YYYYMMDD)
    if len(parts[0]) != 8 or not parts[0].isdigit():
        return False
    
    # Check time part (HHMMSS)
    if len(parts[1]) != 6 or not parts[1].isdigit():
        return False
    
    # Check hex part (8 characters, hex digits)
    if len(parts[2]) != 8:
        return False
    try:
        int(parts[2], 16)
    except ValueError:
        return False
    
    return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Fetch conversion files and metrics from GCS by conversion ID',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get conversion information
  python tools/fetch_conversion.py 20260120_152731_42a34914
  
  # Download files locally
  python tools/fetch_conversion.py 20260120_152731_42a34914 --download
  
  # Download to specific directory
  python tools/fetch_conversion.py 20260120_152731_42a34914 --download --output-dir /tmp/debug

Conversion ID format: YYYYMMDD_HHMMSS_<8-char-hex>
Example: 20260120_152731_42a34914
        """
    )
    
    parser.add_argument(
        'conversion_id',
        help='Conversion ID to fetch (format: YYYYMMDD_HHMMSS_<8-char-hex>)'
    )
    
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download files locally for inspection'
    )
    
    parser.add_argument(
        '--output-dir',
        default='./downloads',
        help='Directory to save downloaded files (default: ./downloads)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON instead of formatted text'
    )
    
    args = parser.parse_args()
    
    # Validate conversion ID format
    if not validate_conversion_id(args.conversion_id):
        logger.error(f"Invalid conversion ID format: {args.conversion_id}")
        logger.error("Expected format: YYYYMMDD_HHMMSS_<8-char-hex>")
        logger.error("Example: 20260120_152731_42a34914")
        sys.exit(1)
    
    # Create fetcher and get info
    fetcher = ConversionFetcher(args.conversion_id)
    info = fetcher.get_conversion_info()
    
    # Output results
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        fetcher.print_summary(info)
    
    # Download files if requested
    if args.download:
        print(f"\n📦 Downloading files to: {args.output_dir}")
        success = fetcher.download_files(args.output_dir)
        if success:
            print("✓ Download completed successfully")
            sys.exit(0)
        else:
            print("⚠ Download completed with warnings")
            sys.exit(1)


if __name__ == '__main__':
    main()
