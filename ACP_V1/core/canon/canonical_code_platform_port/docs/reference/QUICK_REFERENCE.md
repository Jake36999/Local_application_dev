# Quick Reference - Canonical Code Platform v5.0

## 🚀 Quick Start (60 seconds)

```bash
# 1. Initialize RAG (10 sec)
python init_rag.py

# 2. Start Orchestrator (10 sec)
python orchestrator.py

# 3. Launch UI (10 sec)
streamlit run ui_app.py

# 4. Ingest a file (10 sec)
python workflow_ingest_enhanced.py your_file.py

# 5. Explore in browser (20 sec)
# Navigate to http://localhost:8501
```

---

## 📊 Database Files

| File | Size | Purpose | Tables |
|------|------|---------|--------|
| `canon.db` | 0.57 MB | Code analysis | 8 |
| `orchestrator_bus.db` | 0.16 MB | Events & commands | 5 |
| `settings.db` | 0.04 MB | Settings & flags | 5 |
| `rag_vectors.db` | 0.01 MB | RAG indexing | 4 |

---

## 📁 Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `ui_app.py` | 650+ | 7-tab Streamlit dashboard |
| `orchestrator.py` | 280 | File monitoring & coordination |
| `bus/message_bus.py` | 430 | Event bus & state management |
| `bus/settings_db.py` | 400 | Settings registry |
| `rag_engine.py` | 500+ | Semantic search & indexing |
| `rag_orchestrator.py` | 300+ | RAG command processor |
| `workflow_ingest_enhanced.py` | 389 | Multi-method file ingestion |

---

## 🎯 Main Features

### Orchestration
- ✓ File monitoring (staging/incoming/)
- ✓ Event-driven architecture
- ✓ Async command processing
- ✓ Status tracking

### Settings
- ✓ Persistent preferences
- ✓ Feature flags
- ✓ Type-aware values
- ✓ Audit logging

### UI Dashboard (7 Tabs)
1. 🏠 **Dashboard** - System metrics
2. 📊 **Analysis** - Code components
3. 🚀 **Extraction** - Microservices
4. 📈 **Drift History** - Versions
5. 🎛️ **Orchestrator** - Bus monitoring
6. 🤖 **RAG Analysis** - Semantic search
7. ⚙️ **Settings** - Configuration

### RAG (Retrieval-Augmented Generation)
- ✓ Semantic component search
- ✓ AI-augmented analysis
- ✓ Relationship tracking
- ✓ Recommendations
- ✓ Augmented reports

---

## 💾 Staging Folder Structure

```
staging/
├── incoming/       # New files waiting to process
├── processed/      # Successfully processed
├── failed/         # Processing failures
├── archive/        # Historical files
└── legacy/         # Migrated legacy files
```

---

## 🔄 Event Types

```
staging_file_detected       → New file in incoming/
rag_indexing_completed      → RAG index updated
rag_component_analysis      → Component analyzed
rag_semantic_search         → Search executed
rag_augmented_report        → Report generated
```

---

## ⚙️ Settings Reference

```python
# User Settings
staging_enabled             → bool  (default: true)
auto_scan                   → bool  (default: true)
scan_interval_seconds       → int   (default: 5)
ui_port                     → int   (default: 8501)
max_file_size_mb            → int   (default: 100)
retention_days              → int   (default: 30)
auto_cleanup                → bool  (default: true)
rag_integration_enabled     → bool  (default: false)
dark_mode                   → bool  (default: false)
notifications_enabled       → bool  (default: true)
```

---

## 🔍 Search & Query Commands

```bash
# Message Bus Events
sqlite3 orchestrator_bus.db "SELECT event_type, COUNT(*) FROM bus_events GROUP BY event_type;"

# Pending Commands
sqlite3 orchestrator_bus.db "SELECT command_type, status, COUNT(*) FROM bus_commands GROUP BY command_type, status;"

# State Variables
sqlite3 orchestrator_bus.db "SELECT * FROM bus_state ORDER BY state_key;"

# User Settings
sqlite3 settings.db "SELECT setting_key, setting_value FROM user_settings;"

# Feature Flags
sqlite3 settings.db "SELECT flag_name, enabled FROM feature_flags;"

# Indexed Components
sqlite3 rag_vectors.db "SELECT COUNT(*) FROM indexed_components;"

# RAG Augmentations
sqlite3 rag_vectors.db "SELECT augmentation_type, COUNT(*) FROM rag_augmentations GROUP BY augmentation_type;"
```

---

## 🎮 Common Operations

### Ingest a File

```bash
# Method 1: Direct
python workflow_ingest_enhanced.py myfile.py

# Method 2: Interactive
echo "myfile.py" | python workflow_ingest_enhanced.py

# Method 3: Staging (drop file in staging/incoming/)
# Orchestrator detects automatically
```

### Enable RAG

```python
from bus.settings_db import SettingsDB
sdb = SettingsDB()
sdb.set_feature_flag('rag_integration_enabled', True)
```

### Query Message Bus

```python
from bus.message_bus import MessageBus
bus = MessageBus()

# Get recent events
events = bus.get_events(limit=10)
for evt in events:
    print(f"{evt['event_type']}: {evt['timestamp']}")

# Get pending commands
commands = bus.get_pending_commands()
print(f"Pending: {len(commands)}")

# Get system state
status = bus.get_state('orchestrator_status')
scans = bus.get_state('total_scans')
```

### Perform Semantic Search

```python
from rag_orchestrator import get_rag_orchestrator
orch = get_rag_orchestrator()

# Search
results = orch.search_components("error handling", top_k=5)
for r in results:
    print(f"{r['component_name']}: {r['similarity_score']:.2f}")

# Analyze component
analysis = orch.analyze_component(component_id)
print(analysis['recommendations'])

# Generate report
report = orch.get_augmented_report(file_id)
print(f"Analyzed {report['analyzed_components']} components")
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Orchestrator not detecting files | Verify staging/incoming/ exists, check logs |
| UI tab missing | Ensure all Python files exist, restart streamlit |
| No components indexed | Ingest files first via workflow_ingest_enhanced.py |
| Settings not saving | Check settings.db exists and is writable |
| RAG unavailable | Run `python init_rag.py` to initialize |

---

## 📈 Performance Notes

- **Orchestrator Interval:** 5 seconds (configurable)
- **Message Bus:** SQLite with WAL mode
- **Settings:** In-memory cache + disk persistence
- **RAG Search:** O(n) where n = indexed components
- **UI:** Real-time updates via Streamlit reruns

---

## 🔐 Security Considerations

- SQLite files are local (no network exposure)
- Feature flags prevent unauthorized RAG usage
- Audit logging for all settings changes
- Command validation via message bus
- No sensitive data in logs

---

## 📚 Documentation Files

| File | Content |
|------|---------|
| `RAG_GUIDE.md` | Complete RAG documentation |
| `staging/README.md` | Staging folder guide |
| `SYSTEM_COMPLETE.md` | Full system summary |
| This file | Quick reference |

---

## 🎯 Next Steps

1. **For Development:**
   - Modify RAG embedding model (currently TF-IDF)
   - Add new analysis types
   - Extend UI with custom tabs

2. **For Operations:**
   - Monitor orchestrator logs
   - Review settings audit trail
   - Schedule regular backups

3. **For Scaling:**
   - Implement distributed message bus
   - Add horizontal scaling for RAG
   - Set up monitoring/alerting

---

## 💡 Tips & Tricks

- **Faster indexing:** Pre-ingest large files
- **Better search:** Use specific, meaningful queries
- **Monitoring:** Watch orchestrator logs in real-time
- **Debugging:** Use database queries directly
- **Performance:** Adjust scan_interval_seconds as needed

---

## 📞 Support Resources

- **Documentation:** `RAG_GUIDE.md`, `staging/README.md`
- **Logs:** Check `logs/orchestrator.log`
- **Tests:** Run `python run_system_tests.py`
- **Diagnostics:** Execute `python verify_orchestrator.py`

---

**Version:** 5.0  
**Last Updated:** February 2, 2026  
**Status:** Production Ready ✓
