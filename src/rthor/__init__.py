"""rthor - Python implementation of RTHOR."""

from ._version import __version__
from .api import compare_matrices, rthor_test
from .formatting import print_comparison, print_results

__all__ = [
    "__version__",
    "compare_matrices",
    "print_comparison",
    "print_results",
    "rthor_test",
]
