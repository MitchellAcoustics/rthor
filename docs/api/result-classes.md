# Results and Formatting

## DataFrame Results

Both [`rthor_test()`][rthor.rthor_test] and [`compare_matrices()`][rthor.compare_matrices] return pandas DataFrames containing all test results and metadata.

### rthor_test() Returns

A single DataFrame with columns:

- **`matrix`**: Matrix identifier (1-indexed)
- **`predictions`**: Number of hypothesized predictions
- **`agreements`**: Number of predictions satisfied
- **`ties`**: Number of tied correlations
- **`ci`**: Correspondence Index (-1 to +1)
- **`p_value`**: Randomization test p-value
- **`label`**: Descriptive label for matrix
- **`n_permutations`**: Number of permutations tested
- **`n_variables`**: Number of variables per matrix

Each row represents one tested matrix. Metadata columns (`n_permutations`, `n_variables`) are repeated for tidy data principles.

### compare_matrices() Returns

A tuple of two DataFrames: `(individual_results, pairwise_comparisons)`

**individual_results** has the same structure as rthor_test() output.

**pairwise_comparisons** DataFrame columns:

- **`matrix1`**, **`matrix2`**: Matrix identifiers being compared
- **`both_agree`**: Predictions satisfied by both matrices
- **`only1`**: Predictions satisfied only by matrix 1
- **`only2`**: Predictions satisfied only by matrix 2
- **`neither`**: Predictions satisfied by neither
- **`ci`**: Comparison CI (positive means matrix 2 fits better)
- **`p_value`**: Statistical significance of difference
- **`n_permutations`**, **`n_variables`**: Metadata columns

## Formatting Functions

Optional functions for pretty-printing results:

### [`print_results()`][rthor.print_results]

Print formatted table of rthor_test() results:

```python
import rthor

df = rthor.rthor_test(data, order="circular6")
rthor.print_results(df)  # Pretty-print the results
```

Or use the convenience parameter:

```python
df = rthor.rthor_test(data, order="circular6", print_results=True)
```

### [`print_comparison()`][rthor.print_comparison]

Print formatted tables for comparison results:

```python
individual, pairwise = rthor.compare_matrices(data, order="circular6")
rthor.print_comparison(individual, pairwise)
```

Or use the convenience parameter:

```python
individual, pairwise = rthor.compare_matrices(
    data, order="circular6", print_results=True
)
```

Both functions support rich formatting (if the `rich` package is installed) or plain text.

## Working with DataFrames

Since results are standard pandas DataFrames, you can use all pandas functionality:

```python
# Filter significant results
significant = df[df['p_value'] < 0.05]

# Export to various formats
df.to_csv("results.csv")
df.to_excel("results.xlsx")
df.to_latex("results.tex")

# Get specific values
n_perms = df['n_permutations'].iloc[0]
mean_ci = df['ci'].mean()

# Plotting
import matplotlib.pyplot as plt
df.plot.bar(x='label', y='ci')
```

<!-- prettier-ignore -->
::: rthor.formatting.print_results
:::

<!-- prettier-ignore -->
::: rthor.formatting.print_comparison
:::
