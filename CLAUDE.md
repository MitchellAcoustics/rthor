# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python implementation of RTHOR (Randomization test of hypothesized order relations).

- Python versions: 3.11-3.13
- Package manager: `uv` is used for running Python commands
- Build system: setuptools with setuptools-scm for versioning
- **Primary use case**: Importable Python library (not CLI/app focused)
- **Development approach**: Test-driven development with regression tests against R implementation

## Development Commands

### Running Python/Tests

```bash
# Run tests across all Python versions
tox

# Run tests in current environment
uv run pytest tests

# Run tests with coverage
uv run pytest --cov --cov-report=xml

# Run a single test file
uv run pytest tests/test_dummy.py
```

### Linting and Formatting

```bash
# Ruff is configured to auto-fix issues
uv run ruff check .
uv run ruff format .

# Type checking with ty (configured in pre-commit)
uv run ty check . --ignore unresolved-import
```

### Documentation

```bash
# Build documentation
tox -e docs

# Build and serve documentation locally
mkdocs serve
```

### Building

```bash
# Build distribution packages
uv run python -m build
```

### Pre-commit Hooks

Pre-commit hooks are managed with `prek`. The following checks run automatically:

- ruff (linting and formatting)
- markdownlint
- toml-sort
- ty (type checking)
- prettier (markdown/yaml/json formatting)
- Standard pre-commit hooks (trailing whitespace, EOF fixer, etc.)

## Project Structure

```text
src/pythor/          # Main package source (library API)
  __init__.py        # Package initialization and public API exports
  _version.py        # Auto-generated version (setuptools-scm)
tests/               # Test files
  conftest.py        # Pytest fixtures and configuration
  fixtures/          # Test data (R outputs converted to JSON/CSV)
  test_rthor_regression.py  # Regression tests against R RTHORR package
docs/                # MkDocs documentation
RTHORR/              # Original R package (for reference and test generation)
pyproject.toml       # Project configuration, dependencies, and tool settings
```

## Code Style

- Ruff is configured with `select = ["ALL"]` and specific ignores in pyproject.toml
- All Python code should have type hints (ty checking enforced)
- Docstrings follow Google style (configured for mkdocstrings)
- Maximum cyclomatic complexity: 18
- Tests are in `tests/` directory and run with pytest

## Version Management

- Version is auto-generated from git tags using setuptools-scm
- Version file is written to `src/pythor/_version.py`
- No local version suffixes in releases (`local_scheme = "no-local-version"`)

## Implementation Priorities

### Priority 1: Results Parity with R

- Regression tests in `tests/test_rthor_regression.py` compare against R RTHORR outputs
- Test data converted from R .rds files to JSON/CSV in `tests/fixtures/`
- All numerical outputs must match R to high precision (rtol=1e-10, atol=1e-12)
- Permutation order must match R for identical p-values

### Priority 2: Pythonic Design

- Use NumPy for core numerical operations (not xarray - adds unnecessary overhead)
- Use pandas only for I/O and results formatting
- Clean, modular code with proper type hints
- Follow scientific Python conventions
