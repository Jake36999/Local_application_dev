#!/usr/bin/env python3
"""
Compatibility shim for ingestion workflow.
Delegates to workflows.workflow_ingest.main so legacy callers keep working.
"""
import sys
from workflows.workflow_ingest import main

if __name__ == "__main__":
    sys.exit(main())
