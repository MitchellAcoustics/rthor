# pythor Development Plan

## Overview

This document outlines the step-by-step plan for implementing the Python translation of the R RTHORR package. We're following a Test-Driven Development (TDD) approach with **Priority 1: Results Parity with R** as the primary goal.

## Development Approach

### Test-Driven Development Cycle

For each function:

1. **Un-skip the test** - Remove `@pytest.mark.skip` decorator from the corresponding test
2. **Run the test** - Verify it fails (as expected, function doesn't exist yet)
3. **Implement the function** - Write the minimal code to make the test pass
4. **Run the test** - Verify it passes with numerical precision matching R
5. **Refactor** - Clean up code while keeping tests green
6. **Move to next function**

## Implementation Order

### Phase 1: Core Algorithm Components

These are shared utilities needed by all functions:

#### 1.1 Order Hypothesis Generation

**File**: `src/pythor/core.py`

**Function**: `generate_hypothesis_matrix(ord: str | list[int], n: int) -> np.ndarray`

- Input: Order specification ("circular6", "circular8", or custom list)
- Output: Hypothesis matrix (np × np) where np = (n² - n) / 2
- R Code Reference: Lines 32-38, 70-74 in `randall.R`

**Algorithm**:

```python
# Convert ord string to numeric array
if ord == "circular6":
    ord_array = [1,2,3,2,1,1,2,3,2,1,2,3,1,2,1]
elif ord == "circular8":
    ord_array = [1,2,3,4,3,2,1,1,2,3,4,3,2,1,2,3,4,3,1,2,3,4,1,2,3,1,2,1]

# Build hypothesis matrix: mathyp[i,j] = 1 if ord[j] < ord[i], else 0
```

**Test**: Create unit test in `tests/test_core.py` with known inputs/outputs

#### 1.2 Permutation Generation

**File**: `src/pythor/permutations.py`

**Function**: `generate_permutations(n: int, max_perm: int = 50000) -> np.ndarray`

- Input: Number of variables n, maximum permutations
- Output: Permutation matrix (nper × n)
- R Code Reference: Lines 93-107 in `randall.R`

**Algorithm**:

```python
nper = factorial(n)
if nper > max_perm:
    nper = max_perm
    # Generate random permutations
else:
    # Generate all permutations using itertools.permutations
```

**Critical**: Permutation order must match R exactly for identical p-values

**Test**: Verify permutations match R output for n=6 case

#### 1.3 Fit Calculation

**File**: `src/pythor/core.py`

**Function**: `calculate_fit(dmat: np.ndarray, mathyp: np.ndarray) -> tuple[int, int]`

- Input: Correlation matrix, hypothesis matrix
- Output: (nagr, ntie) - number of agreements and ties
- R Code Reference: Lines 122-148 in `randall.R`

**Algorithm**:

```python
# Extract upper triangle as vector (scal)
# Build comparison matrix (matc):
#   matc[i,j] = 1 if scal[j] > scal[i]
#   matc[i,j] = 2 if scal[j] == scal[i]
#   matc[i,j] = 0 if scal[j] < scal[i]
# Count: nagr = sum(matc == 1 & mathyp == 1)
#        ntie = sum(matc == 2 & mathyp == 1)
```

**Optimization**: Use NumPy broadcasting instead of nested loops

**Test**: Verify against known R intermediate values

#### 1.4 Matrix File I/O

**File**: `src/pythor/io.py`

**Function**: `read_correlation_matrices(filepath: Path, n: int, nmat: int) -> np.ndarray`

- Input: File path, number of variables, number of matrices
- Output: 3D array (n × n × nmat)
- R Code Reference: Lines 49-67 in `randall.R`

**Format**: Input file contains lower triangular matrices with diagonal

```text
1.00
 .62 1.00
 .40 .62 1.00
 ...
```

**Test**: Verify against `tests/fixtures/input.txt`

### Phase 2: Main API Functions

#### 2.1 Implement `randall()`

**File**: `src/pythor/api.py`

**Signature**:

```python
def randall(
    n: int,
    nmat: int,
    ord: str | list[int] = "circular6",
    input: Path | str,
    description: list[str] | None = None,
) -> pd.DataFrame:
```

**Test**: `tests/test_rthor_regression.py::TestRandallRegression::test_randall_matches_r_output`

**Un-skip**: Line 18 in `test_rthor_regression.py`

**Steps**:

1. Read matrices using `read_correlation_matrices()`
2. Generate hypothesis matrix using `generate_hypothesis_matrix()`
3. Generate permutations using `generate_permutations()`
4. For each matrix:
   - Calculate original fit
   - Calculate CI: `(nagr - (nhyp - (nagr + ntie))) / nhyp`
   - Run permutation test
   - Calculate p-value: `count / nper`
5. Return DataFrame with columns: `["mat", "pred", "met", "tie", "CI", "p", "description"]`

**R Reference**: `RTHORR/R/randall.R` lines 29-233

#### 2.2 Implement `randall_from_df()`

**File**: `src/pythor/api.py`

**Signature**:

```python
def randall_from_df(
    df_list: list[pd.DataFrame],
    description: list[str],
    ord: str | list[int] = "circular6",
) -> pd.DataFrame:
```

**Test**: `tests/test_rthor_regression.py::TestRandallFromDfRegression::test_randall_from_df_matches_r_output`

**Un-skip**: Line 123 in `test_rthor_regression.py`

**Steps**:

1. Validate inputs (same number of columns, matching descriptions)
2. Compute correlation matrices: `df.corr()` for each DataFrame
3. Extract lower triangular matrices (matching R's `gdata::lowerTriangle()`)
4. Call core `randall` logic (same as 2.1, steps 2-5)

**R Reference**: `RTHORR/R/randall_from_df.R` lines 27-254

**Critical**: Reverse df_list order (line 74 in R) to match R behavior

#### 2.3 Implement `randmf()`

**File**: `src/pythor/api.py`

**Signature**:

```python
def randmf(
    n: int,
    nmat: int,
    ord: str | list[int] = "circular6",
    input: Path | str,
) -> dict[str, pd.DataFrame]:
```

**Test**: `tests/test_rthor_regression.py::TestRandmfRegression::test_randmf_matches_r_output`

**Un-skip**: Line 63 in `test_rthor_regression.py`

**Returns**: Dictionary with two DataFrames:

- `"RTHOR"`: Same as randall output (without description)
- `"comparisons"`: Pairwise matrix comparisons

**Steps**:

1. Same as randall for reading and hypothesis generation
2. Nested loop over matrix pairs (kk1, kk2):
   - Calculate fit for both matrices
   - Count agreement patterns:
     - `bboth`: both matrices meet hypothesis
     - `yy1n2`: matrix 1 meets, matrix 2 doesn't
     - `nn1y2`: matrix 1 doesn't, matrix 2 meets
     - `nn1n2`: neither meets
   - Calculate comparison CI: `(nn1y2 - yy1n2) / (bboth + yy1n2 + nn1y2 + nn1n2)`
   - Run permutation test for comparison
3. Return both DataFrames in dict

**R Reference**: `RTHORR/R/randmf.R` lines 29-371

#### 2.4 Implement `randmf_from_df()`

**File**: `src/pythor/api.py`

**Signature**:

```python
def randmf_from_df(
    df_list: list[pd.DataFrame],
    ord: str | list[int] = "circular6",
) -> dict[str, pd.DataFrame]:
```

**Test**: `tests/test_rthor_regression.py::TestRandmfFromDfRegression::test_randmf_from_df_matches_r_output`

**Un-skip**: Line 164 in `test_rthor_regression.py`

**Steps**:

1. Validate inputs (>= 2 DataFrames, same dimensions)
2. Compute correlations (same as randall_from_df)
3. Call core `randmf` logic (same as 2.3, steps 1-3)

**R Reference**: `RTHORR/R/randmf_from_df.R` lines 30-414

### Phase 3: Package Integration

#### 3.1 Public API Exports

**File**: `src/pythor/__init__.py`

```python
"""pythor - Python implementation of RTHOR."""

from ._version import __version__
from .api import randall, randall_from_df, randmf, randmf_from_df

__all__ = [
    "__version__",
    "randall",
    "randall_from_df",
    "randmf",
    "randmf_from_df",
]
```

#### 3.2 Type Stubs (if needed)

**File**: `src/pythor/py.typed`

Create empty file to indicate package is typed

#### 3.3 Update Dependencies

Already done in `pyproject.toml`:

- numpy>=1.24.0
- pandas>=2.0.0

Consider adding optional dependencies:

- scipy (if needed for statistical functions)
- typing-extensions (for Python 3.11 compatibility)

### Phase 4: Documentation & Examples

#### 4.1 Update README.md

- Installation instructions
- Quick start examples
- Link to full documentation

#### 4.2 Create Usage Examples

**File**: `docs/examples.md` or Jupyter notebooks

```python
import pythor
import pandas as pd

# Example 1: From correlation matrix file
result = pythor.randall(
    n=6,
    nmat=3,
    ord="circular6",
    input="correlation_matrices.txt",
    description=["sample1", "sample2", "sample3"]
)
print(result)

# Example 2: From raw data
df1 = pd.read_csv("data1.csv")
df2 = pd.read_csv("data2.csv")
result = pythor.randall_from_df(
    df_list=[df1, df2],
    description=["sample1", "sample2"],
    ord="circular6"
)
print(result)
```

#### 4.3 API Documentation

Use mkdocstrings to auto-generate from docstrings

## Key Implementation Notes

### NumPy Optimization Opportunities

The R code has many nested loops that can be vectorized:

**R Code (slow)**:

```r
for(i in 1:np){
  for(j in 1:np){
    if(scal[j] > scal[i]) matc[i,j]<-1
    if(scal[j] == scal[i]) matc[i,j]<-2
    if(scal[j] < scal[i]) matc[i,j]<-0
  }
}
```

**Python (vectorized)**:

```python
# Broadcasting: compare each element against all others
matc = (scal[:, np.newaxis] < scal[np.newaxis, :]).astype(int)
matc[scal[:, np.newaxis] == scal[np.newaxis, :]] = 2
```

### Critical Implementation Details

1. **Permutation Order**: Must match R exactly
   - R uses `permute::allPerms()` with specific ordering
   - Test with n=6 case first (720 permutations)
   - May need to replicate R's permutation algorithm

2. **Matrix Indexing**: R is 1-indexed, Python is 0-indexed
   - Carefully translate loop bounds
   - R: `for(i in 1:n)` → Python: `for i in range(n)`

3. **Upper Triangle Extraction**: Must match R exactly
   - R extracts in specific order with diagonal
   - Python: Use careful indexing or `np.triu_indices()`

4. **Floating Point Precision**:
   - Use `np.float64` throughout
   - Don't round intermediate values
   - Only round in final output if explicitly required

5. **DataFrame Ordering**:
   - `randall_from_df` reverses df_list (line 74 in R)
   - This affects correlation matrix ordering

## Testing Strategy

### Unit Tests (create as needed)

- `tests/test_core.py` - Test core algorithm components
- `tests/test_io.py` - Test file reading
- `tests/test_permutations.py` - Test permutation generation

### Regression Tests (already created)

- `tests/test_rthor_regression.py` - Compare against R outputs

### Testing Checklist

For each function:

- [ ] Remove `@pytest.mark.skip` decorator
- [ ] Run test, verify it fails
- [ ] Implement function
- [ ] Run test, verify numerical precision
- [ ] Check all columns present
- [ ] Check DataFrame dtypes match
- [ ] Check edge cases (if any)

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test class
uv run pytest tests/test_rthor_regression.py::TestRandallRegression -v

# Run with coverage
uv run pytest --cov --cov-report=term-missing

# Run regression tests only
uv run pytest tests/test_rthor_regression.py -v
```

## Success Criteria

### Phase 1 Complete

- [ ] All core utility functions implemented
- [ ] Unit tests passing
- [ ] Code is vectorized using NumPy

### Phase 2 Complete

- [ ] All 4 main API functions implemented
- [ ] All regression tests passing (no `@pytest.mark.skip`)
- [ ] Numerical outputs match R (rtol=1e-10, atol=1e-12)

### Phase 3 Complete

- [ ] Clean public API in `__init__.py`
- [ ] Type hints throughout
- [ ] Passes `ty check` and `ruff check`

### Phase 4 Complete

- [ ] README with examples
- [ ] API documentation generated
- [ ] Usage examples in docs/

### Ready for Release

- [ ] All tests passing
- [ ] Pre-commit hooks passing
- [ ] Documentation complete
- [ ] Version tagged

## Current Status

**Completed**:

- ✅ Test infrastructure setup
- ✅ R test data converted to Python format
- ✅ Regression tests written
- ✅ pytest fixtures created
- ✅ Dependencies added to pyproject.toml

**Next Step**:
Start Phase 1.1 - Implement `generate_hypothesis_matrix()` in `src/pythor/core.py`

## Notes

- Keep `RTHORR/` directory for reference but don't import from it
- This is a pure Python implementation (no R dependencies)
- Primary use case: importable library (not CLI)
- TDD approach keeps us on track for Priority 1
