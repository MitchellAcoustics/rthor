# Core Concepts

## What is RTHOR?

RTHOR (Randomization Test of Hypothesized Order Relations) is a statistical test for evaluating whether correlation matrices conform to theoretically predicted patterns, particularly circumplex and circular structures.

Developed by Hubert & Arabie (1987), RTHOR is widely used in personality, emotion, and interpersonal research to validate circumplex models.

## The Circumplex Problem

Many psychological constructs organize in circular patterns (circumplexes):

- **Interpersonal behavior**: Dominance-submission and affiliation dimensions
- **Emotions**: Valence and arousal dimensions
- **Personality traits**: Various two-dimensional models

In a circumplex:

- Variables are arranged in a circle
- **Adjacent** variables have strong positive correlations
- **Opposite** variables have weak or negative correlations
- **Intermediate** distances have intermediate correlations

Traditional methods like exploratory factor analysis don't directly test whether data follow a hypothesized circular ordering. RTHOR provides a formal statistical test for this.

## How RTHOR Works

### 1. Specify Order Hypotheses

You define predictions about relative correlation magnitudes. For example, in a 6-variable circumplex:

- Adjacent pairs (1-2, 2-3, ..., 6-1) should have **highest** correlations
- Alternate pairs (1-3, 2-4, ...) should have **intermediate** correlations
- Opposite pairs (1-4, 2-5, 3-6) should have **lowest** correlations

This creates a set of **order predictions** comparing all pairs of variable-pairs.

### 2. Count Agreements

RTHOR counts how many predictions are satisfied by observed data:

- **Agreement**: Predicted order matches observed order
- **Disagreement**: Predicted order contradicts observed order
- **Tie**: Correlations are equal

### 3. Compute Correspondence Index (CI)

The CI summarizes fit (Hubert & Arabie, 1987, Eq. 3, p. 176):

$$
CI = \frac{A - D}{A + D + T}
$$

Where:

- **A** = agreements
- **D** = disagreements
- **T** = ties

**Range**: -1 (perfect disagreement) to +1 (perfect agreement)

### 4. Permutation Test

Statistical significance is determined by randomization (Hubert & Arabie, 1987, p. 175):

1. Generate all permutations of variable labels (or sample when n! > 50,000)
2. For each permutation, recompute CI
3. p-value = proportion of permutations with CI ≥ observed

This tests: "Is the observed fit better than chance?"

The key insight: By permuting object labels (not individual predictions), the test preserves the structural integrity of order relations while providing a valid null distribution.

## Interpreting Results

### Correspondence Index (CI)

**General guidelines**:

- **CI > 0.7**: Strong support for hypothesis
- **CI = 0.4-0.7**: Moderate support
- **CI < 0.4**: Weak support
- **CI ≈ 0**: No better than chance
- **CI < 0**: Data contradicts hypothesis

**Important**: CI values depend on number of variables, correlation strength, and hypothesis complexity.

### p-values

**Conventional thresholds**:

- **p < 0.05**: Significant support
- **p < 0.01**: Strong support
- **p < 0.001**: Very strong support

**Interpretation**: Probability of obtaining CI this high (or higher) by chance alone.

## The Ordering Vector

The ordering vector encodes your hypothesis. For n variables, it has length n(n-1)/2 (one value per unique pair).

### Example: Circular6

For a 6-variable circumplex:

```text
        1
      6   2
     5     3
        4
```

The preset `circular6 = [1, 2, 3, 2, 1, 1, 2, 3, 2, 1, 2, 3, 1, 2, 1]` encodes:

- Pairs with value 1: Adjacent pairs (strongest correlations)
- Pairs with value 2: Alternate pairs (intermediate)
- Pairs with value 3: Opposite pairs (weakest)

Lower numbers = predicted higher correlations.

## Common Applications

### Interpersonal Circumplex (IPC)

Test if interpersonal scales follow the classic two-dimensional circular structure:

```python
result = rthor.rthor_test(ipc_matrix, order="circular8")
```

### Affect Circumplex

Test Russell's (1980) circumplex model of emotions:

```python
result = rthor.rthor_test(emotion_matrix, order="circular8")
```

### Custom Models

Test any hypothesized ordering:

```python
# Linear ordering: 1 < 2 < 3 < 4
custom_order = [1, 2, 3, 2, 3, 3]
result = rthor.rthor_test(matrix, order=custom_order)
```

## Method Advantages

1. **Theory-driven**: Directly tests theoretical predictions
2. **Distribution-free**: No parametric assumptions (permutation test)
3. **Flexible**: Works with any hypothesized ordering
4. **Interpretable**: CI provides intuitive effect size
5. **Validated**: Exact parity with R implementation

## References

**Original Method:**

- Hubert, L. J., & Arabie, P. (1987). Evaluating order hypotheses within proximity matrices. _Psychological Bulletin_, 102(1), 172-178. <https://doi.org/10.1037/0033-2909.102.1.172>

**R Implementation:**

- Gurtman, M. B. (2021). RTHORR: Randomization Tests of Hypothesized Order Relations [R package].

**Applications:**

- Gurtman, M. B., & Pincus, A. L. (2003). The circumplex model: Methods and research applications. In _Handbook of psychology_ (pp. 407-428).
- Browne, M. W. (1992). Circumplex models for correlation matrices. _Psychometrika_, 57(4), 469-497.

## Next Steps

- See [Paper Validation](../examples/paper-validation.py) - Verification against Hubert & Arabie (1987)
- Try [Basic Usage](../examples/basic-usage.py) - Getting started examples
- Explore [Advanced Features](../examples/advanced-features.py) - Custom orderings and comparisons
- Check [API Reference](../api/reference/input.md) - Complete function documentation
