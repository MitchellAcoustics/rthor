# Overview

`rthor` provides a simple, high-level API for testing correlation matrices against hypothesized orderings. The main functions are:

- [**`test()`**][rthor.test]: Test one or more correlation matrices
- [**`compare()`**][rthor.compare]: Compare multiple matrices pairwise

Results are returned as pandas DataFrames for easy integration with data analysis workflows.

## Input Formats

`rthor` accepts multiple input formats for flexibility:

### NumPy Arrays

```python
import numpy as np
import rthor

# Single matrix (2D array)
matrix = np.array([[1.0, 0.8], [0.8, 1.0]])
result = rthor.test(matrix, order="circular6")

# Multiple matrices (3D array with shape [n_vars, n_vars, n_matrices])
matrices = np.stack([matrix1, matrix2, matrix3], axis=2)
result = rthor.test(matrices, order="circular6")
```

### pandas DataFrames

```python
import pandas as pd
import rthor

# DataFrames with raw data - correlations computed automatically
df1 = pd.DataFrame({'var1': [...], 'var2': [...], ...})
df2 = pd.DataFrame({'var1': [...], 'var2': [...], ...})

result = rthor.test([df1, df2], order="circular6")
```

### File Input

```python
# Text file with lower triangular matrices
result = rthor.test(
    "correlations.txt",
    n_matrices=10,
    n_variables=6,
    order="circular6"
)
```

File format: Lower triangular matrices including diagonal, whitespace-separated values.

## Preset Orderings

`rthor` includes two preset orderings for common circumplex models:

### circular6

For 6 variables arranged in a circular pattern (e.g., interpersonal circumplex):

```python
result = rthor.test(matrix, order="circular6")
```

Hypothesizes that adjacent variables have stronger correlations than distant ones.

### circular8

For 8 variables arranged in a circular pattern:

```python
result = rthor.test(matrix, order="circular8")
```

Commonly used for octant models in personality and emotion research.

## Custom Orderings

You can specify custom hypothesized orderings for any number of variables:

```python
# For 4 variables with linear ordering: 1 < 2 < 3 < 4
custom_order = [1, 2, 3, 2, 3, 3]
result = rthor.test(matrix, order=custom_order)
```

The ordering vector specifies the expected relationship between all pairs of variables. For k variables, the vector has length k×(k-1)/2.

See the [Advanced Features](../examples/advanced-features.py) example for detailed explanation of custom orderings.

## Statistical Interpretation

### Correspondence Index (CI)

The CI measures agreement between data and hypothesis:

- **CI = 1.0**: Perfect agreement with hypothesis
- **CI = 0.0**: No better than chance
- **CI = -1.0**: Perfect disagreement (opposite of hypothesis)

Formula: CI = (agreements - disagreements) / total_predictions

### p-values

Computed via permutation test (default: 5000 permutations):

- **p < 0.05**: Significant fit (conventional threshold)
- **p < 0.01**: Strong fit
- **p < 0.001**: Very strong fit

The p-value represents the proportion of random permutations that achieve a CI as high or higher than the observed CI.

## Export and Integration

### Working with DataFrames

Results are pandas DataFrames with full pandas functionality:

```python
result = rthor.test(matrices, order="circular6")

# Filter significant results
sig = result[result['p_value'] < 0.05]

# Export to CSV
result.to_csv("results.csv", index=False)
```

### To Dictionary/JSON

```python
import json

result_dict = result.to_dict(orient='records')
with open("results.json", "w") as f:
    json.dump(result_dict, f, indent=2)
```

### Integration with Statistical Workflows

```python
# Extract CI values for further analysis
ci_values = result['ci'].values

# Get matrix with best fit
best_matrix = result.loc[result['ci'].idxmax(), 'label']

# Compare groups
group1_ci = result.loc[result['label'].str.contains('Group1'), 'ci']
group2_ci = result.loc[result['label'].str.contains('Group2'), 'ci']
```

## Performance Notes

- Vectorized operations using NumPy for efficiency
- Optimized for matrices with 4-20 variables
- Memory-efficient permutation algorithm
- Pre-computed correlations recommended for repeated analyses

## See Also

- [Basic Usage Example](../examples/basic-usage.py) - Getting started guide
- [Advanced Features](../examples/advanced-features.py) - Custom orderings, comparisons
- [Paper Validation](../examples/paper-validation.py) - Verification against Hubert & Arabie (1987)
- [Core Concepts](../user-guide/concepts.md) - Theoretical background
