"""Public API functions for RTHOR analysis."""

from pathlib import Path

import pandas as pd

from pythor.core import calculate_ci, calculate_fit, generate_hypothesis_matrix
from pythor.io import read_correlation_matrices
from pythor.permutations import apply_permutation, generate_permutations


def randall(
    n: int,
    nmat: int,
    input: Path | str,  # noqa: A002
    ord: str | list[int] = "circular6",
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
