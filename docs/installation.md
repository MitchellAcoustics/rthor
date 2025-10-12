# Installation

## Requirements

- Python 3.11 or later
- NumPy >= 1.24.0
- pandas >= 2.0.0

Optional dependencies:

- `rich`: For pretty-printing results

## Install from PyPI

Once released, install rthor using pip:

```bash
pip install rthor
```

Or with uv:

```bash
uv add rthor
```

To use our pretty-printing functionality ([rthor.print_results][]) you also need the optional `rich` dependency:

```bash
pip install 'rthor[rich]'
# or with uv
uv add rthor --extra rich
```

## Install from Source

For the latest development version:

```bash
git clone https://github.com/MitchellAcoustics/rthor.git
cd rthor
pip install -e .
```

Or with uv:

```bash
git clone https://github.com/MitchellAcoustics/rthor.git
cd rthor
uv pip install -e .
```

## Development Installation

To contribute to rthor, install with development dependencies:

```bash
git clone https://github.com/MitchellAcoustics/rthor.git
cd rthor
uv sync --group dev
```

This installs additional tools for:

- Testing (pytest, pytest-cov)
- Documentation (mkdocs, marimo)
- Linting (ruff, ty)
- Building (build, twine)
- Pre-commit hooks (prek)

### Set up pre-commit hooks

```bash
uv run prek install
```

This configures hooks for:

- Code formatting (ruff)
- Type checking (ty)
- TOML sorting
- Markdown linting
- Trailing whitespace removal

## Verify Installation

```python
import rthor
print(rthor.__version__)

# Run a quick test
import numpy as np
matrix = np.array(
    [
        [1.00, 0.90, 0.60, 0.30, 0.60, 0.90],  # Var 1
        [0.90, 1.00, 0.90, 0.60, 0.30, 0.60],  # Var 2
        [0.60, 0.90, 1.00, 0.90, 0.60, 0.30],  # Var 3
        [0.30, 0.60, 0.90, 1.00, 0.90, 0.60],  # Var 4
        [0.60, 0.30, 0.60, 0.90, 1.00, 0.90],  # Var 5
        [0.90, 0.60, 0.30, 0.60, 0.90, 1.00],  # Var 6
    ]
)
result = rthor.test(matrix, order="circular6")
rthor.print_results(result)
```

```python
                                   RTHOR Test Results
               1 matrix • 6 variables • 72 predictions • 720 permutations
╭──────────────┬────┬───────┬────────────────┬──────────────┬──────────────┬───────────╮
│ Matrix       │    │    CI │ Interpretation │ Significance │    Satisfied │  Violated │
├──────────────┼────┼───────┼────────────────┼──────────────┼──────────────┼───────────┤
│ [1] Matrix 1 │ ✓  │ 1.000 │ Excellent fit  │   p<.05 *    │ 72/72 (100%) │ 0/72 (0%) │
╰──────────────┴────┴───────┴────────────────┴──────────────┴──────────────┴───────────╯
               ℹ️  Higher CI values indicate better fit (range: -1 to +1)
```

## Next Steps

- [Core Concepts](user-guide/concepts.md) - Understand RTHOR
- [Basic Usage](examples/basic-usage.py) - Get started with examples
- [API Reference](api/reference/index.md) - Full function documentation
