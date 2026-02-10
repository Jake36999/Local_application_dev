ACP v1 is a governed IDE + control plane.

ACP does NOT include:
- IRER simulation execution
- domain-specific physics logic
- experimental reasoning engines

All subsystems below ACP are strictly functional.
All intelligence is mediated via workflows.

| Domain           | Canonical Location                          |
| ---------------- | ------------------------------------------- |
| Boot / lifecycle | `run_boot.bat`, `startup_config.yaml`       |
| Orchestrator     | `orchestrator.py`                           |
| Bundling         | `tooling/bundler/Directory_bundler_v4.5.py` |
| Static analysis  | `tooling/analysis/analysis/`                |
| Ingest / RAG     | `tooling/ingest/`                           |
| Workflows        | `workflows/`                                |
| Memory           | `memory/sql`, `memory/vector`               |
| UI               | `ui/`                                       |

* Anything outside these paths is **non-authoritative**
* No refactors yet
* No file moves yet
