# Installation

## Requirements

- Python 3.11 or later
- NumPy >= 1.24.0
- pandas >= 2.0.0

## Install from PyPI

Once released, install pythor using pip:

```bash
pip install pythor
```

Or with uv:

```bash
uv pip install pythor
```

## Install from Source

For the latest development version:

```bash
git clone https://github.com/MitchellAcoustics/pythor.git
cd pythor
pip install -e .
```

Or with uv:

```bash
git clone https://github.com/MitchellAcoustics/pythor.git
cd pythor
uv pip install -e .
```

## Development Installation

To contribute to pythor, install with development dependencies:

```bash
git clone https://github.com/MitchellAcoustics/pythor.git
cd pythor
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
import pythor
print(pythor.__version__)

# Run a quick test
import numpy as np
matrix = np.array([[1.0, 0.8], [0.8, 1.0]])
result = pythor.rthor_test(matrix, order="circular6")
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
pip install pythor
```

### Import Errors

If you get import errors after installation:

1. Verify installation: `pip show pythor`
2. Check Python version: `python --version` (must be 3.11+)
3. Try reinstalling: `pip uninstall pythor && pip install pythor`

### Type Checking Issues

If using mypy or other type checkers, pythor is fully typed. If you encounter issues:

```bash
# Install type stubs for dependencies
pip install types-numpy types-pandas
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Learn basic usage
- [Core Concepts](concepts.md) - Understand RTHOR
- [Examples](../examples/basic-usage.py) - See it in action
