"""
Canonical Code Platform - Enhanced UI
5-tab professional interface with comprehensive features
"""

from typing import Any, Callable, Optional, TYPE_CHECKING, cast, Dict, List
import streamlit as st
import sqlite3
import json
import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))
if str(PROJECT_ROOT) not in sys.path:  # ensure package imports without external PYTHONPATH
    sys.path.insert(0, str(PROJECT_ROOT))

if TYPE_CHECKING:
    from bus.message_bus import MessageBus as MessageBusType
    from bus.settings_db import SettingsDB as SettingsDBType
    from orchestrator.rag_orchestrator import RAGOrchestrator
    from ui.llm_workflow_ui import render_llm_workflow_builder_tab as RenderLLMBuilder

MessageBusCls: Optional[Callable[[], Any]] = None
SettingsDBCls: Optional[Callable[[], Any]] = None
get_rag_orchestrator_fn: Optional[Callable[[], Any]] = None
render_llm_workflow_builder_tab_fn: Optional[Callable[..., Any]] = None

try:
    from bus.message_bus import MessageBus as _MessageBus
    from bus.settings_db import SettingsDB as _SettingsDB
    MessageBusCls = _MessageBus
    SettingsDBCls = _SettingsDB
except Exception:
    MessageBusCls = None
    SettingsDBCls = None

try:
    # Prefer packaged orchestrator module
    from orchestrator.rag_orchestrator import get_rag_orchestrator as _get_rag_orchestrator
    get_rag_orchestrator_fn = _get_rag_orchestrator
except ImportError:
    get_rag_orchestrator_fn = None
except Exception as e:
    print(f"Error importing RAG Orchestrator: {e}")
    get_rag_orchestrator_fn = None

try:
    # Prefer packaged UI module
    from ui.llm_workflow_ui import render_llm_workflow_builder_tab as _render_llm_workflow_builder_tab
    render_llm_workflow_builder_tab_fn = _render_llm_workflow_builder_tab
except ImportError:
    render_llm_workflow_builder_tab_fn = None
except Exception as e:
    print(f"Error importing LLM UI: {e}")
    render_llm_workflow_builder_tab_fn = None

# Page configuration
st.set_page_config(
    page_title="Canonical Code Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with explicit backgrounds to avoid white-out
st.markdown("""
<style>
    :root {
        --bg-primary: #0f172a;
        --bg-card: #111827;
        --text-primary: #e5e7eb;
        --text-muted: #cbd5e1;
        --accent: #3b82f6;
    }
    .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--text-primary);
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--accent);
        margin-bottom: 1rem;
    }
    .phase-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .phase-complete { background: #10B981; color: #0b1220; }
    .phase-partial { background: #F59E0B; color: #0b1220; }
    .phase-pending { background: #EF4444; color: #0b1220; }
    .stMetric {
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 1rem;
        border-radius: 0.5rem;
    }
    pre, code, .stCode, .stTextArea textarea {
        background: #0b1220 !important;
        color: #e5e7eb !important;
    }
    .stAlert {
        color: #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
conn = None
try:
    conn = sqlite3.connect("canon.db", check_same_thread=False)
except sqlite3.Error as e:
    st.error(f"Could not connect to database: canon.db ({str(e)})")
    st.info("Run: python workflows/workflow_ingest.py <file.py>")
    st.stop()

if conn is None:
    st.stop()

# Orchestrator integrations
bus: Optional[Any] = MessageBusCls() if MessageBusCls else None
settings_db: Optional[Any] = SettingsDBCls() if SettingsDBCls else None

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🔍 Navigation")
    
    tab = st.radio(
        "Select View:",
        ["🏠 Dashboard", "📊 Analysis", "🚀 Extraction", "📈 Drift History", "🎛️ Orchestrator", "🤖 RAG Analysis", "🤖 LLM Builder", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📁 Quick Actions")
    ingest_target = st.text_input(
        "Target file or folder to ingest",
        key="ingest_target",
        placeholder="e.g. C:/projects/app.py or /projects/service",
        help="Paste an absolute path; relative paths resolve against the app root."
    )
    if st.button("🚀 Scan / Ingest", use_container_width=True):
        target_raw = ingest_target.strip()
        if not target_raw:
            st.warning("Please provide a file or folder path to ingest.")
        else:
            cleaned = target_raw.strip('"').strip("'")
            target_path = Path(cleaned).expanduser()
            if target_path.drive:
                target_path = target_path.resolve()
            else:
                target_path = (PROJECT_ROOT / target_path).resolve()

            if not target_path.exists():
                st.error(f"Path not found: {target_path}")
            else:
                env = os.environ.copy()
                env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
                env["PYTHONIOENCODING"] = "utf-8"
                files_to_ingest: List[Path] = []
                patterns = ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.json", "*.md", "*.css", "*.html"]
                if target_path.is_dir():
                    collected: set[Path] = set()
                    for pattern in patterns:
                        collected.update(target_path.rglob(pattern))
                    files_to_ingest = sorted(collected)
                    if not files_to_ingest:
                        st.warning("No supported files found (py/ts/js/json/md/css/html).")
                elif target_path.is_file():
                    if any(target_path.match(p) for p in patterns):
                        files_to_ingest = [target_path]
                    else:
                        st.warning("Unsupported file type for ingest.")
                else:
                    st.error("Unsupported path type. Please select a file or folder.")

                if files_to_ingest:
                    progress = st.progress(0)
                    failures: List[tuple[Path, str]] = []
                    total = len(files_to_ingest)

                    for idx, file_path in enumerate(files_to_ingest, start=1):
                        with st.spinner(f"Ingesting: {file_path} ({idx}/{total})"):
                            ingest_proc = subprocess.run(
                                [sys.executable, "workflows/workflow_polyglot.py", str(file_path)],
                                capture_output=True,
                                text=True,
                                env=env,
                                cwd=str(PROJECT_ROOT),
                            )
                        if ingest_proc.returncode != 0:
                            failures.append(
                                (
                                    file_path,
                                    ingest_proc.stderr if ingest_proc.stderr else ingest_proc.stdout,
                                )
                            )
                        progress.progress(int(idx * 100 / total))

                    if failures:
                        st.warning(f"Ingestion completed with {len(failures)} failure(s).")
                        for failed_path, output in failures:
                            st.error(str(failed_path))
                            if output:
                                with st.expander(f"Error log: {failed_path.name}"):
                                    st.code(output, language="text")
                    else:
                        st.success(f"✓ Ingested {len(files_to_ingest)} file(s).")
                        st.rerun()
    
    if st.button("🔄 Re-analyze File", use_container_width=True):
        if conn is not None:
            files = conn.execute("SELECT repo_path FROM canon_files ORDER BY created_at DESC LIMIT 1").fetchone()
            if files:
                env = os.environ.copy()
                env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
                env["PYTHONIOENCODING"] = "utf-8"
                with st.spinner("Re-analyzing last file..."):
                    ingest_proc = subprocess.run(
                        [sys.executable, "workflows/workflow_ingest.py", files[0]],
                        capture_output=True,
                        text=True,
                        env=env,
                        cwd=str(PROJECT_ROOT),
                    )
                    if ingest_proc.returncode == 0:
                        st.success("✓ Re-analysis complete!")
                        st.rerun()
                    else:
                        st.error("Re-analysis failed")
                        st.code(ingest_proc.stderr if ingest_proc.stderr else ingest_proc.stdout)
            else:
                st.warning("No files to re-analyze. Ingest a file first.")
        else:
            st.warning("Database not available")
    
    if st.button("📝 Generate Report", use_container_width=True):
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
        env["PYTHONIOENCODING"] = "utf-8"
        with st.spinner("Generating governance report..."):
            report_proc = subprocess.run(
                [sys.executable, "analysis/governance_report.py"],
                capture_output=True,
                text=True,
                env=env,
                cwd=str(PROJECT_ROOT),
            )
        if report_proc.returncode == 0:
            st.success("✓ Report generated: governance_report.txt")
            if Path("governance_report.txt").exists():
                with open("governance_report.txt", "r") as f:
                    st.text_area("Report Preview", f.read(), height=200)
        else:
            st.error("Report generation failed")
            st.code(report_proc.stderr if report_proc.stderr else report_proc.stdout)
    
    if st.button("✅ Verify System", use_container_width=True):
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{PROJECT_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
        env["PYTHONIOENCODING"] = "utf-8"
        with st.spinner("Verifying system phases..."):
            verify_proc = subprocess.run(
                [sys.executable, "workflows/workflow_verify.py"],
                capture_output=True,
                text=True,
                env=env,
                cwd=str(PROJECT_ROOT),
            )
        if verify_proc.returncode == 0:
            st.success("✓ System verification complete!")
            st.code(verify_proc.stdout, language="text")
        else:
            st.warning("Verification completed with issues")
            st.code(verify_proc.stdout if verify_proc.stdout else verify_proc.stderr, language="text")

# Main header
st.markdown('<div class="main-header">🔍 Canonical Code Platform</div>', unsafe_allow_html=True)

# ===== DASHBOARD TAB =====
if tab == "🏠 Dashboard":
    if conn is not None:
        # System metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            files_count = conn.execute("SELECT COUNT(*) FROM canon_files").fetchone()[0]
            st.metric("Files Ingested", files_count)
        
        with col2:
            components_count = conn.execute("SELECT COUNT(*) FROM canon_components").fetchone()[0]
            st.metric("Components", components_count)
        
        with col3:
            directives_count = conn.execute(
                "SELECT COUNT(*) FROM overlay_semantic WHERE source='comment_directive'"
            ).fetchone()[0]
            st.metric("Directives", directives_count)
        
        with col4:
            errors_count = conn.execute(
                "SELECT COUNT(*) FROM overlay_best_practice WHERE severity='ERROR'"
            ).fetchone()[0]
            st.metric("Blocking Errors", errors_count, delta=-errors_count if errors_count > 0 else None)
        
        st.markdown("---")
        
        # Phase status
        st.markdown("### 📊 Phase Status")
        
        phases = [
            ("Phase 1: Foundation", "complete"),
            ("Phase 2: Symbol Tracking", "complete"),
            ("Phase 3: Call Graph", "complete"),
            ("Phase 4: Semantic Rebuild", "complete"),
            ("Phase 5: Comment Metadata", "complete"),
            ("Phase 6: Drift Detection", "complete"),
            ("Phase 7: Governance", "complete"),
        ]
        
        cols = st.columns(4)
        for idx, (phase, status) in enumerate(phases):
            with cols[idx % 4]:
                badge_class = f"phase-{status}"
                st.markdown(
                    f'<div class="metric-card">'
                    f'<span class="phase-badge {badge_class}">OK</span>'
                    f'<br><strong>{phase}</strong></div>',
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        
        # Recent activity
        st.markdown("### 📜 Recent Activity")
        
        versions = conn.execute("""
            SELECT v.version_number, v.ingested_at, v.change_summary, v.component_count, f.repo_path
            FROM file_versions v
            JOIN canon_files f ON v.file_id = f.file_id
            ORDER BY v.ingested_at DESC
            LIMIT 5
        """).fetchall()
        
        if versions:
            for v_num, ingested_at, change_summary, comp_count, repo_path in versions:
                st.markdown(f"**Version {v_num}** ({ingested_at[:19]}) - {repo_path}")
                st.caption(f"{change_summary} - {comp_count} components")
        else:
            st.info("No activity yet. Run: `python workflows/workflow_ingest.py <file>`")
    else:
        st.warning("Database not available. Please ensure canon.db exists.")

# ===== ANALYSIS TAB =====
elif tab == "📊 Analysis":
    st.markdown("### 📊 Component Analysis")
    
    if conn is not None:
        files = conn.execute("SELECT file_id, repo_path FROM canon_files ORDER BY created_at DESC").fetchall()
        
        if not files:
            st.warning("No files ingested yet.")
            st.info("Run: `python workflows/workflow_ingest.py <file.py>`")
        else:
            file_options = {f[1]: f[0] for f in files}
            selected_file = st.selectbox("Select File:", list(file_options.keys()))
            file_id = file_options[selected_file]
            
            # Component selector
            components = conn.execute("""
                SELECT component_id, qualified_name, kind, name
                FROM canon_components
                WHERE file_id = ?
                ORDER BY order_index
            """, (file_id,)).fetchall()
            
            if not components:
                st.info("No components found in this file.")
            else:
                comp_options = {f"{c[1]} ({c[2]})": c[0] for c in components}
                selected_comp = st.selectbox("Select Component:", list(comp_options.keys()))
                comp_id = comp_options[selected_comp]
                
                # Two-column layout
                left, right = st.columns([1, 1])
                
                with left:
                    st.markdown("#### 📝 Source Code")
                    source = conn.execute("""
                        SELECT source_text FROM canon_source_segments
                        WHERE component_id = ?
                    """, (comp_id,)).fetchone()
                    
                    if source:
                        st.code(source[0], language="python")
                    else:
                        st.info("No source code found")
                
                with right:
                    st.markdown("#### 🎯 Advisory Overlays")
                    
                    # Comment directives
                    directives = conn.execute("""
                        SELECT json_extract(payload_json, '$.directive')
                        FROM overlay_semantic
                        WHERE target_id = ? AND source = 'comment_directive'
                    """, (comp_id,)).fetchall()
                    
                    if directives:
                        st.markdown("**📝 Directives:**")
                        for (d,) in directives:
                            st.markdown(f"- `@{d}`")
                    
                    # Cut analysis score
                    cut_score = conn.execute("""
                        SELECT payload_json FROM overlay_semantic
                        WHERE target_id = ? AND source = 'cut_analyzer'
                    """, (comp_id,)).fetchone()
                    
                    if cut_score:
                        try:
                            data = json.loads(cut_score[0])
                            st.markdown("**📊 Extraction Score:**")
                            score = data.get('score', 0)
                            tier = data.get('tier', 'Unknown')
                            st.metric("Score", f"{score:.2f}")
                            st.caption(f"Tier: {tier}")
                        except:
                            pass
                    
                    # Governance violations
                    violations = conn.execute("""
                        SELECT rule_id, severity, message
                        FROM overlay_best_practice
                        WHERE component_id = ?
                    """, (comp_id,)).fetchall()
                    
                    if violations:
                        st.markdown("**🚩 Governance Issues:**")
                        for rule, severity, msg in violations:
                            if severity == "ERROR":
                                st.error(f"**{rule}**: {msg}")
                            elif severity in ("WARN", "WARNING"):
                                st.warning(f"**{rule}**: {msg}")
                            else:
                                st.info(f"**{rule}**: {msg}")
    else:
        st.warning("Database not available. Please ensure canon.db exists.")

# ===== EXTRACTION TAB =====
elif tab == "🚀 Extraction":
    st.markdown("### 🚀 Microservice Extraction")
    
    if conn is not None:
        # Gate status
        st.markdown("#### 🚦 Extraction Gate Status")
        
        gate_checks = [
            ("Comment Directives", "SELECT COUNT(*) FROM overlay_semantic WHERE source='comment_directive'"),
            ("Extraction Scores", "SELECT COUNT(*) FROM overlay_semantic WHERE source='cut_analyzer'"),
            ("Governance Rules", "SELECT COUNT(*) FROM overlay_best_practice"),
        ]
        
        cols = st.columns(3)
        for idx, (check_name, query) in enumerate(gate_checks):
            with cols[idx]:
                count = conn.execute(query).fetchone()[0]
                st.metric(check_name, str(count), delta="✓" if count > 0 else None)
    else:
        st.warning("Database not available. Please ensure canon.db exists.")

# ===== DRIFT HISTORY TAB =====
elif tab == "📈 Drift History":
    st.markdown("### 📈 Component Drift History")
    
    if conn is not None:
        files = conn.execute("SELECT file_id, repo_path FROM canon_files ORDER BY created_at DESC").fetchall()
        
        if not files:
            st.warning("No files ingested yet.")
        else:
            file_options = {f[1]: f[0] for f in files}
            selected_file = st.selectbox("Select File:", list(file_options.keys()), key="drift_file")
            file_id = file_options[selected_file]
            
            # Get version history
            versions = conn.execute("""
                SELECT version_number, component_count, change_summary, ingested_at
                FROM file_versions
                WHERE file_id = ?
                ORDER BY version_number
            """, (file_id,)).fetchall()
            
            if not versions:
                st.info("No version history for this file.")
            else:
                st.markdown("#### 📅 Version Timeline")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Versions", len(versions))
                
                with col2:
                    total_components = sum(v[1] for v in versions)
                    st.metric("Total Components", total_components)
                
                with col3:
                    drift_count = conn.execute("""
                        SELECT COUNT(*) FROM drift_events 
                        WHERE component_id IN (
                            SELECT component_id FROM canon_components WHERE file_id = ?
                        )
                    """, (file_id,)).fetchone()[0]
                    st.metric("Drift Events", drift_count)
                
                st.markdown("---")
                
                # Version details
                for v_num, comp_count, change_summary, ingested_at in versions:
                    with st.expander(f"Version {v_num}: {change_summary} ({ingested_at[:19]})"):
                        st.markdown(f"**Components:** {comp_count}")
                        
                        # Get component history for this version
                        version_id = conn.execute("""
                            SELECT version_id FROM file_versions 
                            WHERE file_id = ? AND version_number = ?
                        """, (file_id, v_num)).fetchone()
                        
                        if version_id:
                            history = conn.execute("""
                                SELECT drift_type, COUNT(*) as count
                                FROM component_history
                                WHERE file_version_id = ?
                                GROUP BY drift_type
                            """, (version_id[0],)).fetchall()
                            
                            if history:
                                cols = st.columns(len(history))
                                for idx, (drift_type, count) in enumerate(history):
                                    with cols[idx]:
                                        if drift_type == "ADDED":
                                            st.success(f"✅ {count} Added")
                                        elif drift_type == "REMOVED":
                                            st.error(f"❌ {count} Removed")
                                        elif drift_type == "MODIFIED":
                                            st.warning(f"⚠️ {count} Modified")
                                        else:
                                            st.info(f"ℹ️ {count} {drift_type}")
    else:
        st.warning("Database not available. Please ensure canon.db exists.")

# ===== ORCHESTRATOR TAB =====
elif tab == "🎛️ Orchestrator":
    st.markdown("### 🎛️ Orchestrator Control Panel")

    if not bus:
        st.warning("Message bus not available. Ensure bus/message_bus.py exists.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", bus.get_state("orchestrator_status") or "IDLE")
        with col2:
            st.metric("Total Scans", bus.get_state("total_scans") or 0)
        with col3:
            st.metric("Failed Scans", bus.get_state("failed_scans") or 0)

        st.markdown("---")

        st.markdown("#### 📋 Recent Events")
        events = bus.get_events(limit=20)
        if events:
            for event in events:
                with st.expander(f"[{event['event_type']}] {event['timestamp'][:19]}"):
                    try:
                        st.json(json.loads(event["payload_json"]))
                    except Exception:
                        st.write(event["payload_json"])
        else:
            st.info("No events yet.")

        st.markdown("---")

        st.markdown("#### ⏳ Pending Commands")
        commands = bus.get_pending_commands()
        if commands:
            for cmd in commands:
                st.info(f"{cmd['command_type']} → {cmd['target']} (ID: {cmd['command_id'][:8]})")
        else:
            st.success("No pending commands")

        st.markdown("---")

        st.markdown("#### 💾 Saved Schemas")
        schemas = bus.list_schemas()
        if schemas:
            for schema in schemas[:10]:
                st.write(f"**{schema['schema_name']}** ({schema['schema_type']}) - {schema['created_at'][:19]}")
        else:
            st.info("No schemas saved yet.")

# ===== RAG ANALYSIS TAB =====
elif tab == "🤖 RAG Analysis":
    if not conn:
        st.error("Database connection unavailable. Restart the app after ingesting data.")
        st.stop()

    st.markdown("### 🤖 RAG - Retrieval-Augmented Generation")
    
    if not get_rag_orchestrator_fn:
        st.warning("RAG module not available. Ensure rag_orchestrator.py exists.")
    else:
        rag_orch: Any = get_rag_orchestrator_fn()
        
        # Check if RAG is enabled
        st.markdown("#### ⚙️ RAG Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            status_info: Dict[str, Any] = cast(Dict[str, Any], rag_orch.get_status())
            st.metric("RAG Status", status_info.get('status', 'UNKNOWN'))
        
        with col2:
            st.metric("Indexed Components", status_info.get('total_indexed_components', 0))
        
        st.markdown("---")
        
        # RAG Operations
        st.markdown("#### 🔍 Semantic Search")
        
        search_query = st.text_input("Search for components:", placeholder="e.g., 'function', 'class', 'error'")
        
        if search_query:
            with st.spinner("Searching..."):
                search_results: List[Dict[str, Any]] = cast(List[Dict[str, Any]], rag_orch.search_components(search_query, top_k=5))
                
                if search_results:
                    st.success(f"Found {len(search_results)} results")
                    
                    for i, item in enumerate(search_results, 1):
                        with st.expander(f"{i}. {item['component_name']} (score: {item['similarity_score']:.2f})"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**ID:** `{item['component_id'][:12]}...`")
                                st.write(f"**Relationships:** {len(item.get('relationships', []))}")
                            
                            with col2:
                                if item['context']:
                                    st.text_area("Context", item['context'], height=100, disabled=True)
                else:
                    st.info("No components found matching query")
        
        st.markdown("---")
        
        st.markdown("#### 📊 Component Analysis")
        
        # Get available components
        files = conn.execute("SELECT file_id, repo_path FROM canon_files ORDER BY created_at DESC").fetchall()
        
        if files:
            file_options = {f[1]: f[0] for f in files}
            selected_file = st.selectbox("Select File:", list(file_options.keys()), key="rag_file")
            file_id = file_options[selected_file]
            
            # Get components for this file
            components = conn.execute("""
                SELECT component_id, name, type FROM canon_components
                WHERE file_id = ? ORDER BY name
            """, (file_id,)).fetchall()
            
            if components:
                comp_options = {f"{c[1]} ({c[2]})": c[0] for c in components}
                selected_comp = st.selectbox("Select Component:", list(comp_options.keys()), key="rag_component")
                component_id = comp_options[selected_comp]
                
                if st.button("🔬 Analyze Component", use_container_width=True):
                    with st.spinner("Analyzing component..."):
                        analysis = rag_orch.analyze_component(component_id)
                        
                        if analysis:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Type", analysis.get('component_type', 'N/A'))
                                st.metric("Relationships", analysis.get('direct_relationships', 0))
                            
                            with col2:
                                st.metric("Documentation", "Yes" if analysis.get('documentation_available') else "No")
                            
                            st.markdown("---")
                            
                            # Recommendations
                            if analysis.get('recommendations'):
                                st.markdown("**AI-Generated Recommendations:**")
                                for rec in analysis['recommendations']:
                                    st.info(rec)
                            
                            # Augmentation
                            if analysis.get('augmentation'):
                                st.markdown("**Augmented Context:**")
                                st.text(analysis['augmentation'])
                        else:
                            st.warning("No analysis available for this component")
            else:
                st.info("No components found for this file")
        else:
            st.info("No files ingested yet. Run ingestion first.")
        
        st.markdown("---")
        
        st.markdown("#### 📈 RAG Reports")
        
        if st.button("📊 Generate Augmented Report", use_container_width=True):
            files = conn.execute("SELECT file_id FROM canon_files ORDER BY created_at DESC LIMIT 1").fetchone()
            
            if files:
                with st.spinner("Generating report..."):
                    report = rag_orch.get_augmented_report(files[0])
                    
                    if report:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Components", report.get('total_components', 0))
                        with col2:
                            st.metric("Analyzed", report.get('analyzed_components', 0))
                        
                        st.success("✓ Report generated")
                        
                        # Show component analyses
                        for analysis in report.get('component_analyses', [])[:5]:
                            with st.expander(f"Component: {analysis.get('component_name')}"):
                                st.json(analysis)
                    else:
                        st.warning("Failed to generate report")
            else:
                st.warning("No files to analyze")

# ===== LLM WORKFLOW BUILDER TAB =====
elif tab == "🤖 LLM Builder":
    if not render_llm_workflow_builder_tab_fn:
        st.error("LLM Workflow Builder module not available. Ensure llm_workflow_ui.py exists.")
    else:
        try:
            render_llm_workflow_builder_tab_fn()
        except Exception as e:
            st.error(f"Failed to render LLM builder: {str(e)}")
            st.info("Please ensure:")
            st.code("""
- LM Studio running at http://192.168.0.190:1234
- All required modules installed (requests, pyyaml)
- workflows/ directory exists
            """, language="bash")

# ===== SETTINGS TAB =====
elif tab == "⚙️ Settings":
    if not conn:
        st.error("Database connection unavailable. Restart the app after ingesting data.")
        st.stop()

    st.markdown("### ⚙️ System Settings")
    
    # Database stats
    st.markdown("#### 📊 Database Statistics")
    
    tables = [
        "canon_files",
        "canon_components",
        "canon_source_segments",
        "overlay_semantic",
        "overlay_best_practice",
        "file_versions",
        "component_history",
        "drift_events"
    ]
    
    col1, col2 = st.columns(2)
    for idx, table in enumerate(tables):
        with col1 if idx % 2 == 0 else col2:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                st.metric(table, count)
            except:
                st.metric(table, "N/A")
    
    st.markdown("---")

    st.markdown("#### ⚙️ Runtime Settings")
    if not settings_db:
        st.warning("Settings database not available. Ensure bus/settings_db.py exists.")
    else:
        settings = settings_db.get_all_settings()

        with st.expander("User Settings", expanded=False):
            for key, value in settings.items():
                new_val: Any = value
                if isinstance(value, bool):
                    new_val = st.checkbox(key, value=value, key=f"setting_{key}")
                elif isinstance(value, int):
                    new_val = st.number_input(key, value=value, step=1, key=f"setting_{key}")
                elif isinstance(value, float):
                    new_val = st.number_input(key, value=value, format="%.3f", key=f"setting_{key}")
                else:
                    new_val = st.text_input(key, value=str(value), key=f"setting_{key}")

                if new_val != value:
                    settings_db.set_setting(key, new_val)
                    st.success(f"Updated {key}")
                    st.rerun()

        with st.expander("Feature Flags", expanded=False):
            flags = settings_db.get_all_flags()
            if not flags:
                st.info("No feature flags yet.")
            else:
                for flag_name, enabled in flags.items():
                    new_enabled = st.checkbox(flag_name, value=enabled, key=f"flag_{flag_name}")
                    if new_enabled != enabled:
                        settings_db.set_feature_flag(flag_name, new_enabled)
                        st.success(f"Updated {flag_name}")
                        st.rerun()
    
    st.markdown("---")
    
    # Workflow commands
    st.markdown("#### 🔄 Workflow Commands")
    
    st.code("""
# Ingest a file
python workflows/workflow_ingest.py myfile.py

# Extract microservices
python workflows/workflow_extract.py

# Verify system
python workflows/workflow_verify.py

# Start orchestrator + UI
start_orchestrator.bat

# Launch UI
streamlit run ui_app.py
    """, language="bash")
    
    st.markdown("---")
    
    # Documentation links
    st.markdown("#### 📚 Documentation")
    
    docs = [
        ("QUICKSTART.md", "5-minute tutorial"),
        ("WORKFLOWS.md", "Complete workflow reference"),
        ("ARCHITECTURE.md", "System design & data model"),
        ("MIGRATION_GUIDE.md", "Transition from old scripts"),
        ("VERIFICATION_PLAN.md", "Testing & validation"),
    ]
    
    for doc, desc in docs:
        st.markdown(f"- **{doc}** - {desc}")

# Close connection on exit
if conn:
    conn.close()
