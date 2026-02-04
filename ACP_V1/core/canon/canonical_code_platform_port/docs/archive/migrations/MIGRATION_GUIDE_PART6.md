# Migration Guide - Part 6: Directory Reorganization

## Overview

This guide explains how to reorganize the Canonical Code Platform into the new structured layout.

## Step 1: Files to Move to `core/`

Move these core platform files:
```
canon_db.py              → core/canon_db.py
canon_extractor.py       → core/canon_extractor.py
ingest.py                → core/ingest.py
```

**Note**: These files are typically not modified post-initialization, so moving them is safe.

## Step 2: Files to Move to `analysis/`

Move these analysis modules:
```
cut_analysis.py          → analysis/cut_analysis.py
rule_engine.py           → analysis/rule_engine.py
drift_detector.py        → analysis/drift_detector.py (if exists)
semantic_rebuilder.py    → analysis/semantic_rebuilder.py
symbol_resolver.py       → analysis/symbol_resolver.py
```

**Future**: Could move `rag_engine.py` here

## Step 3: Files to Move to `workflows/`

Move these workflow files:
```
workflows/workflow_ingest.py              → workflows/workflow_ingest.py
workflow_ingest_enhanced.py     → workflows/workflow_ingest_enhanced.py
workflows/workflow_extract.py             → workflows/workflow_extract.py
workflows/workflow_verify.py              → workflows/workflow_verify.py
(other workflow files)          → workflows/
```

## Step 4: Files Already in `ui/`

Move the UI file:
```
ui_app.py                → ui/ui_app.py
```

**Status**: This is critical - needs import updates if moved!

## Step 5: Files Already in `bus/`

These are already organized:
```
bus/__init__.py          ✓
bus/message_bus.py       ✓
bus/settings_db.py       ✓
```

No changes needed.

## Step 6: Files Already in `staging/`

These are already organized:
```
staging/incoming/        ✓
staging/processed/       ✓
staging/failed/          ✓
staging/archive/         ✓
staging/legacy/          ✓
```

No changes needed.

## Step 7: Files in `tools/` (Create if Moving)

These are diagnostic/utility files. **Optional move**:
```
debug_db.py              → tools/debug_db.py
debug_rebuild.py         → tools/debug_rebuild.py
verify_orchestrator.py   → tools/verify_orchestrator.py
run_system_tests.py      → tools/run_system_tests.py
check_bus_status.py      → tools/check_bus_status.py
(other tool files)       → tools/
```

## Step 8: Files to Keep at Root Level

These critical files should stay at root for easy access:
```
orchestrator.py          ✓ (or move to orchestrator/)
rag_engine.py            ✓
rag_orchestrator.py      ✓
migrate_legacy.py        ✓
init_rag.py              ✓
setup.py                 ✓
pytest.ini               ✓
start_orchestrator.bat   ✓
```

**Note**: These can optionally be moved, but it requires import updates.

## Import Updates Required

### If Moving Files to `core/`

Any file importing from core modules needs updates:

**Before**:
```python
from canon_db import CanonicalCodeDB
from canon_extractor import ComponentExtractor
```

**After**:
```python
from core.canon_db import CanonicalCodeDB
from core.canon_extractor import ComponentExtractor
```

### If Moving Files to `analysis/`

**Before**:
```python
from cut_analysis import CutAnalyzer
from rule_engine import RuleEngine
```

**After**:
```python
from analysis.cut_analysis import CutAnalyzer
from analysis.rule_engine import RuleEngine
```

### If Moving Files to `workflows/`

**Before**:
```python
from workflow_ingest_enhanced import EnhancedWorkflow
```

**After**:
```python
from workflows.workflow_ingest_enhanced import EnhancedWorkflow
```

### If Moving `ui_app.py` to `ui/`

**Critical**: Streamlit requires ui_app.py at root for `streamlit run ui_app.py` to work.

**Option 1**: Keep at root (recommended)

**Option 2**: Move and create wrapper at root:
```python
# ui_app.py (at root)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "ui"))

from ui_app import *
```

Then run: `streamlit run ui_app.py`

## Verification Steps

### 1. Check Syntax After Moving

```bash
python -m py_compile core/*.py
python -m py_compile analysis/*.py
python -m py_compile workflows/*.py
python -m py_compile ui/*.py
```

### 2. Test Imports

```bash
python -c "from core.canon_db import CanonicalCodeDB; print('OK')"
python -c "from analysis.cut_analysis import CutAnalyzer; print('OK')"
python -c "from workflows.workflow_ingest_enhanced import EnhancedWorkflow; print('OK')"
```

### 3. Run System Tests

```bash
python run_system_tests.py
```

### 4. Verify UI Still Works

```bash
streamlit run ui_app.py
```

## Gradual Migration Strategy

### Phase 1: Create Structure (DONE ✓)
- Create all directories
- Create all __init__.py files
- Create README files

### Phase 2: Move Non-Critical Files (Optional)
- Move core modules (safe to move)
- Move analysis modules (safe to move)
- Update imports gradually

### Phase 3: Update Critical Files (Careful)
- Update imports in orchestrator.py
- Update imports in workflows
- Test thoroughly

### Phase 4: Verify Everything (Must Do)
- Run all tests
- Test UI
- Verify orchestrator still works
- Check message bus

## Recommendation

**Current Status**: Structure is ready (directories + __init__.py created)

**Recommended Approach**:
1. Keep everything at root for now (working system)
2. Move files gradually as updates are made
3. Update imports during refactoring sessions
4. Test after each move

**Reason**: The system is working well at root level. Moving files introduces risk of import errors. Move when:
- You need to add new modules in those categories
- You're doing a major refactoring
- You want to reorganize for better maintainability

## Files Already in Correct Locations

✓ `bus/` - message_bus.py, settings_db.py
✓ `staging/` - incoming/, processed/, failed/, archive/, legacy/
✓ `docs/` - README.md created
✓ `orchestrator/` - README.md created
✓ `analysis/` - README.md created
✓ `workflows/` - README.md created
✓ `ui/` - README.md created
✓ `core/` - README.md created

## Command-Line Operations (Future)

### Move a file (when ready)
```bash
mv orchestrator.py orchestrator/orchestrator.py
```

### Update imports in a directory
```bash
find analysis/ -name "*.py" -type f -exec sed -i 's/from cut_analysis/from analysis.cut_analysis/g' {} \;
```

### Test all imports after moves
```bash
python -m py_compile core/*.py analysis/*.py workflows/*.py ui/*.py bus/*.py
```

## Support

If you encounter import errors after moving files:

1. Check the error message for the missing module
2. Verify the file exists in its new location
3. Update the import statement in the importing file
4. Re-run tests

Example:
```
ModuleNotFoundError: No module named 'canon_db'
Solution: Update import to "from core.canon_db import ..."
```

---

**Status**: Structure is ready. Files remain at root for now. Move when needed!
