import marimo

__generated_with = "0.9.14"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """
        # Basic Usage of pythor

        This notebook demonstrates the basic usage of `pythor` for testing correlation
        matrices against hypothesized orderings using the RTHOR (Randomization Test of
        Hypothesized Order Relations) method.
        """
    )


@app.cell
def __():
    import numpy as np
    import pandas as pd

    import pythor

    return np, pd, pythor


@app.cell
def __(mo):
    mo.md(
        """
        ## Creating Sample Data

        First, let's create some sample correlation matrices. We'll create 3 matrices
        with 6 variables each, following a circular/circumplex structure.
        """
    )


@app.cell
def __(np):
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
    return corr_matrices, corr_matrix_1, corr_matrix_2, corr_matrix_3


@app.cell
def __(mo):
    mo.md(
        """
        ## Testing a Single Matrix

        Let's test the first correlation matrix against a circular ordering hypothesis.
        The "circular6" preset specifies that we expect variables 1-6 to be arranged
        in a circular pattern.
        """
    )


@app.cell
def __(corr_matrix_1, pythor):
    # Test single matrix
    result_single = pythor.rthor_test(corr_matrix_1, order="circular6")

    print(result_single.summary())
    return (result_single,)


@app.cell
def __(mo):
    mo.md(
        """
        ## Testing Multiple Matrices

        Now let's test all three matrices simultaneously and provide descriptive labels.
        """
    )


@app.cell
def __(corr_matrices, pythor):
    # Test multiple matrices
    result_multiple = pythor.rthor_test(
        corr_matrices,
        order="circular6",
        labels=["Strong Pattern", "Moderate Pattern", "Weak Pattern"],
    )

    print(result_multiple.summary())
    return (result_multiple,)


@app.cell
def __(mo):
    mo.md(
        """
        ## Accessing Results

        The results are stored in a pandas DataFrame for easy analysis and export.
        """
    )


@app.cell
def __(result_multiple):
    # Display results DataFrame
    results_df = result_multiple.results
    results_df
    return (results_df,)


@app.cell
def __(mo):
    mo.md(
        """
        ## Understanding the Results

        - **matrix**: Matrix identifier (1-indexed)
        - **predictions**: Number of hypothesized predictions tested
        - **agreements**: Number of predictions met by the data
        - **ties**: Number of tied correlations
        - **ci**: Correspondence Index (-1 to +1, higher is better fit)
        - **p_value**: Statistical significance (< 0.05 typically indicates good fit)
        - **label**: Descriptive label for the matrix

        A CI close to 1 indicates strong agreement with the hypothesized ordering,
        while a value close to 0 or negative indicates poor fit.
        """
    )


@app.cell
def __(mo):
    mo.md(
        """
        ## Comparing Matrices

        You can also compare multiple matrices pairwise to see which fits better.
        """
    )


@app.cell
def __(corr_matrices, pythor):
    # Compare matrices
    comparison = pythor.compare_matrices(corr_matrices, order="circular6")

    print(comparison.summary())
    return (comparison,)


@app.cell
def __(comparison):
    # Display pairwise comparisons
    comparison.comparisons


@app.cell
def __(mo):
    mo.md(
        """
        ## Next Steps

        - Try the [Advanced Features](advanced-features.md) notebook for custom orderings
        - See the [API Reference](../api.md) for detailed documentation
        - Check out the [User Guide](../user-guide/concepts.md) for theoretical background
        """
    )


if __name__ == "__main__":
    app.run()
