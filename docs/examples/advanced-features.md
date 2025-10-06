# Advanced Features

This example demonstrates advanced usage including custom orderings, DataFrame input, and pairwise comparisons.

## Interactive Notebook

!marimo_file /notebooks/advanced_features.py

## Topics Covered

### Custom Orderings

Define your own hypothesized orderings for any number of variables:

```python
# For 4 variables with linear ordering
custom_order = [1, 2, 3, 2, 3, 3]
result = pythor.rthor_test(matrix, order=custom_order)
```

The ordering vector specifies the hypothesized relationship between all pairs of variables.

### Working with Raw Data

pythor can compute correlations from raw data automatically:

```python
import pandas as pd

# Create DataFrames with raw data
df1 = pd.DataFrame({'var1': [...], 'var2': [...], ...})
df2 = pd.DataFrame({'var1': [...], 'var2': [...], ...})

# Test directly - correlations computed automatically
result = pythor.rthor_test([df1, df2], order="circular6")
```

### Pairwise Comparisons

Compare multiple matrices to see which fits best:

```python
comparison = pythor.compare_matrices(
    [matrix1, matrix2, matrix3],
    order="circular6"
)

# Individual results
print(comparison.rthor_results)

# Pairwise differences
print(comparison.comparisons)
```

The comparison CI indicates which matrix fits better:

- **CI > 0**: Matrix 2 fits better than Matrix 1
- **CI < 0**: Matrix 1 fits better than Matrix 2
- **CI ≈ 0**: Similar fit

### File Input

For large datasets, read from files:

```python
result = pythor.rthor_test(
    "correlations.txt",
    n_matrices=10,
    n_variables=8,
    order="circular8"
)
```

File format: Lower triangular matrices with diagonal, whitespace-separated.

## Performance Tips

- Use NumPy arrays for pre-computed correlations when possible
- For many small datasets, consider batch processing
- The vectorized implementation is optimized for matrices with 4-20 variables

## Export and Analysis

```python
# Export to CSV
result.results.to_csv("results.csv")

# Filter significant results
sig = result.results[result.results['p_value'] < 0.05]

# Get results as dictionary
result_dict = result.to_dict()
```
