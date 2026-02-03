# Workflows Package

Unified workflow orchestration for file processing pipelines.

## Contents

- `workflow_ingest.py` - Standard ingestion workflow
- `workflow_ingest_enhanced.py` - Enhanced ingestion with multiple input modes
- `workflow_extract.py` - Microservice extraction workflow
- `workflow_verify.py` - Verification and testing workflow

## Input Methods

The enhanced workflow supports:
1. **Direct filepath**: `python workflow_ingest_enhanced.py file.py`
2. **Interactive prompt**: `echo "file.py" | python workflow_ingest_enhanced.py`
3. **Staging folder**: Select from `staging/incoming/`
4. **Scan history**: Browse previously processed files

## Usage

```bash
# Run enhanced ingestion
python workflows/workflow_ingest_enhanced.py myfile.py

# Or with multiple input modes via UI
python ui/ui_app.py
```
