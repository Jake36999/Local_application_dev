# User Interface Package

Streamlit-based web interface for the Canonical Code Platform.

## Contents

- `ui_app.py` - Main Streamlit dashboard (7-tab interface)

## Features

### Dashboard Tabs

1. **🏠 Dashboard** - System metrics and overview
2. **📊 Analysis** - Component viewer with overlays
3. **🚀 Extraction** - Microservice generation
4. **📈 Drift History** - Version timeline and changes
5. **🎛️ Orchestrator** - Message bus monitoring and control
6. **🤖 RAG Analysis** - Semantic search and AI recommendations
7. **⚙️ Settings** - System configuration and feature flags

## Running the UI

```bash
streamlit run ui/ui_app.py
```

Access at: http://localhost:8501

## Orchestrator Tab

- **Status Metrics**: Orchestrator status, total scans, failed scans
- **Recent Events**: View and expand bus events with JSON payloads
- **Pending Commands**: Monitor queued commands
- **Saved Schemas**: Browse workflow and config schemas
- **Feature Flags**: Toggle RAG and other integrations

## RAG Analysis Tab

- **Semantic Search**: Find components using natural language
- **Component Analysis**: Analyze selected components with AI recommendations
- **Augmented Reports**: Generate enhanced analysis reports
