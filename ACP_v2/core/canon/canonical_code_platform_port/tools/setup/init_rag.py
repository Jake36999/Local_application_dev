#!/usr/bin/env python
"""
Quick RAG System Initialization

Sets up RAG integration:
1. Enable RAG feature flag
2. Initialize vector database
3. Build initial index
4. Print system status
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_rag():
    """Initialize RAG system."""
    
    print("\n" + "="*60)
    print("  RAG SYSTEM INITIALIZATION")
    print("="*60 + "\n")
    
    # Step 1: Enable RAG in settings
    print("[1/3] Enabling RAG feature flag...")
    try:
        from bus.settings_db import SettingsDB
        sdb = SettingsDB()
        sdb.set_feature_flag('rag_integration_enabled', True, 'RAG integration system')
        print("  [OK] RAG feature flag enabled")
    except Exception as e:
        print(f"  [FAIL] Failed to enable RAG: {e}")
        return False
    
    # Step 2: Initialize vector database
    print("\n[2/3] Initializing RAG vector database...")
    try:
        from rag_engine import get_rag_db
        db = get_rag_db()
        components_before = len(db.get_indexed_components())
        print(f"  [OK] Vector database initialized ({components_before} components)")
    except Exception as e:
        print(f"  [FAIL] Failed to initialize database: {e}")
        return False
    
    # Step 3: Build index from canonical database
    print("\n[3/3] Building RAG index from canonical database...")
    try:
        from rag_engine import get_rag_analyzer
        analyzer = get_rag_analyzer()
        indexed = analyzer.build_index_from_canon_db()
        print(f"  [OK] Indexed {indexed} components")
    except Exception as e:
        print(f"  [FAIL] Failed to build index: {e}")
        return False
    
    # Print status
    print("\n" + "="*60)
    print("  RAG SYSTEM STATUS")
    print("="*60 + "\n")
    
    try:
        from rag_orchestrator import get_rag_orchestrator
        orch = get_rag_orchestrator()
        status = orch.get_status()
        
        print(f"  Status:               {status.get('status', 'UNKNOWN')}")
        print(f"  RAG Enabled:          {status.get('rag_enabled', False)}")
        print(f"  Indexed Components:   {status.get('total_indexed_components', 0)}")
        print(f"  Vector Database:      {status.get('vector_db', 'rag_vectors.db')}")
        print(f"  Timestamp:            {status.get('timestamp', 'N/A')[:19]}")
        
        print("\n[OK] RAG system is ready!")
        print("\nNext steps:")
        print("  1. Start the Streamlit UI: streamlit run ui_app.py")
        print("  2. Navigate to RAG Analysis tab")
        print("  3. Try semantic search or component analysis")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Failed to get status: {e}")
        return False

if __name__ == "__main__":
    success = init_rag()
    
    print("\n" + "="*60 + "\n")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
