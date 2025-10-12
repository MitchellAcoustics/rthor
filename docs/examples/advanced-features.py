# %% [markdown]
# # Advanced Features
#
# This notebook demonstrates advanced features including custom orderings, working with DataFrames, and pairwise matrix comparisons.

# %%
import numpy as np
import pandas as pd

import rthor

# %% [markdown]
# ## Custom Orderings
#
# While rthor provides preset orderings like "circular6" and "circular8", you can specify custom hypothesized orderings for any number of variables.
#
# The ordering is specified as a vector where each element represents the hypothesized relationship between pairs of variables.

# %% [markdown]
# ### Example: 4-Variable Linear Ordering
#
# Let's create a custom ordering for 4 variables arranged linearly: Variable 1 < Variable 2 < Variable 3 < Variable 4
#
# For 4 variables, we have 4×(4-1)/2 = 6 pairwise comparisons.

# %%
# Create a correlation matrix with linear structure
corr_linear = np.array(
    [
        [1.00, 0.80, 0.60, 0.40],
        [0.80, 1.00, 0.75, 0.55],
        [0.60, 0.75, 1.00, 0.70],
        [0.40, 0.55, 0.70, 1.00],
    ]
)

# Custom ordering: [1,2,1] means:
# - Pair (1,2): Expect corr(1,2) > corr(1,3)  → order value 1
# - Pair (1,3): Expect corr(1,3) > corr(1,4)  → order value 2
# - Pair (1,4): ...and so on
#
# For a simple linear order (1<2<3<4), a common pattern is:
custom_order = [1, 2, 3, 2, 3, 3]

result_custom = rthor.test(corr_linear, order=custom_order)
result_custom.summary(print_table=True)

# %% [markdown]
# ## Working with DataFrames
#
# rthor can work directly with pandas DataFrames containing raw data. It will compute the correlation matrices automatically.

# %%
# Create sample datasets
np.random.seed(42)

# Dataset 1: Strong circular structure
n_samples = 100
angles = np.linspace(0, 2 * np.pi, 6, endpoint=False)

data1 = pd.DataFrame(
    {
        f"var{i + 1}": np.sin(angles[i]) + np.random.normal(0, 0.3, n_samples)
        for i in range(6)
    }
)

# Dataset 2: Weaker circular structure (more noise)
data2 = pd.DataFrame(
    {
        f"var{i + 1}": np.sin(angles[i]) + np.random.normal(0, 0.6, n_samples)
        for i in range(6)
    }
)

# Dataset 3: Random (no structure)
data3 = pd.DataFrame(
    {f"var{i + 1}": np.random.normal(0, 1, n_samples) for i in range(6)}
)

data1.head()

# %%
# Test DataFrames
result_dfs = rthor.test(
    [data1, data2, data3],
    order="circular6",
    labels=["Strong Structure", "Weak Structure", "Random"],
)
result_dfs.summary(print_table=True)

# %% [markdown]
# Notice how the CI values and p-values reflect the strength of the circular structure in each dataset.

# %% [markdown]
# ## Pairwise Matrix Comparisons
#
# The `compare()` function performs two analyses:
#
# 1. Individual RTHOR tests for each matrix
# 2. Pairwise comparisons to determine which matrix fits better

# %%
# Compare matrices pairwise
individual, pairwise = rthor.compare([data1, data2, data3], order="circular6")

# %% [markdown]
# ### Individual Results
#
# First, let's look at how each matrix performed individually:

# %%
individual.round(3)

# %% [markdown]
# ### Pairwise Comparisons
#
# Now let's see the pairwise comparisons:
#
# - **both_agree**: Predictions satisfied by both matrices
# - **only1**: Predictions satisfied only by matrix 1
# - **only2**: Predictions satisfied only by matrix 2
# - **neither**: Predictions satisfied by neither
# - **ci**: Comparison CI (positive means matrix 2 fits better)
# - **p_value**: Significance of the difference

# %%
pairwise.round(3)

# %% [markdown]
# ## Reading from Files
#
# For large-scale analyses, you can read correlation matrices from text files:
#
# ```python
# result = rthor.test(
#     "correlations.txt",
#     n_matrices=10,
#     n_variables=6,
#     order="circular6"
# )
# ```
#
# The file should contain lower triangular matrices (including diagonal) with values separated by whitespace.

# %% [markdown]
# ## Export Results
#
# Results can be easily exported for further analysis:
#
# ```python
# # To CSV
# result.results.to_csv("rthor_results.csv", index=False)
#
# # To dictionary (for JSON)
# result_dict = result.to_dict()
#
# # Get specific statistics
# significant_matrices = result.results[result.results['p_value'] < 0.05]
# ```

# %% [markdown]
# ## Next Steps
#
# - Explore the [API Reference](../api.md) for complete function documentation
# - Read the [User Guide](../user-guide/concepts.md) for theoretical background
# - Check the [Input Formats](../user-guide/input-formats.md) guide for data preparation

# %%
