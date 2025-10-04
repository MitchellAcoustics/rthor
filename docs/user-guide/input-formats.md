# Input Formats

pythor accepts multiple input formats to work seamlessly with different workflows. This guide covers all supported formats and their requirements.

## Overview

pythor accepts three main input types:

1. **NumPy arrays** - Pre-computed correlation matrices
2. **pandas DataFrames** - Raw data (correlations computed automatically)
3. **Text files** - Correlation matrices stored in files

## NumPy Arrays

### Single Matrix (2D Array)

The simplest case - a single correlation matrix:

```python
import numpy as np
import pythor

# 6×6 correlation matrix
matrix = np.array([
    [1.00, 0.80, 0.50, 0.20, 0.40, 0.70],
    [0.80, 1.00, 0.75, 0.45, 0.30, 0.55],
    [0.50, 0.75, 1.00, 0.80, 0.50, 0.35],
    [0.20, 0.45, 0.80, 1.00, 0.75, 0.40],
    [0.40, 0.30, 0.50, 0.75, 1.00, 0.70],
    [0.70, 0.55, 0.35, 0.40, 0.70, 1.00]
])

result = pythor.rthor_test(matrix, order="circular6")
```

**Requirements**:

- Shape: `[n_variables, n_variables]`
- Must be symmetric
- Diagonal should be 1.0 (or close)
- Values between -1 and 1

### Multiple Matrices (3D Array)

Stack multiple matrices along the third dimension:

```python
# Create three 6×6 matrices
matrix1 = np.array([...])  # Shape: (6, 6)
matrix2 = np.array([...])  # Shape: (6, 6)
matrix3 = np.array([...])  # Shape: (6, 6)

# Stack along axis=2
matrices = np.stack([matrix1, matrix2, matrix3], axis=2)
# Shape: (6, 6, 3)

result = pythor.rthor_test(
    matrices,
    order="circular6",
    labels=["Group A", "Group B", "Group C"]
)
```

**Requirements**:

- Shape: `[n_variables, n_variables, n_matrices]`
- Use `axis=2` when stacking
- All matrices must have same dimensions

**Common mistake**:

```python
# ❌ Wrong - stacks along axis=0
matrices = np.stack([m1, m2, m3])  # Shape: (3, 6, 6)

# ✅ Correct - stacks along axis=2
matrices = np.stack([m1, m2, m3], axis=2)  # Shape: (6, 6, 3)
```

## pandas DataFrames

### Single DataFrame

Pass a DataFrame with raw data - pythor computes correlations automatically:

```python
import pandas as pd
import numpy as np
import pythor

# Raw data with 6 variables and 100 observations
np.random.seed(42)
data = pd.DataFrame({
    'var1': np.random.normal(0, 1, 100),
    'var2': np.random.normal(0, 1, 100),
    'var3': np.random.normal(0, 1, 100),
    'var4': np.random.normal(0, 1, 100),
    'var5': np.random.normal(0, 1, 100),
    'var6': np.random.normal(0, 1, 100),
})

# Correlations computed automatically
result = pythor.rthor_test(data, order="circular6")
```

**Requirements**:

- All columns must be numeric
- Each column is treated as a variable
- Rows are observations
- Missing values are handled by pandas correlation (pairwise deletion by default)

### Multiple DataFrames

Pass a list of DataFrames:

```python
# Create separate datasets for different groups
group1_data = pd.DataFrame({...})  # 100 observations
group2_data = pd.DataFrame({...})  # 100 observations
group3_data = pd.DataFrame({...})  # 100 observations

# Test all groups
result = pythor.rthor_test(
    [group1_data, group2_data, group3_data],
    order="circular6",
    labels=["Control", "Treatment A", "Treatment B"]
)
```

**Requirements**:

- All DataFrames must have same columns (variable names)
- Column order must match
- Sample sizes can differ

### Loading from CSV

Common workflow with CSV files:

```python
# Load raw data
data = pd.read_csv('study_data.csv')

# Test
result = pythor.rthor_test(data, order="circular6")

# Or load multiple files
datasets = [
    pd.read_csv('group1.csv'),
    pd.read_csv('group2.csv'),
    pd.read_csv('group3.csv')
]
result = pythor.rthor_test(datasets, order="circular6")
```

## File Input

For large-scale analyses or integration with other tools, pythor can read correlation matrices from text files.

### File Format

Text file with lower triangular matrices (including diagonal):

```text
1.000000
0.800000 1.000000
0.500000 0.750000 1.000000
0.200000 0.450000 0.800000 1.000000
0.400000 0.300000 0.500000 0.750000 1.000000
0.700000 0.550000 0.350000 0.400000 0.700000 1.000000
1.000000
0.700000 1.000000
0.450000 0.680000 1.000000
0.250000 0.400000 0.720000 1.000000
0.350000 0.280000 0.480000 0.700000 1.000000
0.650000 0.500000 0.320000 0.380000 0.650000 1.000000
```

This shows two 6×6 matrices concatenated.

### Reading from File

```python
result = pythor.rthor_test(
    "correlations.txt",
    n_matrices=2,
    n_variables=6,
    order="circular6",
    labels=["Sample 1", "Sample 2"]
)
```

**Required parameters for file input**:

- `n_matrices`: Number of matrices in the file
- `n_variables`: Number of variables per matrix

**File requirements**:

- Values separated by whitespace (spaces or tabs)
- Lower triangular format (including diagonal)
- One matrix follows another
- No headers or extra text

### Creating Files from NumPy

To save NumPy arrays in the correct format:

```python
def save_correlation_matrices(matrices, filename):
    """Save correlation matrices to file in RTHOR format."""
    with open(filename, 'w') as f:
        n_vars = matrices.shape[0]
        n_mats = matrices.shape[2] if matrices.ndim == 3 else 1

        if matrices.ndim == 2:
            matrices = matrices[:, :, np.newaxis]

        for k in range(n_mats):
            for i in range(n_vars):
                row = matrices[i, :i+1, k]
                f.write(' '.join(f'{x:.6f}' for x in row) + '\n')

# Save matrices
matrices = np.stack([matrix1, matrix2], axis=2)
save_correlation_matrices(matrices, 'correlations.txt')

# Read back
result = pythor.rthor_test(
    'correlations.txt',
    n_matrices=2,
    n_variables=6,
    order="circular6"
)
```

## Data Validation

pythor automatically validates input data and provides helpful error messages.

### Correlation Matrix Validation

```python
# ❌ Non-symmetric matrix
matrix = np.array([
    [1.0, 0.8],
    [0.7, 1.0]  # 0.7 ≠ 0.8
])
# Raises: ValueError: Matrix is not symmetric

# ❌ Invalid diagonal
matrix = np.array([
    [0.5, 0.8],  # Diagonal should be 1.0
    [0.8, 1.0]
])
# Raises: ValueError: Diagonal values must be 1.0

# ❌ Values out of range
matrix = np.array([
    [1.0, 1.5],  # Correlation can't be > 1
    [1.5, 1.0]
])
# Raises: ValueError: Correlations must be between -1 and 1
```

### DataFrame Validation

```python
# ❌ Non-numeric columns
data = pd.DataFrame({
    'var1': [1, 2, 3],
    'var2': ['a', 'b', 'c']  # String column
})
# Raises: ValueError: All columns must be numeric

# ✅ Missing values are OK (handled by pandas)
data = pd.DataFrame({
    'var1': [1, 2, np.nan],
    'var2': [4, 5, 6]
})
result = pythor.rthor_test(data, order="circular6")  # Works
```

## Performance Considerations

### Pre-compute Correlations

If running multiple analyses on the same data, pre-compute correlations:

```python
# Compute once
correlation_matrix = data.corr().values

# Use multiple times with different orderings
result1 = pythor.rthor_test(correlation_matrix, order="circular6")
result2 = pythor.rthor_test(correlation_matrix, order="circular8")
result3 = pythor.rthor_test(correlation_matrix, order=custom_order)
```

### Memory-Efficient File Processing

For very large numbers of matrices:

```python
# Instead of loading all into memory
all_data = [pd.read_csv(f'data_{i}.csv') for i in range(1000)]  # ❌

# Process in batches
batch_size = 100
for batch_start in range(0, 1000, batch_size):
    batch_data = [
        pd.read_csv(f'data_{i}.csv')
        for i in range(batch_start, batch_start + batch_size)
    ]
    result = pythor.rthor_test(batch_data, order="circular6")
    result.results.to_csv(f'results_batch_{batch_start}.csv')
```

## Tips and Best Practices

!!! tip "Column Names"

    When using DataFrames, column names are preserved in output. Use descriptive names:

    ```python
    data.columns = ['Dominance', 'Affiliation', 'Warmth', ...]
    ```

!!! tip "Reproducibility"

    Set random seed for reproducible p-values:

    ```python
    np.random.seed(42)
    result = pythor.rthor_test(data, order="circular6")
    ```

!!! warning "Sample Size"

    For DataFrame input, ensure adequate sample size for stable correlations. General rule: N ≥ 10 × n_variables.

!!! tip "Data Standardization"

    pythor uses Pearson correlations. If your data needs transformation (e.g., log, rank), do it before passing to pythor:

    ```python
    from scipy.stats import rankdata
    data_ranked = data.apply(rankdata)
    result = pythor.rthor_test(data_ranked, order="circular6")
    ```

## Next Steps

- Learn about [interpreting results](results.md)
- See [basic usage examples](../examples/basic-usage.md)
- Explore [advanced features](../examples/advanced-features.md)
- Check [API reference](../api.md)
