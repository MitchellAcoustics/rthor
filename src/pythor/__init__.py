"""pythor - Python implementation of RTHOR."""

from ._version import __version__

# Old API (deprecated, will be removed in v1.0.0)
from .api import randall, randall_from_df, randmf, randmf_from_df

# New API (v0.2.0+)
from .api_new import compare_matrices, rthor_test
from .results import ComparisonResult, RTHORResult

__all__ = [
    # Version
    "__version__",
    # New API (recommended)
    "rthor_test",
    "compare_matrices",
    "RTHORResult",
    "ComparisonResult",
    # Old API (deprecated)
    "randall",
    "randall_from_df",
    "randmf",
    "randmf_from_df",
]
