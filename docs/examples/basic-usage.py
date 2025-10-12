# %% [markdown]
# # Basic Usage
#
# This example demonstrates the fundamental features of rthor for testing correlation matrices.

# %% [markdown]
# ## Creating Sample Data
#
# First, let's create some sample correlation matrices with varying degrees of fit to a circular pattern. We'll create 3 matrices with 6 variables each, ranging from perfect fit to poor fit.

# %%
import numpy as np

import rthor

# %%
# Create sample correlation matrices with varying fit to circular pattern
# In a circular pattern (1-2-3-4-5-6-1), adjacent variables should correlate
# higher than distant variables, with opposite variables correlating lowest

# Matrix 1: Excellent fit - perfect circular pattern (CI = 1.0)
# Clear gradation: adjacent (0.90) > distance-2 (0.60) > opposite (0.30)
corr_matrix_1 = np.array(
    [
        [1.00, 0.90, 0.60, 0.30, 0.60, 0.90],  # Var 1
        [0.90, 1.00, 0.90, 0.60, 0.30, 0.60],  # Var 2
        [0.60, 0.90, 1.00, 0.90, 0.60, 0.30],  # Var 3
        [0.30, 0.60, 0.90, 1.00, 0.90, 0.60],  # Var 4
        [0.60, 0.30, 0.60, 0.90, 1.00, 0.90],  # Var 5
        [0.90, 0.60, 0.30, 0.60, 0.90, 1.00],  # Var 6
    ]
)

# Matrix 2: Good fit - mostly circular with some violations (CI ≈ 0.8)
# Some distance ordering violations but overall pattern holds
corr_matrix_2 = np.array(
    [
        [1.00, 0.68, 0.72, 0.58, 0.65, 0.70],  # Some non-adjacent correlations too high
        [0.68, 1.00, 0.72, 0.68, 0.52, 0.62],
        [0.72, 0.72, 1.00, 0.70, 0.68, 0.55],
        [0.58, 0.68, 0.70, 1.00, 0.72, 0.65],
        [0.65, 0.52, 0.68, 0.72, 1.00, 0.70],
        [0.70, 0.62, 0.55, 0.65, 0.70, 1.00],
    ]
)

# Matrix 3: Poor fit - violates circular pattern (CI ≈ -0.5)
# Opposite and adjacent correlations have similar or reversed magnitudes
corr_matrix_3 = np.array(
    [
        [1.00, 0.48, 0.62, 0.55, 0.51, 0.45],  # Opposite higher than adjacent
        [0.48, 1.00, 0.45, 0.58, 0.52, 0.50],
        [0.62, 0.45, 1.00, 0.50, 0.60, 0.48],
        [0.55, 0.58, 0.50, 1.00, 0.48, 0.55],
        [0.51, 0.52, 0.60, 0.48, 1.00, 0.50],
        [0.45, 0.50, 0.48, 0.55, 0.50, 1.00],
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
df_single = rthor.test(corr_matrix_1, order="circular6", print_results=True)

# %% [markdown]
# ## Testing Multiple Matrices
#
# Now let's test all three matrices simultaneously and provide descriptive labels.

# %%
# Test multiple matrices with automatic printing
df_multiple = rthor.test(
    corr_matrices,
    order="circular6",
    labels=["Excellent Fit", "Good Fit", "Poor Fit"],
    print_results=True,
)

# %% [markdown]
# ## Accessing Results
#
# The results are in a pandas DataFrame for easy analysis and export.

# %%
# Display results DataFrame
df_multiple.round(3)

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
individual, pairwise = rthor.compare(
    corr_matrices, order="circular6", print_results=True
)

# %%
# Display pairwise comparisons
pairwise.round(3)

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
# df = rthor.test(corr_matrix, order="circular6", print_results=True)
# ```
#
# ### Testing Multiple Matrices
#
# You can test multiple matrices simultaneously:
#
# ```python
# # Stack matrices into 3D array or use list of DataFrames
# df = rthor.test(
#     matrices,
#     order="circular6",
#     labels=["Group 1", "Group 2", "Group 3"]
# )
# # Work with the DataFrame
# df[df['p_value'] < 0.05]  # Filter significant results
# df.to_csv('results.csv')  # Export
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
