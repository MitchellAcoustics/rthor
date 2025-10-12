"""Formatting utilities for displaying RTHOR results."""

from __future__ import annotations

import pandas as pd

from rthor._utils import is_installed, requires


def print_results(results: pd.DataFrame, *, use_rich: bool = True) -> None:
    """Print RTHOR test results in a formatted table.

    Args:
        results: DataFrame from rthor_test() containing test results
        use_rich: If True and rich is installed, use rich formatting.
            If False or rich not available, use plain text.

    Examples:
        >>> import rthor
        >>> from rthor.formatting import print_results
        >>> df = rthor.rthor_test(data, order="circular6")
        >>> print_results(df)

    """
    if use_rich and is_installed("rich"):
        _print_results_rich(results)
    else:
        _print_results_plain(results)


def print_comparison(
    individual: pd.DataFrame,
    pairwise: pd.DataFrame,
    *,
    use_rich: bool = True,
) -> None:
    """Print comparison results in formatted tables.

    Args:
        individual: DataFrame with individual matrix results
        pairwise: DataFrame with pairwise comparison results
        use_rich: If True and rich is installed, use rich formatting.
            If False or rich not available, use plain text.

    Examples:
        >>> import rthor
        >>> from rthor.formatting import print_comparison
        >>> individual, pairwise = rthor.compare_matrices(data, order="circular6")
        >>> print_comparison(individual, pairwise)

    """
    if use_rich and is_installed("rich"):
        _print_comparison_rich(individual, pairwise)
    else:
        _print_comparison_plain(individual, pairwise)


def _print_results_plain(results: pd.DataFrame) -> None:
    """Generate plain text summary of RTHOR results."""
    # Extract metadata from first row
    n_perms = int(results["n_permutations"].iloc[0])
    n_vars = int(results["n_variables"].iloc[0])
    n_mats = len(results)
    n_preds = int(results["predictions"].iloc[0])

    lines = [
        "RTHOR Analysis Summary",
        "=" * 50,
        f"Matrices analyzed: {n_mats}",
        f"Variables per matrix: {n_vars}",
        f"Hypothesized predictions: {n_preds}",
        f"Permutations tested: {n_perms}",
        "",
        "Results:",
        "-" * 50,
    ]

    # Add key statistics
    for _, row in results.iterrows():
        label = row["label"] if row["label"] else f"Matrix {row['matrix']}"
        ci = row["ci"]
        p_val = row["p_value"]
        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else ""
        )
        lines.append(f"{label:30s} CI={ci:7.4f}  p={p_val:.4f} {sig}")

    lines.extend(
        [
            "",
            "Significance codes: *** p<0.001, ** p<0.01, * p<0.05",
        ]
    )

    print("\n".join(lines))


def _print_results_rich(results: pd.DataFrame) -> None:
    """Create and print a rich table displaying RTHOR results."""
    requires("rich", reason="use_rich=True", extras="rich")
    import rich.box  # noqa: PLC0415
    import rich.table  # noqa: PLC0415
    from rich.console import Console  # noqa: PLC0415

    # Extract metadata
    n_perms = int(results["n_permutations"].iloc[0])
    n_vars = int(results["n_variables"].iloc[0])
    n_mats = len(results)
    n_preds = int(results["predictions"].iloc[0])

    # Create metadata table
    meta_table = rich.table.Table(
        title="RTHOR Analysis Results",
        box=rich.box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold magenta",
    )
    meta_table.add_column("Metric", style="dim")
    meta_table.add_column("Value", style="bold cyan")
    meta_table.add_row("Matrices analyzed", str(n_mats))
    meta_table.add_row("Variables per matrix", str(n_vars))
    meta_table.add_row("Hypothesized predictions", str(n_preds))
    meta_table.add_row("Permutations tested", str(n_perms))

    # Create results table
    results_table = rich.table.Table(
        title="Individual Matrix Results",
        box=rich.box.SIMPLE,
        show_header=True,
        header_style="bold yellow",
    )

    results_table.add_column("Matrix", justify="right", style="cyan")
    results_table.add_column("Label", style="white")
    results_table.add_column("CI", justify="right", style="green")
    results_table.add_column("p-value", justify="right", style="yellow")
    results_table.add_column("Sig.", justify="center", style="bold red")
    results_table.add_column("Predictions", justify="right", style="dim")
    results_table.add_column("Agreements", justify="right", style="dim")

    # Add rows for each matrix
    for _, row in results.iterrows():
        label = row["label"] if row["label"] else f"Matrix {row['matrix']}"
        ci = row["ci"]
        p_val = row["p_value"]

        # Determine significance
        if p_val < 0.001:
            sig = "***"
            sig_style = "bold red"
        elif p_val < 0.01:
            sig = "**"
            sig_style = "bold yellow"
        elif p_val < 0.05:
            sig = "*"
            sig_style = "bold"
        else:
            sig = ""
            sig_style = "dim"

        results_table.add_row(
            str(row["matrix"]),
            label,
            f"{ci:.4f}",
            f"{p_val:.4f}",
            f"[{sig_style}]{sig}[/]",
            str(row["predictions"]),
            str(row["agreements"]),
        )

    results_table.caption = "Significance codes: *** p<0.001, ** p<0.01, * p<0.05"
    results_table.caption_style = "dim italic"

    console = Console()
    console.print(meta_table)
    console.print()
    console.print(results_table)


def _print_comparison_plain(individual: pd.DataFrame, pairwise: pd.DataFrame) -> None:
    """Generate plain text summary of comparison results."""
    # Extract metadata
    n_perms = int(individual["n_permutations"].iloc[0])
    n_vars = int(individual["n_variables"].iloc[0])
    n_mats = len(individual)
    n_preds = int(individual["predictions"].iloc[0])

    lines = [
        "Matrix Comparison Analysis Summary",
        "=" * 60,
        f"Matrices analyzed: {n_mats}",
        f"Variables per matrix: {n_vars}",
        f"Hypothesized predictions: {n_preds}",
        f"Permutations tested: {n_perms}",
        "",
        "Individual Matrix Results:",
        "-" * 60,
    ]

    # Individual results
    for _, row in individual.iterrows():
        mat_id = row["matrix"]
        ci = row["ci"]
        p_val = row["p_value"]
        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else ""
        )
        lines.append(f"Matrix {mat_id:2d}  CI={ci:7.4f}  p={p_val:.4f} {sig}")

    lines.extend(
        [
            "",
            "Pairwise Comparisons:",
            "-" * 60,
        ]
    )

    # Pairwise comparisons
    for _, row in pairwise.iterrows():
        m1 = int(row["matrix1"])
        m2 = int(row["matrix2"])
        ci = row["ci"]
        p_val = row["p_value"]
        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else ""
        )
        lines.append(f"Matrix {m1} vs {m2}  CI={ci:7.4f}  p={p_val:.4f} {sig}")

    lines.extend(
        [
            "",
            "Significance codes: *** p<0.001, ** p<0.01, * p<0.05",
        ]
    )

    print("\n".join(lines))


def _print_comparison_rich(individual: pd.DataFrame, pairwise: pd.DataFrame) -> None:
    """Create and print rich tables for comparison results."""
    requires("rich", reason="use_rich=True", extras="rich")
    import rich.box  # noqa: PLC0415
    import rich.table  # noqa: PLC0415
    from rich.console import Console  # noqa: PLC0415

    # Extract metadata
    n_perms = int(individual["n_permutations"].iloc[0])
    n_vars = int(individual["n_variables"].iloc[0])
    n_mats = len(individual)
    n_preds = int(individual["predictions"].iloc[0])

    # Create metadata table
    meta_table = rich.table.Table(
        title="Matrix Comparison Analysis",
        box=rich.box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold magenta",
    )
    meta_table.add_column("Metric", style="dim")
    meta_table.add_column("Value", style="bold cyan")
    meta_table.add_row("Matrices analyzed", str(n_mats))
    meta_table.add_row("Variables per matrix", str(n_vars))
    meta_table.add_row("Hypothesized predictions", str(n_preds))
    meta_table.add_row("Permutations tested", str(n_perms))

    # Create individual results table
    individual_table = rich.table.Table(
        title="Individual Matrix Results",
        box=rich.box.SIMPLE,
        show_header=True,
        header_style="bold yellow",
    )
    individual_table.add_column("Matrix", justify="right", style="cyan")
    individual_table.add_column("CI", justify="right", style="green")
    individual_table.add_column("p-value", justify="right", style="yellow")
    individual_table.add_column("Sig.", justify="center", style="bold red")
    individual_table.add_column("Predictions", justify="right", style="dim")
    individual_table.add_column("Agreements", justify="right", style="dim")

    for _, row in individual.iterrows():
        sig, sig_style = _get_significance(row["p_value"])
        individual_table.add_row(
            str(row["matrix"]),
            f"{row['ci']:.4f}",
            f"{row['p_value']:.4f}",
            f"[{sig_style}]{sig}[/]",
            str(row["predictions"]),
            str(row["agreements"]),
        )

    individual_table.caption = "Significance codes: *** p<0.001, ** p<0.01, * p<0.05"
    individual_table.caption_style = "dim italic"

    # Create pairwise comparison table
    pairwise_table = rich.table.Table(
        title="Pairwise Comparisons",
        box=rich.box.SIMPLE,
        show_header=True,
        header_style="bold yellow",
    )
    pairwise_table.add_column("Matrix 1", justify="right", style="cyan")
    pairwise_table.add_column("Matrix 2", justify="right", style="cyan")
    pairwise_table.add_column("Both", justify="right", style="dim")
    pairwise_table.add_column("Only 1", justify="right", style="dim")
    pairwise_table.add_column("Only 2", justify="right", style="dim")
    pairwise_table.add_column("Neither", justify="right", style="dim")
    pairwise_table.add_column("CI", justify="right", style="green")
    pairwise_table.add_column("p-value", justify="right", style="yellow")
    pairwise_table.add_column("Sig.", justify="center", style="bold red")

    for _, row in pairwise.iterrows():
        sig, sig_style = _get_significance(row["p_value"])
        pairwise_table.add_row(
            str(int(row["matrix1"])),
            str(int(row["matrix2"])),
            str(row["both_agree"]),
            str(row["only1"]),
            str(row["only2"]),
            str(row["neither"]),
            f"{row['ci']:.4f}",
            f"{row['p_value']:.4f}",
            f"[{sig_style}]{sig}[/]",
        )

    pairwise_table.caption = "Significance codes: *** p<0.001, ** p<0.01, * p<0.05"
    pairwise_table.caption_style = "dim italic"

    console = Console()
    console.print(meta_table)
    console.print()
    console.print(individual_table)
    console.print()
    console.print(pairwise_table)


def _get_significance(p_value: float) -> tuple[str, str]:
    """Get significance symbol and style based on p-value."""
    if p_value < 0.001:
        return "***", "bold red"
    if p_value < 0.01:
        return "**", "bold yellow"
    if p_value < 0.05:
        return "*", "bold"
    return "", "dim"
