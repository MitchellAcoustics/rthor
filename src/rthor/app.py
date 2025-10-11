from enum import StrEnum  # noqa: D100

import fiatlight as fl
import pandas as pd
from fiatlight.fiat_types import TextPath

from rthor import RTHORResult, rthor_test


class _Order(StrEnum):
    CIRC6 = "circular6"
    CIRC8 = "circular8"


def from_file(  # noqa: D103
    filepath: TextPath,
    order: _Order = _Order.CIRC6,
    n_matrices: int = 3,
    n_variables: int = 6,
) -> tuple[str, str, int, int]:
    return filepath, order.value, n_matrices, n_variables


def get_results(rthor_result: RTHORResult) -> pd.DataFrame:  # noqa: D103
    return rthor_result.results


def main() -> None:  # noqa: D103
    graph = fl.FunctionsGraph.from_function_composition(
        [from_file, rthor_test, get_results]
    )
    graph.add_link("from_file", "rthor_test", "order", 1)
    graph.add_link("from_file", "rthor_test", "n_matrices", 2)
    graph.add_link("from_file", "rthor_test", "n_variables", 3)

    fl.register_dataclass(RTHORResult)

    fl.run(graph, app_name="rthor")
