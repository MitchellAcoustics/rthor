# %% [markdown]
# # Basic Usage
#
# This example demonstrates the fundamental features of rthor for testing correlation matrices.

# %% [markdown]
# ## Creating Sample Data
#
# First, let's create some sample correlation matrices. We'll create 3 matrices with 6 variables each, following a circular/circumplex structure.

# %%
import numpy as np

import rthor

# %%
# Create sample correlation matrices that follow a circular pattern
# Variables: 1, 2, 3, 4, 5, 6 arranged in a circle

# Matrix 1: Strong circular pattern
corr_matrix_1 = np.array(
    [
        [1.00, 0.80, 0.50, 0.20, 0.40, 0.70],
        [0.80, 1.00, 0.75, 0.45, 0.30, 0.55],
        [0.50, 0.75, 1.00, 0.80, 0.50, 0.35],
        [0.20, 0.45, 0.80, 1.00, 0.75, 0.40],
        [0.40, 0.30, 0.50, 0.75, 1.00, 0.70],
        [0.70, 0.55, 0.35, 0.40, 0.70, 1.00],
    ]
)

# Matrix 2: Moderate circular pattern
corr_matrix_2 = np.array(
    [
        [1.00, 0.70, 0.45, 0.25, 0.35, 0.65],
        [0.70, 1.00, 0.68, 0.40, 0.28, 0.50],
        [0.45, 0.68, 1.00, 0.72, 0.48, 0.32],
        [0.25, 0.40, 0.72, 1.00, 0.70, 0.38],
        [0.35, 0.28, 0.48, 0.70, 1.00, 0.65],
        [0.65, 0.50, 0.32, 0.38, 0.65, 1.00],
    ]
)

# Matrix 3: Weak circular pattern
corr_matrix_3 = np.array(
    [
        [1.00, 0.60, 0.40, 0.30, 0.35, 0.55],
        [0.60, 1.00, 0.58, 0.42, 0.32, 0.48],
        [0.40, 0.58, 1.00, 0.62, 0.45, 0.35],
        [0.30, 0.42, 0.62, 1.00, 0.60, 0.40],
        [0.35, 0.32, 0.45, 0.60, 1.00, 0.58],
        [0.55, 0.48, 0.35, 0.40, 0.58, 1.00],
    ]
)

# Stack into 3D array
corr_matrices = np.stack([corr_matrix_1, corr_matrix_2, corr_matrix_3], axis=2)

# %% [markdown]
# ## Testing a Single Matrix
#
# Let's test the first correlation matrix against a circular ordering hypothesis. The "circular6" preset specifies that we expect variables 1-6 to be arranged in a circular pattern.

# %%
# Test single matrix
result_single = rthor.rthor_test(corr_matrix_1, order="circular6")
result_single.summary()

# %% [markdown]
# ## Testing Multiple Matrices
#
# Now let's test all three matrices simultaneously and provide descriptive labels.

# %%
# Test multiple matrices
result_multiple = rthor.rthor_test(
    corr_matrices,
    order="circular6",
    labels=["Strong Pattern", "Moderate Pattern", "Weak Pattern"],
)
result_multiple.summary()

# %% [markdown]
# ## Accessing Results
#
# The results are stored in a pandas DataFrame for easy analysis and export.

# %%
# Display results DataFrame
results_df = result_multiple.results
results_df

# %% [markdown]
# ## Understanding the Results
#
# - **matrix**: Matrix identifier (1-indexed)
# - **predictions**: Number of hypothesized predictions tested
# - **agreements**: Number of predictions met by the data
# - **ties**: Number of tied correlations
# - **ci**: Correspondence Index (-1 to +1, higher is better fit)
# - **p_value**: Statistical significance (< 0.05 typically indicates good fit)
# - **label**: Descriptive label for the matrix
#
# A CI close to 1 indicates strong agreement with the hypothesized ordering, while a value close to 0 or negative indicates poor fit.

# %% [markdown]
# ## Comparing Matrices
#
# You can also compare multiple matrices pairwise to see which fits better.

# %%
# Compare matrices
comparison = rthor.compare_matrices(corr_matrices, order="circular6")
comparison.summary()

# %%
# Display pairwise comparisons
comparison.comparisons

# %% [markdown]
# ## Key Concepts
#
# ### Testing Single Matrices
#
# The simplest use case is testing a single correlation matrix:
#
# ```python
# import rthor
# import numpy as np
#
# # Your correlation matrix
# corr_matrix = np.array([...])
#
# # Test against circular6 preset
# result = rthor.rthor_test(corr_matrix, order="circular6")
# print(result.summary())
# ```
#
# ### Testing Multiple Matrices
#
# You can test multiple matrices simultaneously:
#
# ```python
# # Stack matrices into 3D array or use list of DataFrames
# result = rthor.rthor_test(
#     matrices,
#     order="circular6",
#     labels=["Group 1", "Group 2", "Group 3"]
# )
# ```
#
# ### Understanding the Correspondence Index (CI)
#
# The CI measures how well the data fits the hypothesized ordering:
#
# - **CI = 1.0**: Perfect agreement
# - **CI = 0.0**: No better than chance
# - **CI = -1.0**: Perfect disagreement
#
# ### Interpreting p-values
#
# The p-value indicates statistical significance:
#
# - **p < 0.05**: Significant fit (conventional threshold)
# - **p < 0.01**: Strong fit
# - **p < 0.001**: Very strong fit
#
# ## Common Use Cases
#
# ### Circumplex Models
#
# RTHOR is commonly used to test circumplex models in psychology:
#
# - Interpersonal behavior (e.g., IPC octants)
# - Emotional experience
# - Personality traits
#
# ### Custom Orderings
#
# You can specify custom hypothesized orderings for any theoretical model. See the [Advanced Features](advanced-features.py) example for details.
#
# ## Next Steps
#
# - Try the [Advanced Features](advanced-features.py) notebook for custom orderings
# - See the [API Reference](../api.md) for detailed documentation
# - Check out the [User Guide](../user-guide/concepts.md) for theoretical background
