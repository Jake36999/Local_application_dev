# Canonical Code Platform

**Production-ready code intelligence and microservice extraction platform**

> 🚀 **New to the platform?** Start with [QUICKSTART.md](QUICKSTART.md) for a 5-minute tutorial  
> 📚 **Want system details?** See [ARCHITECTURE.md](ARCHITECTURE.md) for design and data model  
> 🔄 **Need workflow reference?** Check [WORKFLOWS.md](WORKFLOWS.md) for all commands  
> 🔧 **Migrating from old scripts?** See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)  
> ✅ **Testing & verification?** Read [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md)

---

## Quick Start

### 1. Analyze Your Code
```bash
python workflows/workflow_ingest.py myfile.py
```

**What it does:**
- Extracts canonical components (Phase 1)
- Tracks symbols and scopes (Phase 2)
- Builds call graph (Phase 3)
- Runs governance rules (Phase 7)
- Generates compliance report

**Output:**
- `canon.db` - Updated with analysis
- `governance_report.txt` - Human-readable report
- `governance_report.json` - Machine-readable format

---

### 2. Extract Microservices
```bash
python workflows/workflow_extract.py
```

**What it does:**
- Checks governance gates
- Identifies extraction-ready components
- Generates production artifacts

**Output:**
- `extracted_services/<service_name>/`
  - `interface.py` - Abstract base class
  - `api.py` - FastAPI endpoints
  - `Dockerfile` - Container definition
  - `deployment.yaml` - Kubernetes config
  - `requirements.txt` - Dependencies
  - `README.md` - Documentation

---

### 3. Verify System
```bash
python workflows/workflow_verify.py
```
python workflows/workflow_ingest.py myfile.py
**What it does:**
- Tests all 7 phases
- Reports operational status
- Identifies issues
python workflows/workflow_extract.py
---

### 4. View UI
```bash
streamlit run ui_app.py
```

- Component browser
- Drift history
- Governance dashboard
- Extraction preview

---
## System Architecture

### 7 Operational Phases

| Phase | Capability | Details |
|-------|-----------|---------|
python workflows/workflow_ingest.py myfile.py
| **Phase 2** | Symbol Tracking (variables, scopes) | [ARCHITECTURE.md](ARCHITECTURE.md#phase-2-symbol-tracking-variables) |
| **Phase 3** | Call Graph (dependencies, metrics) | [ARCHITECTURE.md](ARCHITECTURE.md#phase-3-call-graph-dependencies) |
python workflows/workflow_ingest.py myfile.py
| **Phase 5** | Comment Metadata (directives, governance hints) | [ARCHITECTURE.md](ARCHITECTURE.md#phase-5-comment-metadata-directives) |
| **Phase 6** | Drift Detection (version tracking, changes) | [ARCHITECTURE.md](ARCHITECTURE.md#phase-6-drift-detection-versions) |
| **Phase 7** | Governance (rule validation, extraction gates) | [ARCHITECTURE.md](ARCHITECTURE.md#phase-7-governance-rules-gating) |

**All phases verified operational.** See [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md) for testing details.

---

python workflows/workflow_ingest.py <file.py>

### Drift Detection (Re-ingestion)
```bash
# Initial version
python workflows/workflow_ingest.py myfile.py

# Modify your file, then re-ingest
python workflows/workflow_ingest.py myfile.py
# → Automatically detects changes, creates Version 2
```

```bash
python governance_report.py
# View: governance_report.txt
```

### Manual Phase Execution
If you need fine-grained control:
```bash
python ingest.py myfile.py          # Phase 1-6
python symbol_resolver.py            # Phase 2
python cut_analysis.py               # Phase 3
python rule_engine.py                # Phase 7
python microservice_export.py        # Extraction
```

---

## Troubleshooting

### "No files found in database"
**Solution:** Ingest a file first
```bash
python workflows/workflow_ingest.py <file.py>
```

### "Gate BLOCKED"
**Solution:** Fix blocking errors
```bash
python rule_engine.py
type governance_report.txt
# Fix errors in your code, then re-ingest
```

### "No extraction candidates"
**Solution:** Add extraction hints
```python
# Add to your code:
# @extract
# @service_candidate
def my_function():
    pass
```
Then re-run: `python workflows/workflow_ingest.py <file.py>`

---

## Documentation

### Primary Documentation (Start Here)
- 📖 **[QUICKSTART.md](QUICKSTART.md)** - 5-minute tutorial for new users
- 📖 **[WORKFLOWS.md](WORKFLOWS.md)** - Comprehensive workflow guide
- 📖 **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Transition from old scripts

### Technical Reference
- 📖 **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & data model
- 📖 **[VERIFICATION_PLAN.md](VERIFICATION_PLAN.md)** - Phase status & testing strategy
- [`PHASE6_SUMMARY.md`](PHASE6_SUMMARY.md) - Drift detection guide
- [`PHASE7_COMPLETE.md`](PHASE7_COMPLETE.md) - Governance rules reference
- [`PHASE5_VERIFICATION.md`](PHASE5_VERIFICATION.md) - Comment metadata validation

---

## Technology Stack

- **Python 3.11+** - Core language
- **SQLite3** - Embedded database (no setup required)
- **FastAPI** - Generated microservice APIs
- **Streamlit** - Interactive UI
- **Docker** - Container scaffolding
- **Kubernetes** - Deployment configs

---

## System Requirements

- Python 3.11 or higher
- No external dependencies (uses Python stdlib)
- ~100MB disk space for database
- Windows/Linux/Mac compatible

---

## Next Steps

1. **Run Analysis:** `python workflows/workflow_ingest.py <file.py>`
2. **View Results:** `streamlit run ui_app.py`
3. **Extract Services:** `python workflows/workflow_extract.py`
4. **Deploy:** `cd extracted_services/<service>/ && docker build .`

For detailed workflow guide, see documentation above.
