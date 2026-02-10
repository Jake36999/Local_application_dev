"""
Deprecated legacy entrypoint.
Use: python workflows/workflow_ingest.py
"""

from pathlib import Path
import sys


def main() -> int:
    target = Path(__file__).parent / "workflow_ingest.py"
    print("[DEPRECATED] Use: python workflows/workflow_ingest.py")
    sys.argv = [str(target), *sys.argv[1:]]

    try:
        from workflows.workflow_ingest import main as workflow_main
    except ImportError as exc:
        print(f"[ERROR] Failed to import workflows workflow: {exc}")
        return 1

    return workflow_main() or 0


if __name__ == "__main__":
    raise SystemExit(main())
