# Interpreting Results

This guide explains how to interpret RTHOR results and extract meaningful insights from your analyses.

## Result Object Structure

The `RTHORResult` object contains all analysis outputs:

```python
import pythor

result = pythor.rthor_test(matrices, order="circular6")

# Main results DataFrame
print(result.results)

# Metadata
print(f"Analyzed {result.n_matrices} matrices")
print(f"Variables per matrix: {result.n_variables}")
print(f"Hypothesized ordering: {result.order}")
print(f"Number of predictions: {result.n_predictions}")
print(f"Permutations: {result.n_permutations}")
```

## Results DataFrame

The main results are in a pandas DataFrame with these columns:

### Column Descriptions

| Column        | Type  | Description                                              |
| ------------- | ----- | -------------------------------------------------------- |
| `matrix`      | int   | Matrix identifier (1-indexed)                            |
| `predictions` | int   | Total number of hypothesized predictions tested          |
| `agreements`  | int   | Number of predictions satisfied by the data              |
| `ties`        | int   | Number of tied correlations (neither agree nor disagree) |
| `ci`          | float | Correspondence Index (-1 to +1)                          |
| `p_value`     | float | Statistical significance (from permutation test)         |
| `label`       | str   | Descriptive label for the matrix                         |

### Example Output

```python
   matrix  predictions  agreements  ties        ci  p_value        label
0       1           15          14     0  0.866667   0.0002  Strong Pattern
1       2           15          11     0  0.466667   0.0234  Moderate Pattern
2       3           15           8     0  0.066667   0.3012  Weak Pattern
```

## Understanding the Correspondence Index (CI)

### What is CI?

The Correspondence Index measures agreement between your hypothesis and the data:

$$
CI = \frac{\text{agreements} - \text{disagreements}}{\text{total predictions}}
$$

### Interpreting CI Values

| CI Range   | Interpretation   | Action                                  |
| ---------- | ---------------- | --------------------------------------- |
| 0.8 - 1.0  | Excellent fit    | Strong support for hypothesis           |
| 0.6 - 0.8  | Good fit         | Moderate to strong support              |
| 0.4 - 0.6  | Fair fit         | Some support, but consider alternatives |
| 0.2 - 0.4  | Poor fit         | Weak support                            |
| -0.2 - 0.2 | No fit           | No better than chance                   |
| < -0.2     | Opposite pattern | Data contradicts hypothesis             |

### Factors Affecting CI

1. **Number of variables**: More variables → more predictions → harder to achieve high CI
2. **Correlation strength**: Stronger correlations → clearer patterns → higher CI
3. **Hypothesis complexity**: Simpler patterns easier to detect
4. **Sample size** (for DataFrame input): Smaller N → noisier correlations → lower CI

### Example Interpretation

```python
result = pythor.rthor_test(matrix, order="circular6")
ci = result.results['ci'].iloc[0]

if ci > 0.7:
    print(f"Strong support for circular structure (CI = {ci:.3f})")
elif ci > 0.4:
    print(f"Moderate support for circular structure (CI = {ci:.3f})")
elif ci > 0.0:
    print(f"Weak support for circular structure (CI = {ci:.3f})")
else:
    print(f"No support for circular structure (CI = {ci:.3f})")
```

## Understanding p-values

### What is the p-value?

The p-value represents: "What is the probability of observing a CI this high (or higher) if there were no true pattern?"

Computed via permutation test:

1. Randomly permute variable labels 5000 times
2. Recompute CI for each permutation
3. p-value = proportion of permutations with CI ≥ observed CI

### Interpreting p-values

| p-value     | Interpretation                       |
| ----------- | ------------------------------------ |
| < 0.001     | Very strong evidence                 |
| < 0.01      | Strong evidence                      |
| < 0.05      | Significant (conventional threshold) |
| 0.05 - 0.10 | Marginal evidence                    |
| > 0.10      | No significant evidence              |

### Important Notes

!!! warning "Multiple Testing"

    If testing many matrices, adjust for multiple comparisons:

    ```python
    from statsmodels.stats.multitest import multipletests

    p_values = result.results['p_value'].values
    reject, p_adjusted, _, _ = multipletests(p_values, method='bonferroni')
    result.results['p_adjusted'] = p_adjusted
    ```

!!! tip "Effect Size vs. Significance"

    A significant p-value doesn't mean strong effect. Always check CI:

    - p = 0.001, CI = 0.2: Significant but weak effect
    - p = 0.04, CI = 0.8: Marginally significant but strong effect

!!! note "Reproducibility"

    p-values depend on random permutations. For reproducibility:

    ```python
    import numpy as np
    np.random.seed(42)
    result = pythor.rthor_test(matrix, order="circular6")
    ```

## Agreements and Predictions

### Understanding the Ratio

The raw counts provide additional insight:

```python
predictions = result.results['predictions'].iloc[0]
agreements = result.results['agreements'].iloc[0]
ratio = agreements / predictions

print(f"{agreements}/{predictions} predictions satisfied ({ratio:.1%})")
```

**Interpretation**:

- **90%+ agreements**: Excellent fit
- **70-90% agreements**: Good fit
- **50-70% agreements**: Fair fit
- **<50% agreements**: Poor fit

### Ties

Tied correlations are counted separately:

```python
ties = result.results['ties'].iloc[0]
print(f"{ties} ties (neither agree nor disagree)")
```

**Interpretation**:

- **Few ties** (<10%): Clear patterns in data
- **Many ties** (>20%): Weak or ambiguous patterns

**Note**: Ties are excluded from CI calculation (treated as neither agreement nor disagreement).

## Working with Multiple Matrices

### Comparing Results

```python
# Test multiple matrices
result = pythor.rthor_test(matrices, order="circular6",
                          labels=["Control", "Treatment A", "Treatment B"])

# Sort by fit quality
sorted_results = result.results.sort_values('ci', ascending=False)
print("Best to worst fit:")
print(sorted_results[['label', 'ci', 'p_value']])

# Filter significant results
significant = result.results[result.results['p_value'] < 0.05]
print(f"\n{len(significant)} of {result.n_matrices} matrices showed significant fit")

# Compare groups
control_ci = result.results.loc[result.results['label'] == 'Control', 'ci'].iloc[0]
treatment_ci = result.results.loc[result.results['label'] == 'Treatment A', 'ci'].iloc[0]
print(f"\nCI difference: {treatment_ci - control_ci:.3f}")
```

### Statistical Tests on CIs

To formally test differences between groups:

```python
from scipy import stats

# Extract CIs for each group
group1_cis = result.results[result.results['label'].str.contains('Group1')]['ci']
group2_cis = result.results[result.results['label'].str.contains('Group2')]['ci']

# t-test
t_stat, p_val = stats.ttest_ind(group1_cis, group2_cis)
print(f"t({len(group1_cis) + len(group2_cis) - 2}) = {t_stat:.3f}, p = {p_val:.4f}")

# Effect size (Cohen's d)
pooled_std = np.sqrt(((len(group1_cis)-1)*group1_cis.std()**2 +
                      (len(group2_cis)-1)*group2_cis.std()**2) /
                     (len(group1_cis) + len(group2_cis) - 2))
cohens_d = (group1_cis.mean() - group2_cis.mean()) / pooled_std
print(f"Cohen's d = {cohens_d:.3f}")
```

## Pairwise Comparisons

The `compare_matrices()` function provides additional insights:

```python
comparison = pythor.compare_matrices(matrices, order="circular6")

# Individual RTHOR results
print(comparison.rthor_results)

# Pairwise comparisons
print(comparison.comparisons)
```

### Comparison Results

The `comparisons` DataFrame includes:

| Column       | Description                            |
| ------------ | -------------------------------------- |
| `matrix1`    | First matrix identifier                |
| `matrix2`    | Second matrix identifier               |
| `both_agree` | Predictions satisfied by both matrices |
| `only1`      | Predictions satisfied only by matrix 1 |
| `only2`      | Predictions satisfied only by matrix 2 |
| `neither`    | Predictions satisfied by neither       |
| `ci`         | Comparison CI                          |
| `p_value`    | Significance of difference             |

### Interpreting Comparison CI

```python
comp_ci = comparison.comparisons.loc[0, 'ci']

if comp_ci > 0.2:
    print("Matrix 2 fits significantly better")
elif comp_ci < -0.2:
    print("Matrix 1 fits significantly better")
else:
    print("Matrices have similar fit")
```

## Visualization

### CI Distribution

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
result.results.plot(kind='bar', x='label', y='ci', ax=ax, legend=False)
ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
ax.set_ylabel('Correspondence Index')
ax.set_xlabel('Matrix')
ax.set_title('RTHOR Results: Fit to Circular Hypothesis')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### Scatter Plot: CI vs. p-value

```python
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(result.results['ci'], result.results['p_value'], alpha=0.6)
ax.axvline(x=0, color='k', linestyle='--', linewidth=0.5)
ax.axhline(y=0.05, color='r', linestyle='--', linewidth=0.5, label='p = 0.05')
ax.set_xlabel('Correspondence Index')
ax.set_ylabel('p-value')
ax.set_title('Effect Size vs. Statistical Significance')
ax.legend()
plt.tight_layout()
plt.show()
```

### Agreement Proportions

```python
result.results['agreement_proportion'] = (
    result.results['agreements'] / result.results['predictions']
)

fig, ax = plt.subplots(figsize=(10, 6))
result.results.plot(kind='bar', x='label', y='agreement_proportion',
                   ax=ax, legend=False, color='steelblue')
ax.set_ylabel('Proportion of Predictions Satisfied')
ax.set_xlabel('Matrix')
ax.set_title('Proportion of Hypothesized Predictions Satisfied')
ax.set_ylim(0, 1)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## Exporting Results

### To CSV

```python
# Export main results
result.results.to_csv('rthor_results.csv', index=False)

# Export with additional columns
enriched_results = result.results.copy()
enriched_results['agreement_proportion'] = (
    enriched_results['agreements'] / enriched_results['predictions']
)
enriched_results.to_csv('rthor_results_detailed.csv', index=False)
```

### To JSON

```python
import json

# Convert to dictionary
result_dict = result.to_dict()

# Save to file
with open('rthor_results.json', 'w') as f:
    json.dump(result_dict, f, indent=2)

# For comparisons
comparison_dict = comparison.to_dict()
with open('rthor_comparison.json', 'w') as f:
    json.dump(comparison_dict, f, indent=2)
```

### To LaTeX

```python
# Create LaTeX table
latex_table = result.results.to_latex(
    columns=['label', 'ci', 'p_value'],
    float_format='%.3f',
    index=False,
    caption='RTHOR Analysis Results',
    label='tab:rthor_results'
)

with open('rthor_table.tex', 'w') as f:
    f.write(latex_table)
```

## Reporting Results

### Example Write-Up

> We tested whether the observed correlation matrices conformed to a hypothesized
> circular ordering of six variables using the Randomization Test of Hypothesized
> Order Relations (RTHOR; Hubert & Arabie, 1987). The analysis was conducted using
> pythor (version 0.1.0).
>
> The control group showed strong support for the circular structure
> (CI = 0.87, p < .001), with 14 of 15 (93%) hypothesized predictions satisfied.
> Treatment Group A showed moderate support (CI = 0.47, p = .023), with 11 of 15
> (73%) predictions satisfied. Treatment Group B showed no significant support
> (CI = 0.07, p = .301), with only 8 of 15 (53%) predictions satisfied.
>
> These results suggest that the treatment disrupted the circular organization
> present in the control condition.

## Next Steps

- Review [Core Concepts](concepts.md) for theoretical background
- See [Advanced Features](../examples/advanced-features.md) for complex analyses
- Check [API Reference](../api.md) for function details
- Try the [interactive notebooks](../examples/basic-usage.md)
