"""
Deprecated test orchestrator. The canonical tests now live under tests/.
This module remains only to avoid import errors in legacy tooling.
"""

import pytest

pytest.skip(
    "Deprecated legacy suite; use tests/ instead.", allow_module_level=True
)