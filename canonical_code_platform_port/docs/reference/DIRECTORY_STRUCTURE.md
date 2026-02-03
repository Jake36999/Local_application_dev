# Directory Structure Map

**Canonical Code Platform v5.0** - Organized Directory Layout

```
canonical_code_platform__v2/
│
├── 📁 core/                          # Core platform modules
│   ├── __init__.py
│   ├── README.md
│   ├── canon_db.py                   # Database schema
│   ├── canon_extractor.py            # Component extraction
│   └── ingest.py                     # Ingestion pipeline
│
├── 📁 analysis/                      # Analysis modules
│   ├── __init__.py
│   ├── README.md
│   ├── cut_analysis.py               # Microservice identification
│   ├── rule_engine.py                # Governance rules
│   ├── drift_detector.py             # Version drift detection
│   ├── semantic_rebuilder.py         # Semantic rebuilding
│   └── symbol_resolver.py            # Symbol resolution
│
├── 📁 workflows/                     # Workflow orchestration
│   ├── __init__.py
│   ├── README.md
│   ├── workflows/workflow_ingest.py            # Standard ingestion
│   ├── workflow_ingest_enhanced.py   # Enhanced ingestion (4 input modes)
│   ├── workflows/workflow_extract.py           # Microservice extraction
│   ├── workflows/workflow_verify.py            # Verification workflow
│   └── (other workflow files)
│
├── 📁 ui/                            # User interface
│   ├── __init__.py
│   ├── README.md
│   └── ui_app.py                     # Streamlit dashboard (7 tabs)
│
├── 📁 bus/                           # Message bus system
│   ├── __init__.py
│   ├── README.md
│   ├── message_bus.py                # Event bus & command queue
│   └── settings_db.py                # Settings registry
│
├── 📁 orchestrator/                  # Orchestrator system
│   ├── __init__.py
│   ├── README.md
│   └── orchestrator.py               # Main orchestrator (at root ref)
│
├── 📁 staging/                       # File staging area
│   ├── README.md
│   ├── incoming/                     # Drop files here
│   ├── processed/                    # Successful scans (timestamped)
│   ├── failed/                       # Failed scans
│   ├── archive/                      # Historical files
│   ├── legacy/                       # Migrated legacy files
│   │   ├── test_phase7_rules.py
│   │   ├── test_directives.py
│   │   └── MIGRATION_LOG.json
│   └── metadata.json                 # Scan manifest
│
├── 📁 tests/                         # Test suite
│   ├── test_suite.py
│   ├── conftest.py
│   └── (other test files)
│
├── 📁 tools/                         # Diagnostic tools
│   ├── debug_db.py
│   ├── debug_rebuild.py
│   ├── verify_orchestrator.py
│   ├── run_system_tests.py
│   ├── check_bus_status.py
│   └── (other tools)
│
├── 📁 docs/                          # Documentation
│   ├── README.md
│   ├── TESTING.md
│   └── (other docs)
│
├── 📁 .backup/                       # Deprecated files archive
│   └── (archived files)
│
├── 📁 logs/                          # Application logs
│   └── orchestrator.log
│
├── 📁 __pycache__/                   # Python cache
│
├── 🐍 orchestrator.py                # Main orchestrator (root level)
├── 🐍 rag_engine.py                  # RAG engine (root level)
├── 🐍 rag_orchestrator.py            # RAG orchestrator (root level)
├── 🐍 migrate_legacy.py              # Migration script
├── 🐍 init_rag.py                    # RAG initialization
│
├── ⚙️ orchestrator_config.json       # Orchestrator config
├── 📊 orchestrator_bus.db            # Message bus database
├── 📊 settings.db                    # Settings database
├── 📊 canon.db                       # Main analysis database
├── 📊 rag_vectors.db                 # RAG vector database
│
├── 📄 setup.py                       # Project setup
├── 📄 pytest.ini                     # Pytest configuration
├── 📄 start_orchestrator.bat         # Windows launcher
│
└── 📄 README.md                      # Project README
```

## Directory Purposes

### Core (`core/`)
Database schema and component extraction engines.

### Analysis (`analysis/`)
Code analysis, governance, and drift detection modules.

### Workflows (`workflows/`)
Unified workflow pipelines for file processing.

### UI (`ui/`)
Web interface using Streamlit with 7 tabs.

### Bus (`bus/`)
Message bus for event-driven coordination.

### Orchestrator (`orchestrator/`)
Background file monitoring and workflow orchestration.

### Staging (`staging/`)
File intake and processing area with subdirectories.

### Tests (`tests/`)
Test suite and testing configurations.

### Tools (`tools/`)
Diagnostic and verification tools.

### Docs (`docs/`)
System documentation and guides.

## Key Files at Root Level

### Scripts
- `orchestrator.py` - Main orchestrator (can move to orchestrator/)
- `rag_engine.py` - RAG engine (can move to analysis/)
- `rag_orchestrator.py` - RAG coordination (can move to bus/)
- `migrate_legacy.py` - Legacy migration
- `init_rag.py` - RAG initialization

### Configuration
- `orchestrator_config.json` - Orchestrator configuration
- `setup.py` - Project setup configuration
- `pytest.ini` - Testing configuration

### Databases
- `canon.db` - Main analysis database
- `orchestrator_bus.db` - Message bus events/commands
- `settings.db` - User settings and feature flags
- `rag_vectors.db` - RAG component index

### Launchers
- `start_orchestrator.bat` - Windows batch launcher

## Import Patterns

### From Core Modules
```python
from core.canon_db import CanonicalCodeDB
from core.canon_extractor import ComponentExtractor
```

### From Analysis Modules
```python
from analysis.cut_analysis import CutAnalyzer
from analysis.rule_engine import RuleEngine
```

### From Workflows
```python
from workflows.workflow_ingest_enhanced import EnhancedWorkflow
```

### From UI
```python
from ui.ui_app import create_dashboard
```

### From Bus
```python
from bus.message_bus import MessageBus
from bus.settings_db import SettingsDB
```

## Future Reorganization

These files could be moved into the `orchestrator/` directory for better organization:
- `orchestrator.py` → `orchestrator/orchestrator.py`
- `rag_orchestrator.py` → `orchestrator/rag_orchestrator.py`
- `migrate_legacy.py` → `orchestrator/migrate_legacy.py`

These could be moved into `analysis/`:
- `rag_engine.py` → `analysis/rag_engine.py`

This would centralize orchestration and analysis logic.

## Statistics

- **Total Directories**: 13
- **Total Python Packages**: 6 (with __init__.py)
- **Documentation Files**: 6+ README.md files
- **Databases**: 4 SQLite databases
- **Total Files**: 70+

## Generated Files

Generated at runtime:
- `orchestrator_bus.db` - Created by MessageBus
- `settings.db` - Created by SettingsDB
- `rag_vectors.db` - Created by RAG system
- `orchestrator_config.json` - Created by Orchestrator
- `logs/orchestrator.log` - Created by logging
