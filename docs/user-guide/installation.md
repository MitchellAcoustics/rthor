# Installation

## Requirements

- Python 3.11 or later
- NumPy >= 1.24.0
- pandas >= 2.0.0

## Install from PyPI

Once released, install rthor using pip:

```bash
pip install rthor
```

Or with uv:

```bash
uv pip install rthor
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
uv run prek run --setup
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
matrix = np.array([[1.0, 0.8], [0.8, 1.0]])
result = rthor.rthor_test(matrix, order="circular6")
print(result.summary())
```

## Optional Dependencies

### For Interactive Notebooks

To run the example marimo notebooks:

```bash
pip install marimo
```

Then run:

```bash
marimo edit docs/notebooks/basic_usage.py
```

### For Documentation Building

To build the documentation locally:

```bash
uv sync --group docs
uv run mkdocs serve
```

## Troubleshooting

### NumPy Installation Issues

If you encounter NumPy installation issues on Apple Silicon:

```bash
pip install --upgrade pip setuptools wheel
pip install numpy
pip install rthor
```

### Import Errors

If you get import errors after installation:

1. Verify installation: `pip show rthor`
2. Check Python version: `python --version` (must be 3.11+)
3. Try reinstalling: `pip uninstall rthor && pip install rthor`

### Type Checking Issues

If using mypy or other type checkers, rthor is fully typed. If you encounter issues:

```bash
# Install type stubs for dependencies
pip install types-numpy types-pandas
```

## Next Steps

- [Core Concepts](concepts.md) - Understand RTHOR
- [Basic Usage](../examples/basic-usage.py) - Get started with examples
- [API Reference](../api/reference/index.md) - Full function documentation
