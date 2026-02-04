#!/usr/bin/env python3
"""
DEPRECATED: Use workflows/workflow_verify.py instead. Will be removed in v3.0.
"""

import sys
from textwrap import dedent
def main() -> None:
    warning = dedent(
        """
        ============================================================
        DEPRECATION WARNING
        ------------------------------------------------------------
        This script is deprecated. Use: python workflows/workflow_verify.py
        See: MIGRATION_GUIDE.md
        This script will be removed in v3.0 (Q4 2026).
        ============================================================
        """
    )
    print(warning)

    response = input("Continue anyway? (y/N): ").strip().lower()
    if response != "y":
        print("Aborted. Use: python workflows/workflow_verify.py")
        sys.exit(0)

    print("Legacy rebuild verification is no longer supported. Use workflow_verify.py.")
    sys.exit(0)


def verify() -> None:
    """Legacy entrypoint maintained for compatibility."""
    main()


if __name__ == "__main__":
    main()
