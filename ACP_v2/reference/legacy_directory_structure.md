# ACP_V1 DIRECTORY_STRUCTURE.md

This document describes the unified architecture and module layout for the Autonomous Coding Platform (ACP_V1).

## Root Structure

ACP_V1/
├── orchestrator.py                # Main entry point (The Brain)
├── config/
│   └── startup.yaml               # System configuration
├── tooling/
│   ├── bundler/                   # Directory Bundler (The Eyes)
│   │   ├── scanner.py
│   │   ├── parser.py
│   │   └── bundler_constants.py
│   ├── ingest/                    # Ingest Pipeline (The Memory)
│   │   ├── core/
│   │   ├── utils/
│   │   └── orchestrator.py
│   └── analysis/                  # Static Analysis Engine
│       ├── drift_detector.py
│       ├── rule_engine.py
│       └── call_graph_normalizer.py
├── memory/
│   ├── sql/
│   │   └── project_meta.db        # Unified SQL database
│   └── vector/                    # Vector DB (ChromaDB)
├── safe_ops/
│   └── context/                   # Perception Layer
│       ├── active/
│       └── archive/
├── validation/                    # IRER Validation Suite (Immune System)
│   ├── core_engine.py
│   ├── validation_pipeline.py
│   └── modules/
├── brain/
│   ├── identity/
│   │   ├── configs/
│   │   │   ├── system_prompt_aletheia_v0_1.yaml
│   │   │   ├── reasoning_lenses_v0_1.yaml
│   │   │   └── ethics.yaml
│   │   └── matrix/
│   ├── lenses/
│   └── pipelines/
├── services/                      # Extracted Microservices
│   ├── multiply/
│   └── compute_sum/
├── ui/
│   ├── llm_builder/               # Next.js LLM Builder UI
│   └── dashboard/
│       └── app.py                 # Streamlit Dashboard
├── logs/
│   └── startup_session.log
└── start_ui.bat                   # UI launcher script

## Deprecated/Archived

- canonical_code_platform_port/    # [DEPRECATED]
- control_hub_port/                # [DEPRECATED]

## Notes
- All modules are now referenced from ACP_V1 root.
- Configuration, database, and context paths are unified.
- Legacy modules are archived to prevent confusion.
