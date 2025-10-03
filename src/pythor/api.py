"""Public API functions for RTHOR analysis."""

from pathlib import Path

import numpy as np
import pandas as pd

from pythor.core import calculate_ci, calculate_fit, generate_hypothesis_matrix
from pythor.io import extract_lower_triangle, read_correlation_matrices
from pythor.permutations import apply_permutation, generate_permutations


def randall(
    n: int,
    nmat: int,
    input: Path | str,  # noqa: A002
    ord: str | list[int] = "circular6",  # noqa: A002
    description: list[str] | None = None,
) -> pd.DataFrame:
    """
    Randomization test of hypothesized order relations on correlation matrices.

    Parameters
    ----------
    n : int
        Number of variables (matrix dimension)
    nmat : int
        Number of matrices to analyze
    ord : str or list[int], default="circular6"
        Hypothesized ordering. Can be:
        - "circular6": Preset for 6-variable circular model
        - "circular8": Preset for 8-variable circular model
        - Custom list of integers
    input : Path or str
        Path to input file containing correlation matrices
    description : list[str], optional
        Descriptions for each matrix

    Returns
    -------
    result : pd.DataFrame
        Results with columns:
        - mat: Matrix number
        - pred: Number of predictions (nhyp)
        - met: Number of predictions met (nagr)
        - tie: Number of ties
        - CI: Correspondence Index
        - p: p-value from randomization test
        - description: Matrix description

    Notes
    -----
    Translated from RTHORR/R/randall.R lines 29-233.
    Priority 1: Results must match R output exactly.

    """
    # Read matrices from file
    dmatm = read_correlation_matrices(input, n, nmat)

    # Generate hypothesis matrix
    mathyp, ord_array, nhyp = generate_hypothesis_matrix(ord, n)

    # Generate permutations
    # Note: R uses 1-indexed permutations, we use 0-indexed
    permat = generate_permutations(n)
    nper = permat.shape[0]

    # Initialize output
    results = []

    # Process each matrix
    for kk in range(nmat):
        # Extract matrix (R: dmat <- dmatm[,,kk])
        dmat = dmatm[:, :, kk]

        # Calculate fit for original data
        nagr, ntie = calculate_fit(dmat, mathyp)

        # Calculate CI
        ci = calculate_ci(nagr, ntie, nhyp)

        # Randomization test
        count = 1  # Count of permutations with fit >= observed

        # R code: nperx <- nper - 1 (line 153)
        # Loop through permutations (excluding identity which is first)
        for k in range(nper - 1):
            # Get permutation (R: pp <- permat[k,])
            pp = permat[k, :]

            # Apply permutation (R code lines 162-165)
            dmatp = apply_permutation(dmat, pp)

            # Calculate fit for permuted data
            nsup, nntie = calculate_fit(dmatp, mathyp)

            # Count if fit is equal or greater (R line 204)
            if nsup >= nagr:
                count += 1

        # Calculate p-value
        prob = count / nper

        # Store results
        desc = description[kk] if description else ""
        results.append(
            {
                "mat": kk + 1,  # R uses 1-indexed
                "pred": nhyp,
                "met": nagr,
                "tie": ntie,
                "CI": ci,
                "p": prob,
                "description": desc,
            }
        )

    # Create DataFrame (R lines 222-228)
    df = pd.DataFrame(results)

    # Ensure numeric columns are float/int as appropriate
    df["mat"] = df["mat"].astype(int)
    df["pred"] = df["pred"].astype(int)
    df["met"] = df["met"].astype(int)
    df["tie"] = df["tie"].astype(int)
    df["CI"] = df["CI"].astype(float)
    df["p"] = df["p"].astype(float)

    return df


def randall_from_df(
    df_list: list[pd.DataFrame],
    description: list[str],
    ord: str | list[int] = "circular6",  # noqa: A002
) -> pd.DataFrame:
    """
    Randomization test of hypothesized order relations from raw data.

    Parameters
    ----------
    df_list : list[pd.DataFrame]
        List of DataFrames containing raw data. Each DataFrame should have
        only the columns for variables to be included in the analysis.
    description : list[str]
        Descriptions for each DataFrame/matrix
    ord : str or list[int], default="circular6"
        Hypothesized ordering. Can be:
        - "circular6": Preset for 6-variable circular model
        - "circular8": Preset for 8-variable circular model
        - Custom list of integers

    Returns
    -------
    result : pd.DataFrame
        Results with columns:
        - mat: Matrix number
        - pred: Number of predictions (nhyp)
        - met: Number of predictions met (nagr)
        - tie: Number of ties
        - CI: Correspondence Index
        - p: p-value from randomization test
        - description: Matrix description

    Notes
    -----
    Translated from RTHORR/R/randall_from_df.R lines 27-254.

    This function computes correlation matrices from the input DataFrames,
    then runs the same RTHOR analysis as randall().

    Critical: R reverses df_list order (line 74) before processing.
    This affects the ordering of correlation matrices.

    """
    # Validate inputs
    column_counts = [df.shape[1] for df in df_list]
    if len(set(column_counts)) != 1:
        msg = "Number of columns is not equal for all dataframes passed in."
        raise ValueError(msg)

    if len(df_list) != len(description):
        msg = "Number of descriptions not equal to number of dataframes."
        raise ValueError(msg)

    # Get dimensions
    nmat = len(df_list)
    n = df_list[0].shape[1]

    # Critical: R reverses df_list (line 74 in R code) for correlation computation
    # But then appends values in a way that reverses them back
    # R code: za <- append(gdata::lowerTriangle(...), za)
    # This prepends each new matrix, effectively reversing the order
    df_list_reversed = list(reversed(df_list))

    # Compute correlation matrices and extract lower triangles
    # R code lines 77-83: for loop with prepend means last df_list item is first in za
    za_values = []
    for df in df_list_reversed:
        # Compute correlation matrix
        cor_df = df.corr()
        # Extract lower triangle with diagonal (matches R's gdata::lowerTriangle)
        lower_tri = extract_lower_triangle(cor_df.values, include_diagonal=True)
        # R uses: za <- append(lower_tri, za) which prepends
        # So we need to insert at beginning, not append
        za_values = list(lower_tri) + za_values

    za = np.array(za_values)

    # Build 3D matrix array from correlation values
    # Same logic as read_correlation_matrices (R code lines 87-104)
    dmatm = np.zeros((n, n, nmat))
    np_pairs = (n * n - n) // 2

    for m in range(nmat):
        ii = m * (np_pairs + n) - 1

        # First pass: fill upper triangle
        for j in range(n):
            for i in range(n):
                if i > j:
                    continue
                ii += 1
                dmatm[i, j, m] = za[ii]

        # Second pass: fill lower triangle (make symmetric)
        ii = m * (np_pairs + n) - 1
        for i in range(n):
            for j in range(n):
                if i < j:
                    continue
                ii += 1
                dmatm[i, j, m] = za[ii]

    # Rest of the algorithm is identical to randall()
    # Generate hypothesis matrix
    mathyp, ord_array, nhyp = generate_hypothesis_matrix(ord, n)

    # Generate permutations
    permat = generate_permutations(n)
    nper = permat.shape[0]

    # Initialize output
    results = []

    # Process each matrix
    for kk in range(nmat):
        dmat = dmatm[:, :, kk]

        # Calculate fit for original data
        nagr, ntie = calculate_fit(dmat, mathyp)

        # Calculate CI
        ci = calculate_ci(nagr, ntie, nhyp)

        # Randomization test
        count = 1

        for k in range(nper - 1):
            pp = permat[k, :]
            dmatp = apply_permutation(dmat, pp)
            nsup, nntie = calculate_fit(dmatp, mathyp)

            if nsup >= nagr:
                count += 1

        # Calculate p-value
        prob = count / nper

        # Store results
        results.append(
            {
                "mat": kk + 1,
                "pred": nhyp,
                "met": nagr,
                "tie": ntie,
                "CI": ci,
                "p": prob,
                "description": description[kk],
            }
        )

    # Create DataFrame
    df = pd.DataFrame(results)

    # Ensure correct dtypes
    df["mat"] = df["mat"].astype(int)
    df["pred"] = df["pred"].astype(int)
    df["met"] = df["met"].astype(int)
    df["tie"] = df["tie"].astype(int)
    df["CI"] = df["CI"].astype(float)
    df["p"] = df["p"].astype(float)

    return df
