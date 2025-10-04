# Refactoring Plan for pythor v0.2.0

## Goals

1. **Performance**: Vectorize O(n⁴) nested loops → O(n²) or better
2. **Maintainability**: Eliminate 70-80% code duplication
3. **Usability**: Improve API ergonomics (auto-inference, better naming)
4. **Robustness**: Add comprehensive input validation
5. **Pythonic**: Improve variable naming and code organization

## Proposed API Changes

### Current API (v0.1.0a1)

```python
# File-based analysis
randall(n, nmat, filepath, order="circular6", description=None)
randmf(n, nmat, filepath, order="circular6")

# DataFrame-based analysis
randall_from_df(df_list, description, order="circular6")
randmf_from_df(df_list, order="circular6")
```

**Problems:**

- Redundant parameters (`n`, `nmat` are computable)
- Unclear function names (`randall`, `randmf` not intuitive)
- Inconsistent signatures (description required vs optional)
- Two similar functions per analysis type (file vs DataFrame)

### Proposed API (v0.2.0)

```python
# Single function per analysis type with flexible input
rthor_test(
    data: Path | str | list[pd.DataFrame] | np.ndarray,
    order: str | list[int] = "circular6",
    labels: list[str] | None = None,
    n_matrices: int | None = None,  # Only needed for ambiguous file formats
    n_variables: int | None = None,
) -> RTHORResult

compare_matrices(
    data: Path | str | list[pd.DataFrame] | np.ndarray,
    order: str | list[int] = "circular6",
    n_matrices: int | None = None,
    n_variables: int | None = None,
) -> ComparisonResult
```

**Benefits:**

- Single function per analysis type
- Auto-detects input type and infers dimensions
- Consistent signatures
- Clearer function names
- Returns structured result objects (not raw DataFrames)

### Result Objects

```python
@dataclass
class RTHORResult:
    """Results from RTHOR analysis."""

    # Main results DataFrame
    results: pd.DataFrame  # Columns: matrix, predictions, agreements, ties, ci, p_value, label

    # Metadata
    n_matrices: int
    n_variables: int
    order: np.ndarray
    n_predictions: int
    n_permutations: int

    def summary(self) -> str:
        """Print formatted summary."""

    def plot(self) -> Figure:
        """Generate visualization of results."""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""

@dataclass
class ComparisonResult:
    """Results from pairwise matrix comparison."""

    # Individual matrix tests
    rthor_results: pd.DataFrame

    # Pairwise comparisons
    comparisons: pd.DataFrame  # Columns: matrix1, matrix2, both_agree, only1, only2, neither, ci, p_value

    # Metadata (same as RTHORResult)
    n_matrices: int
    n_variables: int
    order: np.ndarray
    n_predictions: int
    n_permutations: int

    def summary(self) -> str:
    def plot(self) -> Figure:
    def to_dict(self) -> dict:
```

## Code Organization Changes

### Current Structure

```
src/pythor/
  api.py (987 lines, 70-80% duplication)
  core.py (189 lines)
  io.py (136 lines)
  permutations.py (96 lines)
```

### Proposed Structure

```
src/pythor/
  # Public API
  __init__.py          # Exports rthor_test, compare_matrices, result classes
  api.py               # Public functions (simplified, ~150 lines)
  results.py           # Result dataclasses and methods

  # Internal implementation
  _core.py             # Core algorithm (vectorized, ~150 lines)
  _hypothesis.py       # Hypothesis matrix generation
  _permutations.py     # Permutation generation and testing
  _io.py               # File I/O
  _validation.py       # Input validation
  _vectorized.py       # Vectorized operations (comparison matrices, etc.)
```

## Variable Naming Improvements

### Current → Proposed

- `dmat` → `correlation_matrix` or `corr_mat`
- `dmatm` → `correlation_matrices` or `corr_mats`
- `mathyp` → `hypothesis_matrix`
- `ord_array` → `order_array`
- `nhyp` → `n_predictions`
- `nagr` → `n_agreements`
- `ntie` → `n_ties`
- `nper` → `n_permutations`
- `matc` → `comparison_matrix`
- `scal` → `correlations_vector`
- `np_pairs` → `n_pairs`
- `kk`, `ii`, `jj` → descriptive names

## Performance Optimizations

### 1. Vectorize comparison matrix building (core.py:143-150)

**Current:** O(n²) nested loops

```python
for i in range(n_pairs):
    for j in range(n_pairs):
        if scal[j] > scal[i]:
            matc[i, j] = 1
        elif scal[j] == scal[i]:
            matc[i, j] = 2
```

**Vectorized:** O(1)

```python
corr_i = correlations_vector[:, np.newaxis]  # Column vector
corr_j = correlations_vector[np.newaxis, :]  # Row vector
comparison_matrix = np.where(
    corr_j > corr_i, 1,
    np.where(corr_j == corr_i, 2, 0)
)
```

### 2. Vectorize agreement counting (core.py:155-160)

**Current:** O(n²) nested loops

```python
for i in range(n_pairs):
    for j in range(n_pairs):
        if matc[i, j] == 1 and mathyp[i, j] == 1:
            nagr += 1
        if matc[i, j] == 2 and mathyp[i, j] == 1:
            ntie += 1
```

**Vectorized:** O(1)

```python
hypothesis_mask = hypothesis_matrix == 1
n_agreements = np.sum((comparison_matrix == 1) & hypothesis_mask)
n_ties = np.sum((comparison_matrix == 2) & hypothesis_mask)
```

### 3. Vectorize hypothesis matrix generation (core.py:87-90)

**Current:** O(n²) nested loops

```python
for i in range(n_pairs):
    for j in range(n_pairs):
        if ord_array[j] < ord_array[i]:
            mathyp[i, j] = 1
```

**Vectorized:** O(1)

```python
order_i = order_array[:, np.newaxis]
order_j = order_array[np.newaxis, :]
hypothesis_matrix = (order_j < order_i).astype(np.int32)
```

### 4. Vectorize pairwise comparison loops (api.py:~500-700)

**Current:** O(n⁴) nested loops in randmf
**Vectorized:** Use broadcasting and boolean indexing

## Input Validation

Add `_validation.py` module:

```python
def validate_correlation_matrix(matrix: np.ndarray) -> None:
    """Validate correlation matrix properties."""
    if matrix.ndim != 2:
        raise ValueError(f"Expected 2D matrix, got {matrix.ndim}D")
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"Expected square matrix, got {matrix.shape}")
    if not np.allclose(matrix, matrix.T, rtol=1e-10):
        raise ValueError("Matrix is not symmetric")
    if not np.allclose(np.diag(matrix), 1.0, rtol=1e-10):
        raise ValueError("Matrix diagonal must be 1.0 (correlation matrix)")
    if not np.all((matrix >= -1 - 1e-10) & (matrix <= 1 + 1e-10)):
        raise ValueError("Correlations must be in [-1, 1]")

def validate_order(order: str | list[int], n_variables: int) -> np.ndarray:
    """Validate and process order specification."""
    if isinstance(order, str):
        if order not in {"circular6", "circular8"}:
            raise ValueError(f"Unknown order preset: {order}. Use 'circular6', 'circular8', or custom list")
        # Return preset
    else:
        order_array = np.asarray(order, dtype=np.int32)
        expected_length = (n_variables * (n_variables - 1)) // 2
        if len(order_array) != expected_length:
            raise ValueError(
                f"Order length {len(order_array)} doesn't match expected {expected_length} "
                f"for {n_variables} variables"
            )
        return order_array

def validate_labels(labels: list[str] | None, n_matrices: int) -> list[str]:
    """Validate and process labels."""
    if labels is None:
        return [f"Matrix {i+1}" for i in range(n_matrices)]
    if len(labels) != n_matrices:
        raise ValueError(f"Number of labels ({len(labels)}) doesn't match number of matrices ({n_matrices})")
    return labels
```

## Testing Strategy

### Regression Tests (STRICT - must pass)

- Keep `test_rthor_regression.py` but update to use new API
- All numerical results must match R output (rtol=1e-10, atol=1e-12)
- Test new API functions against expected outputs

### Unit Tests (CAN CHANGE)

- Update `test_core.py` to test vectorized implementations
- Update `test_io.py` for new validation
- Add `test_validation.py` for validation logic
- Add `test_vectorized.py` for vectorized operations

### New Tests

- `test_performance.py` - Benchmark old vs new implementations
- `test_results.py` - Test result object methods
- `test_api_flexibility.py` - Test auto-inference, multiple input types

## Implementation Order

1. ✅ Create branch and plan
2. Create new result classes (`results.py`)
3. Create validation module (`_validation.py`)
4. Create vectorized operations (`_vectorized.py`)
5. Refactor core algorithms to use vectorized operations (`_core.py`)
6. Create new API functions (`api.py`)
7. Update regression tests to use new API (verify mathematical parity)
8. Add new unit tests
9. Update documentation
10. Performance benchmarking

## Breaking Changes (v0.1.0a1 → v0.2.0a1)

Since we're still in alpha (v0.1.0a1), breaking changes are acceptable:

- Function names changed: `randall()` → `rthor_test()`, `randmf()` → `compare_matrices()`
- Signatures changed: auto-inference, result objects instead of DataFrames
- Parameter names changed: `description` → `labels`, `filepath` → `data`
- Return types changed: DataFrame → dataclass with additional methods

We can provide migration guide in changelog.

## Backward Compatibility Consideration

If desired, we can keep old API as deprecated:

```python
# In __init__.py
from .api import rthor_test, compare_matrices
from ._deprecated import randall, randall_from_df, randmf, randmf_from_df

__all__ = [
    "rthor_test", "compare_matrices",  # New API
    "randall", "randall_from_df", "randmf", "randmf_from_df",  # Deprecated
]
```

But given alpha status, clean break is probably better.
