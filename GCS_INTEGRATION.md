# GCS Integration Documentation

## Overview

This implementation adds Google Cloud Storage (GCS) support to OmniJAX for persisting application data. The integration is designed to be **optional and non-blocking** - if GCS is not configured or fails, the application continues to function normally.

## Features

1. **Input Persistence**: Uploads DOCX files to `gs://[bucket]/inputs/`
2. **Output Persistence**: Uploads generated ZIP packages to `gs://[bucket]/outputs/`
3. **Metrics Persistence**: Saves conversion metrics as JSON to `gs://[bucket]/metrics/`

## Configuration

Set the `GCS_BUCKET_NAME` environment variable to enable GCS integration:

```bash
export GCS_BUCKET_NAME="your-bucket-name"
```

If not set, the application will:
- Log a warning message
- Continue operating in local-only mode
- Skip all GCS operations

## Authentication

The GCS client uses Application Default Credentials (ADC). Set up authentication by:

1. **For local development**:
   ```bash
   gcloud auth application-default login
   ```

2. **For Google Cloud environments** (Cloud Run, GKE, etc.):
   - Use service account attached to the resource
   - Grant appropriate IAM permissions

## Required Permissions

The service account or user needs these IAM roles:
- `roles/storage.objectCreator` - to upload files
- `roles/storage.objectViewer` - to verify uploads (optional)

## Metrics Schema

Metrics are saved as JSON files with the following structure:

```json
{
  "conversion_id": "20240122_120000_abcd1234",
  "filename": "document.docx",
  "processing_time_seconds": 45.2,
  "input_size_mb": 2.5,
  "output_size_mb": 8.3,
  "status": "completed",
  "timestamp": "2024-01-22T12:01:00.000000"
}
```

For failed conversions:
```json
{
  "conversion_id": "20240122_120000_abcd1234",
  "filename": "document.docx",
  "processing_time_seconds": 12.1,
  "input_size_mb": 2.5,
  "output_size_mb": 0,
  "status": "failed",
  "error": "Error message here",
  "timestamp": "2024-01-22T12:01:00.000000"
}
```

## Testing

Run the GCS utility tests:
```bash
pytest tests/test_gcs_utils.py -v
```

Test with GCS enabled:
```bash
export GCS_BUCKET_NAME="test-bucket"
python app.py
```

Test without GCS (fallback mode):
```bash
unset GCS_BUCKET_NAME
python app.py
```

## Design Decisions

### Non-blocking Operations
GCS operations are designed to be non-blocking:
- Failed uploads are logged but don't affect conversion status
- Missing credentials cause a warning, not an error
- Application continues to function without GCS

This ensures backward compatibility and reliability.

### Separate Directories
Files are organized in separate directories:
- `inputs/` - Original DOCX files
- `outputs/` - Generated ZIP packages
- `metrics/` - JSON metrics files

This organization makes it easier to:
- Set up lifecycle policies
- Grant different access permissions
- Query and analyze data

### Filename Convention
- Inputs: `{conversion_id}_{sanitized_filename}`
- Outputs: `OmniJAX_{base_name}.zip`
- Metrics: `{conversion_id}_metrics.json`

The conversion_id includes timestamp and random hex for uniqueness.

## Future Enhancements

Potential improvements for future versions:
1. Add retry logic for transient failures
2. Implement batch uploads for better performance
3. Add metrics aggregation and reporting
4. Support for additional cloud storage providers
5. Configurable retention policies

## Troubleshooting

### Warning: "GCS_BUCKET_NAME environment variable not set"
- **Cause**: GCS_BUCKET_NAME is not configured
- **Solution**: Set the environment variable or ignore if GCS is not needed

### Error: "Your default credentials were not found"
- **Cause**: GCS credentials not configured
- **Solution**: Run `gcloud auth application-default login` or configure service account

### Error: "Failed to upload {file} to GCS"
- **Cause**: Insufficient permissions or network issues
- **Solution**: Check IAM permissions and network connectivity
- **Impact**: Local files are still available, GCS copy is skipped

## Monitoring

Key metrics to monitor:
- GCS upload success rate
- Upload latency
- Storage costs
- Failed upload patterns

Consider setting up Cloud Monitoring alerts for:
- High failure rates
- Unusual upload sizes
- Storage quota approaching limits
