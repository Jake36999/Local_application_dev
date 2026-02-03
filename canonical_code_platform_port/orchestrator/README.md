# Orchestrator Package

Event-driven orchestration system for background file monitoring and workflow coordination.

## Contents

- `orchestrator.py` - Main orchestrator daemon (at root, reference here)

## Features

- **Staging Folder Monitoring**: Continuously monitors `staging/incoming/` for new files
- **Event Publishing**: Publishes `staging_file_detected` events to message bus
- **Command Queuing**: Sends `ingest` commands for detected files
- **Status Tracking**: Maintains orchestrator state (IDLE, RUNNING, etc.)
- **Configuration**: Auto-generates `orchestrator_config.json`
- **Background Threading**: Runs as daemon thread with configurable intervals

## Configuration

Edit `orchestrator_config.json`:

```json
{
  "staging": {
    "enabled": true,
    "incoming_dir": "staging/incoming/",
    "processed_dir": "staging/processed/",
    "failed_dir": "staging/failed/",
    "scan_interval_seconds": 5
  },
  "workflows": {
    "auto_run": ["ingest", "cut_analysis", "governance"],
    "max_concurrent": 3,
    "timeout_seconds": 300
  }
}
```

## Running the Orchestrator

```bash
# Initialize with default config
python orchestrator/orchestrator.py --init

# Start monitoring
python orchestrator/orchestrator.py

# Or use Windows batch launcher
start_orchestrator.bat
```

## Message Bus Integration

### Events Published

- `staging_file_detected` - New file detected
- `rag_indexing_completed` - RAG index updated
- `rag_component_analysis` - Component analyzed
- `rag_semantic_search` - Search executed

### Commands Supported

- `ingest` - Trigger file ingestion
- `rag_index` - Index components
- `rag_analyze` - Analyze component
- `rag_search` - Semantic search

## Status Monitoring

```python
from bus.message_bus import MessageBus

bus = MessageBus()
status = bus.get_state('orchestrator_status')
scans = bus.get_state('total_scans')
failed = bus.get_state('failed_scans')
```
