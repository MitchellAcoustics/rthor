# Basic Usage

This example demonstrates the fundamental features of pythor for testing correlation matrices.

## Interactive Notebook

@@@marimo notebooks/basic_usage.py

## Key Concepts

### Testing Single Matrices

The simplest use case is testing a single correlation matrix:

```python
import pythor
import numpy as np

# Your correlation matrix
corr_matrix = np.array([...])

# Test against circular6 preset
result = pythor.rthor_test(corr_matrix, order="circular6")
print(result.summary())
```

### Testing Multiple Matrices

You can test multiple matrices simultaneously:

```python
# Stack matrices into 3D array or use list of DataFrames
result = pythor.rthor_test(
    matrices,
    order="circular6",
    labels=["Group 1", "Group 2", "Group 3"]
)
```

### Understanding the Correspondence Index (CI)

The CI measures how well the data fits the hypothesized ordering:

- **CI = 1.0**: Perfect agreement
- **CI = 0.0**: No better than chance
- **CI = -1.0**: Perfect disagreement

### Interpreting p-values

The p-value indicates statistical significance:

- **p < 0.05**: Significant fit (conventional threshold)
- **p < 0.01**: Strong fit
- **p < 0.001**: Very strong fit

## Common Use Cases

### Circumplex Models

RTHOR is commonly used to test circumplex models in psychology:

- Interpersonal behavior (e.g., IPC octants)
- Emotional experience
- Personality traits

### Custom Orderings

You can specify custom hypothesized orderings for any theoretical model.
See the [Advanced Features](advanced-features.md) example for details.
