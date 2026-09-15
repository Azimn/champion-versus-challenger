"""Research harness for architecture-neutral Champion versus Challenger experiments."""

from .state import validate_research_state
from .trace import TraceValidationError, validate_trace_file, validate_trace_records

__all__ = [
    "TraceValidationError",
    "validate_research_state",
    "validate_trace_file",
    "validate_trace_records",
]
