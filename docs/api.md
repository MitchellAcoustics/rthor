# API Reference

## Overview

rthor provides a simple, high-level API for testing correlation matrices against hypothesized orderings. The main functions are:

- **`rthor_test()`**: Test one or more correlation matrices
- **`compare_matrices()`**: Compare multiple matrices pairwise

Results are returned as dataclass objects with convenient methods for viewing and exporting.

## Core Functions

### rthor_test

::: rthor.rthor_test
options:
show_root_heading: true
show_source: false
members_order: source

### compare_matrices

::: rthor.compare_matrices
options:
show_root_heading: true
show_source: false
members_order: source

## Result Classes

### RTHORResult

::: rthor.RTHORResult
options:
show_root_heading: true
show_source: false
members_order: source
show_signature: false

The main result object returned by `rthor_test()`. Key attributes:

- **`results`**: pandas DataFrame with test results for each matrix
- **`n_matrices`**: Number of matrices tested
- **`n_variables`**: Number of variables per matrix
- **`order`**: The hypothesized ordering used
- **`n_predictions`**: Total number of predictions tested
- **`n_permutations`**: Number of permutations (default: 5000)

Methods:

- **`summary()`**: Get formatted summary string
- **`to_dict()`**: Convert to dictionary (useful for JSON export)

### ComparisonResult

::: rthor.ComparisonResult
options:
show_root_heading: true
show_source: false
members_order: source
show_signature: false

Result object for pairwise matrix comparisons from `compare_matrices()`. Key attributes:

- **`rthor_results`**: pandas DataFrame with individual RTHOR results
- **`comparisons`**: pandas DataFrame with pairwise comparison results
- **`n_matrices`**: Number of matrices compared
- **`n_variables`**: Number of variables per matrix
- **`order`**: The hypothesized ordering used

The `comparisons` DataFrame includes:

- **`both_agree`**: Predictions satisfied by both matrices
- **`only1`**: Predictions satisfied only by matrix 1
- **`only2`**: Predictions satisfied only by matrix 2
- **`neither`**: Predictions satisfied by neither
- **`ci`**: Comparison CI (positive means matrix 2 fits better)
- **`p_value`**: Statistical significance of difference

Methods:

- **`summary()`**: Get formatted summary string
- **`to_dict()`**: Convert to dictionary (useful for JSON export)

## Input Formats

rthor accepts multiple input formats for flexibility:

### NumPy Arrays

```python
import numpy as np
import rthor

# Single matrix (2D array)
matrix = np.array([[1.0, 0.8], [0.8, 1.0]])
result = rthor.rthor_test(matrix, order="circular6")

# Multiple matrices (3D array with shape [n_vars, n_vars, n_matrices])
matrices = np.stack([matrix1, matrix2, matrix3], axis=2)
result = rthor.rthor_test(matrices, order="circular6")
```

### pandas DataFrames

```python
import pandas as pd
import rthor

# DataFrames with raw data - correlations computed automatically
df1 = pd.DataFrame({'var1': [...], 'var2': [...], ...})
df2 = pd.DataFrame({'var1': [...], 'var2': [...], ...})

result = rthor.rthor_test([df1, df2], order="circular6")
```

### File Input

```python
# Text file with lower triangular matrices
result = rthor.rthor_test(
    "correlations.txt",
    n_matrices=10,
    n_variables=6,
    order="circular6"
)
```

File format: Lower triangular matrices including diagonal, whitespace-separated values.

## Preset Orderings

rthor includes two preset orderings for common circumplex models:

### circular6

For 6 variables arranged in a circular pattern (e.g., interpersonal circumplex):

```python
result = rthor.rthor_test(matrix, order="circular6")
```

Hypothesizes that adjacent variables have stronger correlations than distant ones.

### circular8

For 8 variables arranged in a circular pattern:

```python
result = rthor.rthor_test(matrix, order="circular8")
```

Commonly used for octant models in personality and emotion research.

## Custom Orderings

You can specify custom hypothesized orderings for any number of variables:

```python
# For 4 variables with linear ordering: 1 < 2 < 3 < 4
custom_order = [1, 2, 3, 2, 3, 3]
result = rthor.rthor_test(matrix, order=custom_order)
```

The ordering vector specifies the expected relationship between all pairs of variables. For k variables, the vector has length k×(k-1)/2.

See the [Advanced Features](examples/advanced-features.py) example for detailed explanation of custom orderings.

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

### To pandas

Results are already in pandas DataFrames:

```python
result = rthor.rthor_test(matrices, order="circular6")

# Filter significant results
sig = result.results[result.results['p_value'] < 0.05]

# Export to CSV
result.results.to_csv("results.csv", index=False)
```

### To Dictionary/JSON

```python
import json

result_dict = result.to_dict()
with open("results.json", "w") as f:
    json.dump(result_dict, f, indent=2)
```

### Integration with Statistical Workflows

```python
# Extract CI values for further analysis
ci_values = result.results['ci'].values

# Get matrix with best fit
best_matrix = result.results.loc[result.results['ci'].idxmax(), 'label']

# Compare groups
group1_ci = result.results.loc[result.results['label'].str.contains('Group1'), 'ci']
group2_ci = result.results.loc[result.results['label'].str.contains('Group2'), 'ci']
```

## Performance Notes

- Vectorized operations using NumPy for efficiency
- Optimized for matrices with 4-20 variables
- Memory-efficient permutation algorithm
- Pre-computed correlations recommended for repeated analyses

## See Also

- [Basic Usage Example](examples/basic-usage.py) - Getting started guide
- [Advanced Features](examples/advanced-features.py) - Custom orderings, comparisons
- [User Guide](user-guide/concepts.md) - Theoretical background
- [Input Formats Guide](user-guide/input-formats.md) - Detailed data preparation
