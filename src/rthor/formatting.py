"""Compact formatting utilities for displaying RTHOR results."""

from __future__ import annotations

import pandas as pd

from rthor._utils import is_installed, requires


def print_results(results: pd.DataFrame, *, use_rich: bool = True) -> None:
    """Print RTHOR test results in a compact, interpretable format."""
    if use_rich and is_installed("rich"):
        _print_results_rich(results)
    else:
        _print_results_plain(results)


def _interpret_ci(ci: float) -> tuple[str, str, str]:
    """Interpret CI value and return (interpretation, quality, symbol)."""
    if ci >= 0.7:
        return "Excellent fit", "excellent", "✓"
    if ci >= 0.5:
        return "Good fit", "good", "↗"
    if ci >= 0.3:
        return "Moderate fit", "moderate", "→"
    if ci >= 0.1:
        return "Weak fit", "weak", "↘"
    if ci >= 0:
        return "Minimal fit", "minimal", "⚠"
    return "Poor fit", "poor", "✗"


def _print_results_plain(results: pd.DataFrame) -> None:
    """Generate concise plain text output of RTHOR results."""
    n_mats = len(results)
    n_vars = int(results["n_variables"].iloc[0])
    n_preds = int(results["predictions"].iloc[0])
    n_perms = int(results["n_permutations"].iloc[0])

    print("=" * 70)  # noqa: T201
    print("RTHOR TEST RESULTS")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print(  # noqa: T201
        f"{n_mats} {'matrix' if n_mats == 1 else 'matrices'} • {n_vars} variables • {n_preds} predictions • {n_perms:,} permutations"
    )
    print()  # noqa: T201

    # Results for each matrix
    for idx, (_, row) in enumerate(results.iterrows(), 1):
        label = row["label"] if row["label"] else f"Matrix {row['matrix']}"
        ci = row["ci"]
        p_val = row["p_value"]
        agreements = int(row["agreements"])
        violations = n_preds - agreements - int(row["ties"])

        # Interpretation
        interpretation, _, _ = _interpret_ci(ci)

        # Significance
        if p_val < 0.001:
            sig = "p < .001 ***"
        elif p_val < 0.01:
            sig = "p < .01 **"
        elif p_val < 0.05:
            sig = "p < .05 *"
        else:
            sig = f"p = {p_val:.3f} ns"

        print(f"[{idx}] {label}")  # noqa: T201
        print(f"    CI = {ci:.3f} ({interpretation}) • {sig}")  # noqa: T201
        print(  # noqa: T201
            f"    {agreements}/{n_preds} satisfied ({agreements / n_preds * 100:.0f}%), {violations}/{n_preds} violated ({violations / n_preds * 100:.0f}%)"
        )
        print()  # noqa: T201

    print("=" * 70)  # noqa: T201


def _print_results_rich(results: pd.DataFrame) -> None:
    """Create compact rich formatted output of RTHOR results."""
    requires("rich", reason="use_rich=True", extras="rich")
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    n_mats = len(results)
    n_vars = int(results["n_variables"].iloc[0])
    n_preds = int(results["predictions"].iloc[0])
    n_perms = int(results["n_permutations"].iloc[0])

    console = Console()

    # Header with better hierarchy
    console.print()
    console.print("[bold white on blue] RTHOR TEST RESULTS [/]", justify="center")
    console.print(
        f"[dim]{n_mats} {'matrix' if n_mats == 1 else 'matrices'} • {n_vars} variables • {n_preds} predictions • {n_perms:,} permutations[/]",
        justify="center",
    )
    console.print()

    # Results for each matrix
    for idx, (_, row) in enumerate(results.iterrows(), 1):
        label = row["label"] if row["label"] else f"Matrix {row['matrix']}"
        ci = row["ci"]
        p_val = row["p_value"]
        agreements = int(row["agreements"])
        violations = n_preds - agreements - int(row["ties"])

        # Interpretation
        interpretation, quality, symbol = _interpret_ci(ci)

        # Color based on quality
        if quality in ("excellent", "good"):
            ci_color = "bright_green"
        elif quality == "moderate":
            ci_color = "yellow"
        else:
            ci_color = "red"

        # Significance
        if p_val < 0.001:
            sig_text = "p < .001 ***"
            sig_color = "bright_red"
        elif p_val < 0.01:
            sig_text = "p < .01 **"
            sig_color = "yellow"
        elif p_val < 0.05:
            sig_text = "p < .05 *"
            sig_color = "green"
        else:
            sig_text = f"p = {p_val:.3f} ns"
            sig_color = "dim"

        result_text = Text()
        result_text.append(f"[{idx}] {label}\n", style="bold white")
        result_text.append("    ", style="white")
        result_text.append(f"{symbol} ", style=ci_color)  # Add symbol
        result_text.append("CI = ", style="white")
        result_text.append(f"{ci:.3f}", style=f"bold {ci_color}")
        result_text.append(f" ({interpretation}) • ", style="white")
        result_text.append(sig_text, style=sig_color)
        result_text.append("\n", style="white")
        result_text.append(
            f"    {agreements}/{n_preds} satisfied ({agreements / n_preds * 100:.0f}%), ",
            style="green",
        )
        result_text.append(
            f"{violations}/{n_preds} violated ({violations / n_preds * 100:.0f}%)\n",
            style="red",
        )

        console.print(Panel(result_text, box=box.ROUNDED, padding=(0, 1)))

    # Add interpretation hint
    console.print(
        "[dim italic]ℹ️  Higher CI values indicate better fit to the hypothesis (range: -1 to +1)[/]"  # noqa: RUF001
    )
    console.print()

    console.print()


def print_comparison(
    individual: pd.DataFrame,
    pairwise: pd.DataFrame,
    *,
    use_rich: bool = True,
) -> None:
    """Print comparison results in a compact, interpretable format."""
    if use_rich and is_installed("rich"):
        _print_comparison_rich(individual, pairwise)
    else:
        _print_comparison_plain(individual, pairwise)


def _print_comparison_plain(individual: pd.DataFrame, pairwise: pd.DataFrame) -> None:
    """Generate concise plain text output of comparison results."""
    n_mats = len(individual)
    n_vars = int(individual["n_variables"].iloc[0])
    n_preds = int(individual["predictions"].iloc[0])
    n_perms = int(individual["n_permutations"].iloc[0])

    print("=" * 70)  # noqa: T201
    print("RTHOR MATRIX COMPARISON")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print(  # noqa: T201
        f"{n_mats} matrices • {n_vars} variables • {n_preds} predictions • {n_perms:,} permutations"
    )
    print()  # noqa: T201

    # Individual results
    print("INDIVIDUAL FIT:")  # noqa: T201
    for _, row in individual.iterrows():
        mat_id = int(row["matrix"])
        ci = row["ci"]
        p_val = row["p_value"]
        interpretation, _, _ = _interpret_ci(ci)

        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else "ns"
        )
        print(f"  Matrix {mat_id}: CI = {ci:.3f} ({interpretation}) [{sig}]")  # noqa: T201
    print()  # noqa: T201

    # Pairwise comparisons
    print("PAIRWISE COMPARISONS:")  # noqa: T201
    for _, row in pairwise.iterrows():
        m1 = int(row["matrix1"])
        m2 = int(row["matrix2"])
        ci = row["ci"]
        p_val = row["p_value"]
        both = int(row["both_agree"])
        only1 = int(row["only1"])
        only2 = int(row["only2"])

        # Interpret the comparison
        if abs(ci) < 0.05:
            winner = "Similar fit"
        elif ci > 0:
            winner = f"Matrix {m2} better"
        else:
            winner = f"Matrix {m1} better"

        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else "ns"
        )

        print(  # noqa: T201
            f"  {m1} vs {m2}: {winner} (CI = {ci:+.3f}) [{sig}] | Both: {both}, Only {m1}: {only1}, Only {m2}: {only2}"
        )

    print()  # noqa: T201
    print("=" * 70)  # noqa: T201


def _print_comparison_rich(individual: pd.DataFrame, pairwise: pd.DataFrame) -> None:
    """Create compact rich formatted output of comparison results."""
    requires("rich", reason="use_rich=True", extras="rich")
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    n_mats = len(individual)
    n_vars = int(individual["n_variables"].iloc[0])
    n_preds = int(individual["predictions"].iloc[0])
    n_perms = int(individual["n_permutations"].iloc[0])

    console = Console()

    # Header with better hierarchy
    console.print()
    console.print("[bold white on blue] RTHOR MATRIX COMPARISON [/]", justify="center")
    console.print(
        f"[dim]{n_mats} matrices • {n_vars} variables • {n_preds} predictions • {n_perms:,} permutations[/]",
        justify="center",
    )
    console.print()

    # Individual results as compact table
    indiv_table = Table(
        title="Individual Fit",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold yellow",
    )
    indiv_table.add_column("Matrix", justify="center", style="cyan")
    indiv_table.add_column("", justify="center", width=2)  # Symbol column
    indiv_table.add_column("CI", justify="right")
    indiv_table.add_column("Interpretation", justify="left")
    indiv_table.add_column("Sig.", justify="center", width=4)

    for _, row in individual.iterrows():
        mat_id = int(row["matrix"])
        ci = row["ci"]
        p_val = row["p_value"]
        interpretation, quality, symbol = _interpret_ci(ci)

        ci_color = (
            "bright_green"
            if quality in ("excellent", "good")
            else "yellow"
            if quality == "moderate"
            else "red"
        )
        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else "ns"
        )

        indiv_table.add_row(
            str(mat_id),
            f"[{ci_color}]{symbol}[/]",
            f"[{ci_color}]{ci:.3f}[/]",
            interpretation,
            f"[dim]{sig}[/]",
        )

    console.print(indiv_table)
    console.print()

    # Pairwise comparisons
    console.print("[bold yellow]PAIRWISE COMPARISONS[/]")
    for _, row in pairwise.iterrows():
        m1 = int(row["matrix1"])
        m2 = int(row["matrix2"])
        ci = row["ci"]
        p_val = row["p_value"]
        both = int(row["both_agree"])
        only1 = int(row["only1"])
        only2 = int(row["only2"])

        comp_text = Text()
        comp_text.append(f"{m1} vs {m2}: ", style="cyan")

        # Interpret the comparison
        if abs(ci) < 0.05:
            winner = "Similar fit"
            ci_color = "yellow"
        elif ci > 0:
            winner = f"Matrix {m2} better"
            ci_color = "green"
        else:
            winner = f"Matrix {m1} better"
            ci_color = "green"

        sig_color = (
            "bright_red"
            if p_val < 0.001
            else "yellow"
            if p_val < 0.01
            else "green"
            if p_val < 0.05
            else "dim"
        )
        sig = (
            "***"
            if p_val < 0.001
            else "**"
            if p_val < 0.01
            else "*"
            if p_val < 0.05
            else "ns"
        )

        comp_text.append(f"{winner}", style=ci_color)
        comp_text.append(f" (CI = {ci:+.3f}) ", style="white")
        comp_text.append(f"[{sig}]", style=sig_color)
        comp_text.append(
            f" | Both: {both}, Only {m1}: {only1}, Only {m2}: {only2}", style="dim"
        )

        console.print(Panel(comp_text, box=box.ROUNDED, padding=(0, 1)))

    # Add interpretation hint
    console.print()
    console.print(
        "[dim italic]Info: Positive CI means matrix 2 fits better, negative means matrix 1 fits better[/]"
    )
    console.print()
