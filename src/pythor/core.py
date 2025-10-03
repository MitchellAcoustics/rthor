"""Core RTHOR algorithm functions."""

import numpy as np


def generate_hypothesis_matrix(
    ord: str | list[int],
    n: int,
) -> tuple[np.ndarray, np.ndarray, int]:
    """
    Generate hypothesis matrix for RTHOR analysis.

    Parameters
    ----------
    ord : str or list[int]
        Order specification. Can be:
        - "circular6": Preset ordering for 6-variable circular model
        - "circular8": Preset ordering for 8-variable circular model
        - Custom list of integers specifying the order
    n : int
        Number of variables (rows/columns in correlation matrix)

    Returns
    -------
    mathyp : np.ndarray
        Hypothesis matrix (np × np) where np = (n² - n) / 2
        mathyp[i,j] = 1 if ord[j] < ord[i], else 0
    ord_array : np.ndarray
        The processed order array
    nhyp : int
        Count of hypothesized relationships (sum of 1s in mathyp)

    Notes
    -----
    Translated from RTHORR/R/randall.R lines 31-81.
    The hypothesis matrix represents predicted pairwise relationships
    between variables based on the hypothesized ordering.

    """
    # Process ord input - convert to array
    if ord == "circular6":
        ord_array = np.array([1, 2, 3, 2, 1, 1, 2, 3, 2, 1, 2, 3, 1, 2, 1])
    elif ord == "circular8":
        ord_array = np.array(
            [
                1,
                2,
                3,
                4,
                3,
                2,
                1,
                1,
                2,
                3,
                4,
                3,
                2,
                1,
                2,
                3,
                4,
                3,
                1,
                2,
                3,
                4,
                1,
                2,
                3,
                1,
                2,
                1,
            ]
        )
    else:
        ord_array = np.array(ord)

    # Calculate number of pairs (upper triangle without diagonal)
    np_pairs = (n * n - n) // 2

    # Generate hypothesis matrix
    # R code: if(ord[j]<ord[i]) mathyp[i,j]<-1 else mathyp[i,j]<-0
    # This creates a matrix comparing all pairs
    mathyp = np.zeros((np_pairs, np_pairs), dtype=np.int32)

    for i in range(np_pairs):
        for j in range(np_pairs):
            if ord_array[j] < ord_array[i]:
                mathyp[i, j] = 1

    # Count hypotheses (number of 1s in matrix)
    nhyp = int(np.sum(mathyp))

    return mathyp, ord_array, nhyp


def calculate_fit(
    dmat: np.ndarray,
    mathyp: np.ndarray,
) -> tuple[int, int]:
    """
    Calculate fit of correlation matrix to hypothesis.

    Parameters
    ----------
    dmat : np.ndarray
        Correlation matrix (n × n)
    mathyp : np.ndarray
        Hypothesis matrix (np × np) where np = (n² - n) / 2

    Returns
    -------
    nagr : int
        Number of agreements (correlations matching hypothesis)
    ntie : int
        Number of ties (equal correlations where hypothesis predicts difference)

    Notes
    -----
    Translated from RTHORR/R/randall.R lines 122-148.
    Compares pairwise correlations against hypothesized ordering.

    """
    n = dmat.shape[0]
    np_pairs = (n * n - n) // 2

    # Extract upper triangle as vector (R code lines 126-131)
    # R uses row-major order, we need to match this exactly
    ii = 0
    scal = np.zeros(np_pairs)
    for i in range(n):
        for j in range(n):
            if i >= j:
                continue
            scal[ii] = dmat[i, j]
            ii += 1

    # Build comparison matrix (R code lines 135-140)
    # matc[i,j] = 1 if scal[j] > scal[i]
    # matc[i,j] = 2 if scal[j] == scal[i]
    # matc[i,j] = 0 if scal[j] < scal[i]
    matc = np.zeros((np_pairs, np_pairs), dtype=np.int32)
    for i in range(np_pairs):
        for j in range(np_pairs):
            if scal[j] > scal[i]:
                matc[i, j] = 1
            elif scal[j] == scal[i]:
                matc[i, j] = 2
            # else remains 0

    # Count agreements and ties (R code lines 143-146)
    nagr = 0
    ntie = 0
    for i in range(np_pairs):
        for j in range(np_pairs):
            if matc[i, j] == 1 and mathyp[i, j] == 1:
                nagr += 1
            if matc[i, j] == 2 and mathyp[i, j] == 1:
                ntie += 1

    return nagr, ntie


def calculate_ci(nagr: int, ntie: int, nhyp: int) -> float:
    """
    Calculate Correspondence Index (CI).

    Parameters
    ----------
    nagr : int
        Number of agreements
    ntie : int
        Number of ties
    nhyp : int
        Number of hypothesized relationships

    Returns
    -------
    ci : float
        Correspondence Index

    Notes
    -----
    CI = (nagr - (nhyp - (nagr + ntie))) / nhyp
    Translated from RTHORR/R/randall.R line 148.

    """
    return (nagr - (nhyp - (nagr + ntie))) / nhyp
