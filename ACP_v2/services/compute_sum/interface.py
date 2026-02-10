"""
AUTO-GENERATED SERVICE INTERFACE
Extracted from: compute_sum
Directives: extract, @pure

This is a service boundary definition for potential extraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Compute_sumInterface(ABC):
    """
    Service interface for compute_sum.
    
    Extracted as potential microservice.
    """
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the service logic."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate service state."""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return service health status."""
        pass


# Original source code (for reference):
# def compute_sum(numbers):
#     """Pure compute function - no IO, no globals."""
#     total = 0
#     for n in numbers:
#         total += n
#     return total...
