"""
Canonical Code Platform - Enhanced UI
5-tab professional interface with comprehensive features
"""

import streamlit as st
import sqlite3
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Canonical Code Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem 0;
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
    .phase-complete { background: #10B981; color: white; }
    .phase-partial { background: #F59E0B; color: white; }
    .phase-pending { background: #EF4444; color: white; }
    .metric-card {
        background: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .stMetric {
        background: #F9FAFB;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
try:
    conn = sqlite3.connect("canon.db", check_same_thread=False)
except sqlite3.Error:
    st.error("Could not connect to database: canon.db")
    st.info("Run: python workflow_ingest.py <file.py>")
    st.stop()

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🔍 Navigation")
    
    tab = st.radio(
        "Select View:",
        ["🏠 Dashboard", "📊 Analysis", "🚀 Extraction", "📈 Drift History", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📁 Quick Actions")
    
    if st.button("🔄 Re-analyze File", use_container_width=True):
        st.info("Run: `python workflow_ingest.py <file>`")
    
    if st.button("📝 Generate Report", use_container_width=True):
        st.info("Run: `python governance_report.py`")
    
    if st.button("✅ Verify System", use_container_width=True):
        st.info("Run: `python workflow_verify.py`")

# Main header
st.markdown('<div class="main-header">🔍 Canonical Code Platform</div>', unsafe_allow_html=True)

# ===== DASHBOARD TAB =====
if tab == "🏠 Dashboard":
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
        st.info("No activity yet. Run: `python workflow_ingest.py <file>`")

# ===== ANALYSIS TAB =====
elif tab == "📊 Analysis":
    st.markdown("### 📊 Component Analysis")
    
    # File selector
    files = conn.execute("SELECT file_id, repo_path FROM canon_files ORDER BY created_at DESC").fetchall()
    
    if not files:
        st.warning("No files ingested yet.")
        st.info("Run: `python workflow_ingest.py <file.py>`")
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
                    st.error(msg)
                elif severity == 'WARN':
                    st.warning(msg)
                else:
                    st.info(msg)

# ===== TAB 2: DRIFT HISTORY =====
with tab2:
    st.header("📊 Version History & Drift Detection")
    
    # Select file for drift view
    f_drift = st.selectbox("Select File to View Drift", files, format_func=lambda x: x[1], key="drift_file")
    
    # Get version history
    versions = conn.execute("""
        SELECT version_number, component_count, change_summary, ingested_at
        FROM file_versions
        WHERE file_id=?
        ORDER BY version_number
    """, (f_drift[0],)).fetchall()
    
    if not versions:
        st.info("No version history for this file.")
    else:
        st.subheader("📅 Version Timeline")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Versions", len(versions))
        with col2:
            total_components = sum(v[1] for v in versions)
            st.metric("Total Components (all versions)", total_components)
        with col3:
            # Count drift events
            drift_count = conn.execute("""
                SELECT COUNT(*) FROM drift_events 
                WHERE component_id IN (
                    SELECT component_id FROM canon_components WHERE file_id=?
                )
            """, (f_drift[0],)).fetchone()[0]
            st.metric("Semantic Drift Events", drift_count)
        
        st.divider()
        
        # Version details
        for v_num, comp_count, change_summary, ingested_at in versions:
            with st.expander(f"Version {v_num}: {comp_count} components ({change_summary}) - {ingested_at[:19]}"):
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.subheader("Component History")
                    history = conn.execute("""
                        SELECT drift_type, COUNT(*) as count
                        FROM component_history
                        WHERE file_version_id IN (
                            SELECT version_id FROM file_versions 
                            WHERE file_id=? AND version_number=?
                        )
                        GROUP BY drift_type
                    """, (f_drift[0], v_num)).fetchall()
                    
                    if history:
                        for drift_type, count in history:
                            if drift_type == "ADDED":
                                st.success(f"✅ {count} Added")
                            elif drift_type == "REMOVED":
                                st.error(f"❌ {count} Removed")
                            elif drift_type == "MODIFIED":
                                st.warning(f"⚠️ {count} Modified")
                            else:
                                st.info(f"ℹ️ {count} {drift_type}")
                
                with col_right:
                    st.subheader("Semantic Drift Details")
                    
                    # Get component IDs for this version
                    version_id = conn.execute(
                        "SELECT version_id FROM file_versions WHERE file_id=? AND version_number=?",
                        (f_drift[0], v_num)
                    ).fetchone()
                    
                    if version_id:
                        # Get components from history
                        comps_in_version = conn.execute("""
                            SELECT DISTINCT component_id FROM component_history
                            WHERE file_version_id=?
                        """, (version_id[0],)).fetchall()
                        
                        comp_ids = [c[0] for c in comps_in_version if c[0]]
                        
                        if comp_ids:
                            drifts = conn.execute(f"""
                                SELECT drift_category, COUNT(*) as count, severity
                                FROM drift_events
                                WHERE component_id IN ({','.join('?' * len(comp_ids))})
                                GROUP BY drift_category
                                ORDER BY severity DESC
                            """, comp_ids).fetchall()
                            
                            if drifts:
                                for category, count, severity in drifts:
                                    icon = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
                                    st.markdown(f"{icon} **{category}**: {count}")
                            else:
                                st.info("No semantic drift in this version")
        
        # Summary of all changes
        st.divider()
        st.subheader("📈 Overall Change Summary")
        
        total_added = conn.execute("""
            SELECT COUNT(*) FROM component_history 
            WHERE file_id=? AND drift_type='ADDED'
        """, (f_drift[0],)).fetchone()[0]
        
        total_removed = conn.execute("""
            SELECT COUNT(*) FROM component_history 
            WHERE file_id=? AND drift_type='REMOVED'
        """, (f_drift[0],)).fetchone()[0]
        
        total_modified = conn.execute("""
            SELECT COUNT(*) FROM component_history 
            WHERE file_id=? AND drift_type='MODIFIED'
        """, (f_drift[0],)).fetchone()[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Components Added", total_added)
        with col2:
            st.metric("Components Removed", total_removed)
        with col3:
            st.metric("Components Modified", total_modified)
