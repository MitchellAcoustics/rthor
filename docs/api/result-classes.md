# Result Classes

## RTHORResult

The main result object returned by [`rthor_test()`][rthor.rthor_test]. Key attributes:

- **`results`**: Pandas DataFrame with test results for each matrix
- **`n_matrices`**: Number of matrices tested
- **`n_variables`**: Number of variables per matrix
- **`order`**: The hypothesized ordering used
- **`n_predictions`**: Total number of predictions tested
- **`n_permutations`**: Number of permutations (default: 5000)

Methods:

- [**`summary()`**][rthor.RTHORResult.summary]: Get formatted summary string
- [**`to_dict()`**][rthor.RTHORResult.to_dict]: Convert to dictionary (useful for JSON export)

<!-- prettier-ignore -->
::: rthor.RTHORResult
:::

## ComparisonResult

Result object for pairwise matrix comparisons from `compare_matrices()`. Key attributes:

- **`rthor_results`**: pandas DataFrame with individual RTHOR results
- **`comparisons`**: pandas DataFrame with pairwise comparison results
- **`n_matrices`**: Number of matrices compared
- **`n_variables`**: Number of variables per matrix
- **`order`**: The hypothesized ordering used

The [`comparisons`][rthor.ComparisonResult.comparisons] DataFrame includes:

- [**`both_agree`**][rthor.ComparisonResult.comparisons.both_agree]: Predictions satisfied by both matrices
- [**`only1`**][rthor.ComparisonResult.comparisons.only1]: Predictions satisfied only by matrix 1
- [**`only2`**][rthor.ComparisonResult.comparisons.only2]: Predictions satisfied only by matrix 2
- [**`neither`**][rthor.ComparisonResult.comparisons.neither]: Predictions satisfied by neither
- [**`ci`**][rthor.ComparisonResult.comparisons.ci]: Comparison CI (positive means matrix 2 fits better)
- [**`p_value`**][rthor.ComparisonResult.comparisons.p_value]: Statistical significance of difference

Methods:

- [**`summary()`**][rthor.ComparisonResult.summary]: Get formatted summary string
- [**`to_dict()`**][rthor.ComparisonResult.to_dict]: Convert to dictionary (useful for JSON export)

::: rthor.ComparisonResult
:::
