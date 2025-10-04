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
    filepath: Path | str,
    order: str | list[int] = "circular6",
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
    filepath : Path or str
        Path to input file containing correlation matrices
    order : str or list[int], default="circular6"
        Hypothesized ordering. Can be:
        - "circular6": Preset for 6-variable circular model
        - "circular8": Preset for 8-variable circular model
        - Custom list of integers
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
    dmatm = read_correlation_matrices(filepath, n, nmat)

    # Generate hypothesis matrix
    mathyp, ord_array, nhyp = generate_hypothesis_matrix(order, n)

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
    order: str | list[int] = "circular6",
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
    order : str or list[int], default="circular6"
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
    mathyp, ord_array, nhyp = generate_hypothesis_matrix(order, n)

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


def randmf(  # noqa: C901, PLR0915
    n: int,
    nmat: int,
    filepath: Path | str,
    order: str | list[int] = "circular6",
) -> dict[str, pd.DataFrame]:
    """
    Randomization test with pairwise matrix comparisons.

    Parameters
    ----------
    n : int
        Number of variables (matrix dimension)
    nmat : int
        Number of matrices to analyze
    filepath : Path or str
        Path to input file containing correlation matrices
    order : str or list[int], default="circular6"
        Hypothesized ordering. Can be:
        - "circular6": Preset for 6-variable circular model
        - "circular8": Preset for 8-variable circular model
        - Custom list of integers

    Returns
    -------
    result : dict[str, pd.DataFrame]
        Dictionary with two DataFrames:
        - "RTHOR": Main RTHOR results (same format as randall)
        - "comparisons": Pairwise matrix comparison results with columns:
            - mat1, mat2: Matrix pair indices
            - bothmet, 1met2not, 2met1not, neither: Agreement pattern counts
            - CI: Comparison correspondence index
            - p: p-value from randomization test

    Notes
    -----
    Translated from RTHORR/R/randmf.R lines 24-363.
    Priority 1: Results must match R output exactly.

    This function performs all pairwise comparisons between matrices,
    tracking agreement patterns (both met, one met, neither met).

    """
    # Read matrices from file
    dmatm = read_correlation_matrices(filepath, n, nmat)

    # Generate hypothesis matrix
    mathyp, ord_array, nhyp = generate_hypothesis_matrix(order, n)

    # Generate permutations
    permat = generate_permutations(n)
    nper = permat.shape[0]

    # Initialize output for RTHOR results
    rthor_results = []

    # Initialize arrays for comparison tracking (R lines 139-145)
    # These track agreement patterns across all pairs
    bboth = np.zeros(nhyp, dtype=np.int32)  # Both matrices meet hypothesis
    yy1n2 = np.zeros(nhyp, dtype=np.int32)  # Matrix 1 meets, 2 doesn't
    nn1y2 = np.zeros(nhyp, dtype=np.int32)  # Matrix 1 doesn't, 2 meets
    nn1n2 = np.zeros(nhyp, dtype=np.int32)  # Neither meets hypothesis

    # Process each matrix for RTHOR results
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

        # Store RTHOR results
        rthor_results.append(
            {
                "mat": kk + 1,
                "pred": nhyp,
                "met": nagr,
                "tie": ntie,
                "CI": ci,
                "p": prob,
            }
        )

    # Now perform pairwise comparisons (R lines 235-290)
    comparison_results = []

    # Loop through all pairs of matrices
    for kk1 in range(nmat):
        for kk2 in range(kk1 + 1, nmat):
            # Reset agreement tracking arrays for this pair
            bboth.fill(0)
            yy1n2.fill(0)
            nn1y2.fill(0)
            nn1n2.fill(0)

            # Extract matrices
            dmat1 = dmatm[:, :, kk1]
            dmat2 = dmatm[:, :, kk2]

            # Extract upper triangles as vectors (R lines 227-239)
            # scal1 and scal2 in R code
            scal1 = []
            scal2 = []
            for i in range(n):
                for j in range(n):
                    if i >= j:
                        continue
                    scal1.append(dmat1[i, j])
                    scal2.append(dmat2[i, j])

            scal1 = np.array(scal1)
            scal2 = np.array(scal2)

            # Build comparison matrices (R lines 244-254)
            # matc1[i,j] = 1 if scal1[j] > scal1[i], 2 if equal, 0 if less
            np_pairs = len(scal1)  # Should be nhyp (15 for n=6)
            matc1 = np.zeros((np_pairs, np_pairs), dtype=np.int32)
            matc2 = np.zeros((np_pairs, np_pairs), dtype=np.int32)

            for i in range(np_pairs):
                for j in range(np_pairs):
                    if scal1[j] > scal1[i]:
                        matc1[i, j] = 1
                    elif scal1[j] == scal1[i]:
                        matc1[i, j] = 2
                    else:
                        matc1[i, j] = 0

                    if scal2[j] > scal2[i]:
                        matc2[i, j] = 1
                    elif scal2[j] == scal2[i]:
                        matc2[i, j] = 2
                    else:
                        matc2[i, j] = 0

            # Track agreement patterns (R lines 266-295)
            # Loop through comparison matrices and hypothesis matrix
            nsup1 = 0
            ntie1 = 0
            nsup2 = 0
            ntie2 = 0
            both = 0
            n1y2 = 0
            y1n2 = 0
            n1n2 = 0

            for i in range(np_pairs):
                for j in range(np_pairs):
                    m1 = 0
                    m2 = 0
                    v1 = 0
                    v2 = 0

                    # Track met/tie for each matrix
                    if matc1[i, j] == 1 and mathyp[i, j] == 1:
                        nsup1 += 1
                        m1 = 1
                    if matc1[i, j] == 2 and mathyp[i, j] == 1:
                        ntie1 += 1
                    if matc1[i, j] == 0 and mathyp[i, j] == 1:
                        v1 = 1

                    if matc2[i, j] == 1 and mathyp[i, j] == 1:
                        nsup2 += 1
                        m2 = 1
                    if matc2[i, j] == 2 and mathyp[i, j] == 1:
                        ntie2 += 1
                    if matc2[i, j] == 0 and mathyp[i, j] == 1:
                        v2 = 1

                    # Track agreement patterns (R lines 291-295)
                    if m1 == 1 and m2 == 1:
                        both += 1
                    if v1 == 1 and m2 == 1:
                        n1y2 += 1
                    if m1 == 1 and v2 == 1:
                        y1n2 += 1
                    if v1 == 1 and v2 == 1:
                        n1n2 += 1

            # Calculate comparison CI
            # R line 205: ci3 <- (nn1y2-yy1n2)/(bboth+yy1n2+nn1y2+nn1n2)
            sum_bboth = both
            sum_yy1n2 = y1n2
            sum_nn1y2 = n1y2
            sum_nn1n2 = n1n2

            denom = sum_bboth + sum_yy1n2 + sum_nn1y2 + sum_nn1n2
            comp_ci = (sum_nn1y2 - sum_yy1n2) / denom if denom > 0 else 0.0

            # Randomization test for comparison (R lines 214-298)
            comp_count = 1

            for k in range(nper - 1):
                pp = permat[k, :]

                # Apply permutation to both matrices
                dmat1p = apply_permutation(dmat1, pp)
                dmat2p = apply_permutation(dmat2, pp)

                # Extract upper triangles from permuted matrices (R lines 226-239)
                scal1p = []
                scal2p = []
                for i in range(n):
                    for j in range(n):
                        if i >= j:
                            continue
                        scal1p.append(dmat1p[i, j])
                        scal2p.append(dmat2p[i, j])

                scal1p = np.array(scal1p)
                scal2p = np.array(scal2p)

                # Build comparison matrices for permuted data (R lines 244-254)
                matc1p = np.zeros((np_pairs, np_pairs), dtype=np.int32)
                matc2p = np.zeros((np_pairs, np_pairs), dtype=np.int32)

                for i in range(np_pairs):
                    for j in range(np_pairs):
                        if scal1p[j] > scal1p[i]:
                            matc1p[i, j] = 1
                        elif scal1p[j] == scal1p[i]:
                            matc1p[i, j] = 2
                        else:
                            matc1p[i, j] = 0

                        if scal2p[j] > scal2p[i]:
                            matc2p[i, j] = 1
                        elif scal2p[j] == scal2p[i]:
                            matc2p[i, j] = 2
                        else:
                            matc2p[i, j] = 0

                # Count agreements for permuted data (R lines 266-295)
                both_p = 0
                n1y2_p = 0
                y1n2_p = 0
                n1n2_p = 0

                for i in range(np_pairs):
                    for j in range(np_pairs):
                        m1 = 0
                        m2 = 0
                        v1 = 0
                        v2 = 0

                        if matc1p[i, j] == 1 and mathyp[i, j] == 1:
                            m1 = 1
                        if matc1p[i, j] == 0 and mathyp[i, j] == 1:
                            v1 = 1

                        if matc2p[i, j] == 1 and mathyp[i, j] == 1:
                            m2 = 1
                        if matc2p[i, j] == 0 and mathyp[i, j] == 1:
                            v2 = 1

                        if m1 == 1 and m2 == 1:
                            both_p += 1
                        if m1 == 1 and v2 == 1:
                            y1n2_p += 1
                        if v1 == 1 and m2 == 1:
                            n1y2_p += 1
                        if v1 == 1 and v2 == 1:
                            n1n2_p += 1

                # Calculate permuted CI (R line 297)
                denom_p = both_p + y1n2_p + n1y2_p + n1n2_p
                comp_ci_p = (n1y2_p - y1n2_p) / denom_p if denom_p > 0 else 0.0

                # Count if permuted CI >= observed CI (R line 298)
                if comp_ci_p >= comp_ci:
                    comp_count += 1

            # Calculate comparison p-value
            comp_prob = comp_count / nper

            # Store comparison results
            comparison_results.append(
                {
                    "mat1": kk1 + 1,
                    "mat2": kk2 + 1,
                    "bothmet": sum_bboth,
                    "1met2not": sum_yy1n2,
                    "2met1not": sum_nn1y2,
                    "neither": sum_nn1n2,
                    "CI": comp_ci,
                    "p": comp_prob,
                }
            )

    # Create DataFrames
    rthor_df = pd.DataFrame(rthor_results)
    rthor_df["mat"] = rthor_df["mat"].astype(int)
    rthor_df["pred"] = rthor_df["pred"].astype(int)
    rthor_df["met"] = rthor_df["met"].astype(int)
    rthor_df["tie"] = rthor_df["tie"].astype(int)
    rthor_df["CI"] = rthor_df["CI"].astype(float)
    rthor_df["p"] = rthor_df["p"].astype(float)

    comp_df = pd.DataFrame(comparison_results)
    comp_df["mat1"] = comp_df["mat1"].astype(int)
    comp_df["mat2"] = comp_df["mat2"].astype(int)
    comp_df["bothmet"] = comp_df["bothmet"].astype(int)
    comp_df["1met2not"] = comp_df["1met2not"].astype(int)
    comp_df["2met1not"] = comp_df["2met1not"].astype(int)
    comp_df["neither"] = comp_df["neither"].astype(int)
    comp_df["CI"] = comp_df["CI"].astype(float)
    comp_df["p"] = comp_df["p"].astype(float)

    return {"RTHOR": rthor_df, "comparisons": comp_df}
