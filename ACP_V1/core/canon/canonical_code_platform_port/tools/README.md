# Diagnostic Tools

These scripts are for debugging and inspection only.  
They are **NOT** part of the main test suite or verification workflow.

## Usage

### Check Database State
```bash
python tools/debug_db.py
```
Shows database contents: components, imports, calls, etc.

### Debug Queries
```bash
python tools/debug_queries.py
```
Run diagnostic SQL queries to inspect data.

### Debug Rebuild Process
```bash
python tools/debug_rebuild.py
```
Trace rebuild process for debugging.

### Trace Rebuild Lineage
```bash
python tools/trace_rebuild.py
```
Trace component rebuild lineage.

### Manual Rebuild
```bash
python tools/manual_rebuild.py
```
Manually trigger rebuild process.

---

## For Testing & Verification

**Use these instead:**
- `python workflows/workflow_verify.py` - Comprehensive phase verification
- `python workflows/workflow_ingest.py <file>` - Ingest and analyze files
- `streamlit run ui_app.py` - Visual inspection via UI

---

**Note:** These tools access `canon.db` directly and are for development/debugging only.
