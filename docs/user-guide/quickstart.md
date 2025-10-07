# Quick Start

This guide walks you through your first RTHOR analysis with pythor.

## Basic Workflow

1. Prepare your correlation matrix or raw data
2. Choose or define a hypothesized ordering
3. Run the test
4. Interpret results

## Your First Analysis

### Example: Testing a Circumplex Structure

Let's test whether a correlation matrix follows a circular (circumplex) pattern with 6 variables:

```python
import numpy as np
import pythor

# Create a correlation matrix with circular structure
# Variables 1-6 arranged in a circle
corr_matrix = np.array([
    [1.00, 0.80, 0.50, 0.20, 0.40, 0.70],
    [0.80, 1.00, 0.75, 0.45, 0.30, 0.55],
    [0.50, 0.75, 1.00, 0.80, 0.50, 0.35],
    [0.20, 0.45, 0.80, 1.00, 0.75, 0.40],
    [0.40, 0.30, 0.50, 0.75, 1.00, 0.70],
    [0.70, 0.55, 0.35, 0.40, 0.70, 1.00]
])

# Test against circular6 preset
result = pythor.rthor_test(corr_matrix, order="circular6")

# View summary
print(result.summary())
```

Output:

```text
RTHOR Analysis Summary
======================
Matrices analyzed: 1
Variables per matrix: 6
Hypothesized ordering: [1, 2, 3, 3, 2, 2, 3, 2, 1, 1, 2, 3, 2, 1, 3]
Number of predictions: 15
Permutations: 5000

Results:
   matrix  predictions  agreements  ties        ci  p_value  label
0       1           15          13     0  0.733333   0.0012  Matrix 1
```

**Interpretation**: The Correspondence Index (CI) of 0.73 indicates strong agreement with the circular hypothesis, and the p-value of 0.0012 shows this is statistically significant.

## Working with Raw Data

If you have raw data instead of correlation matrices, pythor can compute correlations automatically:

```python
import pandas as pd
import numpy as np

# Simulate raw data for 6 variables
np.random.seed(42)
n_samples = 100
angles = np.linspace(0, 2 * np.pi, 6, endpoint=False)

data = pd.DataFrame({
    f'var{i+1}': np.sin(angles[i]) + np.random.normal(0, 0.3, n_samples)
    for i in range(6)
})

# Test directly - correlations computed automatically
result = pythor.rthor_test(data, order="circular6", labels=["My Data"])
print(result.summary())
```

## Testing Multiple Matrices

Compare multiple correlation matrices at once:

```python
# Create three matrices with varying fit
matrix1 = corr_matrix  # Strong circular pattern
matrix2 = 0.8 * corr_matrix + 0.2 * np.eye(6)  # Moderate pattern
matrix3 = np.eye(6) + np.random.normal(0, 0.1, (6, 6))  # Weak pattern
matrix3 = (matrix3 + matrix3.T) / 2  # Make symmetric

# Stack into 3D array (shape: [n_vars, n_vars, n_matrices])
matrices = np.stack([matrix1, matrix2, matrix3], axis=2)

# Test all at once
result = pythor.rthor_test(
    matrices,
    order="circular6",
    labels=["Strong", "Moderate", "Weak"]
)

print(result.summary())
```

## Accessing Detailed Results

Results are stored in a pandas DataFrame for easy analysis:

```python
# Get results as DataFrame
df = result.results
print(df)

# Filter significant results
significant = df[df['p_value'] < 0.05]
print(f"Found {len(significant)} significant matrices")

# Get best fitting matrix
best = df.loc[df['ci'].idxmax()]
print(f"Best fit: {best['label']} (CI = {best['ci']:.3f})")

# Export to CSV
df.to_csv('rthor_results.csv', index=False)
```

## Comparing Matrices

To determine which matrix fits better:

```python
# Pairwise comparisons
comparison = pythor.compare_matrices(matrices, order="circular6")

print(comparison.summary())

# View individual results
print(comparison.rthor_results)

# View pairwise comparisons
print(comparison.comparisons)
```

The comparison CI tells you:

- **CI > 0**: Matrix 2 fits better
- **CI < 0**: Matrix 1 fits better
- **CI ≈ 0**: Similar fit

## Common Use Cases

### Case 1: Interpersonal Circumplex

Testing if interpersonal scales follow a circular pattern:

```python
# 8 interpersonal variables (octants)
ipc_matrix = ...  # Your correlation matrix

result = pythor.rthor_test(ipc_matrix, order="circular8")
```

### Case 2: Custom Hypothesis

Testing a specific linear ordering:

```python
# Hypothesis: Variable 1 < 2 < 3 < 4 in correlation strength
custom_order = [1, 2, 3, 2, 3, 3]  # Ordering for 4 variables

result = pythor.rthor_test(matrix, order=custom_order)
```

### Case 3: File Input

Processing many matrices from a file:

```python
result = pythor.rthor_test(
    "correlations.txt",
    n_matrices=100,
    n_variables=6,
    order="circular6"
)

# Find significant cases
sig = result.results[result.results['p_value'] < 0.05]
print(f"{len(sig)} of {result.n_matrices} matrices showed significant fit")
```

## Understanding Output Columns

- **matrix**: Matrix identifier (1-indexed)
- **predictions**: Total number of hypothesized predictions
- **agreements**: Number of predictions satisfied by the data
- **ties**: Number of tied correlations (neither agree nor disagree)
- **ci**: Correspondence Index (-1 to +1, higher = better fit)
- **p_value**: Statistical significance from permutation test
- **label**: Descriptive label for the matrix

## Next Steps

Now that you understand the basics:

- Learn about [Core Concepts](concepts.md) - Theory behind RTHOR
- Explore [Input Formats](input-formats.md) - Data preparation details
- See [Advanced Features](../examples/advanced-features.py) - Custom orderings and comparisons
- Check [API Reference](../api.md) - Complete function documentation

## Common Pitfalls

!!! warning "Matrix Shape"

    When stacking multiple matrices, use `axis=2`: `np.stack([m1, m2], axis=2)`.
    This creates shape `[n_vars, n_vars, n_matrices]`.

!!! warning "Correlation Validity"

    Ensure correlation matrices are:

    - Symmetric
    - Have 1.0 on diagonal
    - Have values between -1 and 1

!!! tip "Performance"

    For large datasets, pre-compute correlations once and reuse them for multiple analyses.

!!! tip "Reproducibility"

    For reproducible p-values, use `np.random.seed()` before running tests, as the permutation order affects results.
