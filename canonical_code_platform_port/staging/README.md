# Staging Folder - File Intake System

## Overview
This folder is the primary entry point for code analysis in the Canonical Code Platform.

## Structure

### `/incoming/`
**Purpose**: Drop new Python files here for analysis

**Rules**:
- Only `.py` files are processed
- Files are scanned on orchestrator tick (every 5 seconds)
- Successfully scanned files → `processed/`
- Failed scans → `failed/`

**Example**:
```bash
cp myfile.py staging/incoming/
# Orchestrator automatically picks it up
```

### `/processed/`
**Purpose**: Archive successfully scanned files

**Structure**: `processed/<DATE>/<SCAN_ID>/`
- Original file preserved
- Scan metadata stored
- Searchable by date or scan ID

**Example**:
```
processed/
├── 2024-01-15/
│   ├── scan_0f3a1b2c/
│   │   ├── calculator.py
│   │   ├── scan_manifest.json
│   │   └── analysis_result.json
```

### `/failed/`
**Purpose**: Files that failed scanning

**Structure**: `failed/<FAILURE_REASON>/`
- Original file preserved
- Error logs attached
- Can be retried

**Example**:
```
failed/
├── syntax_error/
│   ├── bad_file.py
│   └── error_log.txt
├── missing_dependency/
│   └── ...
```

### `/archive/`
**Purpose**: Long-term storage (optional)

**Rules**:
- Files moved here after 30 days in `processed/`
- Kept for compliance/historical review
- Rarely accessed

### `/legacy/`
**Purpose**: Historical test and example files

**Contents**:
- Moved from root directory
- Reference implementations
- No longer actively used
- Preserved for posterity

---

## Usage Examples

### Manual File Addition
```bash
# Copy to incoming
cp ~/projects/mymodule.py staging/incoming/

# Orchestrator processes automatically
# File moves to processed/ with scan results
```

### Batch Import
```bash
# Scan entire directory
cp /path/to/project/*.py staging/incoming/

# Orchestrator queues and processes sequentially
```

### Check Scan History
```bash
# View recent scans
ls -la staging/processed/2024-01-15/

# View failed scans
ls -la staging/failed/
```

### Direct Filepath (Alternative)
```bash
# If you don't want to use staging/
python workflows/workflow_ingest.py /absolute/path/to/file.py
```

---

## Manifest File (`metadata.json`)

Tracks all staging operations for audit trail:

```json
{
  "last_scan": "2024-01-15T14:32:15Z",
  "total_files_processed": 127,
  "total_files_failed": 3,
  "scans": [
    {
      "scan_id": "0f3a1b2c",
      "timestamp": "2024-01-15T14:30:00Z",
      "filename": "calculator.py",
      "status": "SUCCESS",
      "file_id": "uuid-of-file",
      "version": 1,
      "location": "processed/2024-01-15/scan_0f3a1b2c/"
    }
  ]
}
```

---

## Orchestrator Integration

The orchestrator monitors this folder continuously:

1. **Every 5 seconds**: Check `incoming/` for new files
2. **Process**: Run full analysis pipeline
3. **Move**: File → `processed/` or `failed/`
4. **Update**: `metadata.json` with results
5. **Notify**: UI dashboard updates with new scans

---

## Cleanup Policy

| Folder | Retention | Action |
|--------|-----------|--------|
| `incoming/` | 5 min | Auto-process |
| `processed/` | 30 days | Move to `archive/` |
| `failed/` | 7 days | Delete (configurable) |
| `archive/` | 1 year | Delete |

---

## Configuration

Edit `orchestrator_config.json`:

```json
{
  "staging": {
    "enabled": true,
    "incoming_dir": "staging/incoming/",
    "processed_dir": "staging/processed/",
    "failed_dir": "staging/failed/",
    "archive_dir": "staging/archive/",
    "scan_interval_seconds": 5,
    "retention_days": 30,
    "auto_cleanup": true
  }
}
```
