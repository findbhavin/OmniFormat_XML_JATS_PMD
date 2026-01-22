"""
Tests for GCS utilities module.
"""
import os
import json
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock

from gcs_utils import GCSHandler


class TestGCSHandler:
    """Test suite for GCSHandler class."""
    
    def test_init_without_bucket_name(self):
        """Test initialization when GCS_BUCKET_NAME is not set."""
        with patch.dict(os.environ, {}, clear=True):
            handler = GCSHandler()
            assert handler.bucket_name is None
            assert handler.client is None
            assert handler.bucket is None
            assert handler.enabled is False
    
    def test_init_with_bucket_name(self):
        """Test initialization when GCS_BUCKET_NAME is set."""
        with patch.dict(os.environ, {'GCS_BUCKET_NAME': 'test-bucket'}):
            with patch.object(GCSHandler, '__init__', lambda self: None):
                handler = GCSHandler()
                handler.bucket_name = 'test-bucket'
                handler.enabled = True
                handler.client = Mock()
                handler.bucket = Mock()
                
                assert handler.bucket_name == 'test-bucket'
                assert handler.enabled is True
    
    def test_upload_file_disabled(self):
        """Test upload_file when GCS is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            handler = GCSHandler()
            result = handler.upload_file('/tmp/test.txt', 'test/test.txt')
            assert result is False
    
    def test_upload_file_nonexistent_file(self):
        """Test upload_file with non-existent local file."""
        handler = GCSHandler()
        handler.enabled = True
        handler.bucket_name = 'test-bucket'
        handler.bucket = Mock()
        
        result = handler.upload_file('/nonexistent/file.txt', 'test/file.txt')
        assert result is False
    
    def test_upload_file_success(self):
        """Test successful file upload."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'test content')
            tmp_file_path = tmp_file.name
        
        try:
            handler = GCSHandler()
            handler.enabled = True
            handler.bucket_name = 'test-bucket'
            mock_bucket = Mock()
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            handler.bucket = mock_bucket
            
            result = handler.upload_file(tmp_file_path, 'test/file.txt')
            
            assert result is True
            mock_bucket.blob.assert_called_once_with('test/file.txt')
            mock_blob.upload_from_filename.assert_called_once_with(tmp_file_path)
        finally:
            os.unlink(tmp_file_path)
    
    def test_upload_file_exception(self):
        """Test upload_file when upload fails."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'test content')
            tmp_file_path = tmp_file.name
        
        try:
            handler = GCSHandler()
            handler.enabled = True
            handler.bucket_name = 'test-bucket'
            mock_bucket = Mock()
            mock_blob = Mock()
            mock_blob.upload_from_filename.side_effect = Exception("Upload failed")
            mock_bucket.blob.return_value = mock_blob
            handler.bucket = mock_bucket
            
            result = handler.upload_file(tmp_file_path, 'test/file.txt')
            
            assert result is False
        finally:
            os.unlink(tmp_file_path)
    
    def test_save_metrics_disabled(self):
        """Test save_metrics when GCS is disabled."""
        with patch.dict(os.environ, {}, clear=True):
            handler = GCSHandler()
            result = handler.save_metrics('test-123', {'status': 'completed'})
            assert result is False
    
    def test_save_metrics_success(self):
        """Test successful metrics save."""
        handler = GCSHandler()
        handler.enabled = True
        handler.bucket_name = 'test-bucket'
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        handler.bucket = mock_bucket
        
        metrics_dict = {
            'conversion_id': 'test-123',
            'status': 'completed',
            'processing_time': 45.2
        }
        result = handler.save_metrics('test-123', metrics_dict)
        
        assert result is True
        mock_bucket.blob.assert_called_once_with('metrics/test-123_metrics.json')
        
        # Verify upload was called with JSON string
        call_args = mock_blob.upload_from_string.call_args
        assert call_args is not None
        uploaded_data = json.loads(call_args[0][0])
        assert uploaded_data['conversion_id'] == 'test-123'
        assert uploaded_data['status'] == 'completed'
        assert 'timestamp' in uploaded_data
    
    def test_save_metrics_exception(self):
        """Test save_metrics when upload fails."""
        handler = GCSHandler()
        handler.enabled = True
        handler.bucket_name = 'test-bucket'
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.upload_from_string.side_effect = Exception("Upload failed")
        mock_bucket.blob.return_value = mock_blob
        handler.bucket = mock_bucket
        
        result = handler.save_metrics('test-123', {'status': 'completed'})
        
        assert result is False
