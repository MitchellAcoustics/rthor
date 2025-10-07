# Core Concepts

## What is RTHOR?

RTHOR (Randomization Test of Hypothesized Order Relations) is a statistical test for evaluating whether correlation matrices conform to theoretically predicted patterns, particularly circumplex and circular structures.

Developed by Hubert & Arabie (1987), RTHOR is widely used in personality, emotion, and interpersonal research to validate circumplex models.

## The Problem RTHOR Solves

### Circumplex Models

Many psychological constructs are organized in circular patterns (circumplexes):

- **Interpersonal behavior**: Dominance-submission, love-hate dimensions
- **Emotions**: Pleasure-displeasure, arousal-calmness
- **Personality traits**: Various two-dimensional models

In a circumplex:

- Variables are arranged in a circle
- **Adjacent** variables have strong positive correlations
- **Opposite** variables have negative correlations
- **Orthogonal** variables (90° apart) have near-zero correlations

### The Challenge

Traditional methods like correlation matrices or factor analysis don't directly test whether your data follows a hypothesized circular ordering. RTHOR provides a formal statistical test for this.

## How RTHOR Works

### 1. Hypothesized Ordering

You specify predictions about the relative magnitudes of correlations. For example, in a 6-variable circumplex:

- r(1,2) > r(1,3) > r(1,4)
- r(2,3) > r(2,4) > r(2,5)
- And so on...

This creates a set of **order predictions** about which correlations should be larger than others.

### 2. Count Agreements

RTHOR counts how many of these predictions are satisfied by your observed correlation matrix:

- **Agreement**: Predicted order matches observed order
- **Disagreement**: Predicted order contradicts observed order
- **Tie**: Correlations are equal (neither agree nor disagree)

### 3. Compute Correspondence Index

The Correspondence Index (CI) summarizes the fit:

$$
CI = \frac{\text{agreements} - \text{disagreements}}{\text{total predictions}}
$$

**Range**: -1 to +1

- **+1**: Perfect agreement with hypothesis
- **0**: No better than random
- **-1**: Perfect disagreement (opposite pattern)

### 4. Permutation Test

To determine if the CI is statistically significant:

1. Randomly permute variable labels (5000 times by default)
2. Recompute CI for each permutation
3. p-value = proportion of permutations with CI ≥ observed CI

This tests: "Is our observed fit better than random chance?"

## Understanding the Ordering Vector

The ordering vector is the heart of your hypothesis. It specifies predicted relationships between **all pairs** of variables.

### Example: 4 Variables

For 4 variables, there are 4×(4-1)/2 = 6 pairs:

1. (1,2)
2. (1,3)
3. (1,4)
4. (2,3)
5. (2,4)
6. (3,4)

A **linear ordering** (1 < 2 < 3 < 4) predicts:

- r(1,2) > r(1,3) > r(1,4)
- r(2,3) > r(2,4)
- r(3,4) > others...

This is encoded as: `[1, 2, 3, 2, 3, 3]`

Each number represents the hypothesized "rank" or "tier" of that pair's correlation strength.

### Circular Orderings

For a 6-variable circumplex:

```text
    1
  6   2
 5     3
    4
```

Adjacent pairs (1-2, 2-3, ..., 6-1) should have the strongest correlations, followed by pairs separated by one (1-3, 2-4, ...), then opposite pairs (1-4, 2-5, 3-6).

pythor's `circular6` preset encodes this pattern: `[1, 2, 3, 3, 2, 2, 3, 2, 1, 1, 2, 3, 2, 1, 3]`

## Interpreting Results

### Correspondence Index (CI)

**What it means**:

- **CI > 0.7**: Strong support for hypothesis
- **CI = 0.4-0.7**: Moderate support
- **CI = 0.0-0.4**: Weak support
- **CI < 0**: Data contradicts hypothesis

**Important**: CI values depend on:

- Number of variables (more variables → harder to achieve high CI)
- Strength of correlations (stronger correlations → clearer patterns)
- Complexity of hypothesis (simpler patterns easier to detect)

### p-values

**Statistical significance**:

- **p < 0.05**: Significant support (conventional threshold)
- **p < 0.01**: Strong support
- **p < 0.001**: Very strong support
- **p > 0.05**: No significant support

**Interpretation**: The probability of obtaining this CI (or better) by chance alone.

**Note**: p-values depend on the permutation algorithm's random seed. For exact reproducibility, set `np.random.seed()` before running tests.

### Agreements vs. Predictions

**Ratio matters**:

- 45 agreements out of 50 predictions (90%) = excellent fit
- 45 agreements out of 100 predictions (45%) = poor fit

Always consider both:

- **Absolute count**: How many predictions satisfied?
- **Proportion**: What percentage of predictions satisfied?

The CI automatically accounts for this by normalizing.

## Common Applications

### Interpersonal Circumplex (IPC)

Test if interpersonal scales follow the classic two-dimensional circular structure (Leary, 1957; Wiggins, 1979):

```python
result = pythor.rthor_test(ipc_matrix, order="circular8")
```

### Affect Circumplex

Test Russell's (1980) circumplex model of emotions:

```python
result = pythor.rthor_test(emotion_matrix, order="circular8")
```

### Custom Theoretical Models

Test any hypothesized ordering:

```python
# Hypothesis: Variables form 3 clusters with specific ordering
custom_order = [1, 1, 2, 2, 2, 3, 3, 3, 3, 3]
result = pythor.rthor_test(matrix, order=custom_order)
```

## Advantages of RTHOR

1. **Theory-driven**: Directly tests your theoretical predictions
2. **Distribution-free**: No parametric assumptions (uses permutation test)
3. **Flexible**: Works with any hypothesized ordering
4. **Interpretable**: CI provides intuitive effect size
5. **Validated**: Widely used since 1987, exact R parity in pythor

## Limitations

1. **Pre-specified hypothesis required**: Can't explore patterns post-hoc
2. **Sensitive to violations**: A few strong violations can lower CI substantially
3. **Not a fit index**: Doesn't tell you _how_ to improve your model
4. **Correlation-based**: Assumes linear relationships between variables

## Relationship to Other Methods

### vs. Confirmatory Factor Analysis (CFA)

- **CFA**: Tests a full structural model with loadings and fit indices
- **RTHOR**: Tests only the ordering of correlations (simpler, more focused)

**Use RTHOR when**: You want to test ordinal predictions about correlations without specifying a full measurement model.

### vs. Multidimensional Scaling (MDS)

- **MDS**: Visualizes distances between variables
- **RTHOR**: Statistically tests a specific hypothesis

**Use both**: MDS for exploration, RTHOR for confirmation.

### vs. Correlation Matrix Tests

- **Correlation tests**: Test individual correlations or overall pattern
- **RTHOR**: Tests specific ordering predictions

**RTHOR advantage**: More powerful for detecting circumplex patterns.

## Further Reading

### Original Papers

- Hubert, L. J., & Arabie, P. (1987). Evaluating order hypotheses within proximity matrices. _Psychological Bulletin_, 102(1), 172-178.

### R Implementation

- Yentes, R. D., & Wilhelm, F. (2018). RTHORR: Randomization Test for Hypothesized Order Relations. R package version 1.0.1.

### Applications

- Gurtman, M. B., & Pincus, A. L. (2003). The circumplex model: Methods and research applications. In _Handbook of psychology_ (pp. 407-428).
- Browne, M. W. (1992). Circumplex models for correlation matrices. _Psychometrika_, 57(4), 469-497.

## Next Steps

- See [Input Formats](input-formats.md) for data preparation
- Try [Basic Usage Example](../examples/basic-usage.py)
- Explore [Advanced Features](../examples/advanced-features.py)
- Check [API Reference](../api.md) for function details
