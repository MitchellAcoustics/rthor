"""Unit tests for core RTHOR algorithm functions."""

import numpy as np

from pythor.core import calculate_ci, calculate_fit, generate_hypothesis_matrix


class TestGenerateHypothesisMatrix:
    """Test generate_hypothesis_matrix function."""

    def test_circular6_shape(self) -> None:
        """Test that circular6 produces correct shape."""
        n = 6
        mathyp, ord_array, nhyp = generate_hypothesis_matrix("circular6", n)

        np_pairs = (n * n - n) // 2  # 15 for n=6
        assert mathyp.shape == (np_pairs, np_pairs)
        assert len(ord_array) == np_pairs
        assert nhyp == np.sum(mathyp)

    def test_circular6_ordering(self) -> None:
        """Test that circular6 has correct ordering."""
        _, ord_array, _ = generate_hypothesis_matrix("circular6", 6)
        expected = np.array([1, 2, 3, 2, 1, 1, 2, 3, 2, 1, 2, 3, 1, 2, 1])
        np.testing.assert_array_equal(ord_array, expected)

    def test_circular8_ordering(self) -> None:
        """Test that circular8 has correct ordering."""
        _, ord_array, _ = generate_hypothesis_matrix("circular8", 8)
        expected = np.array(
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
        np.testing.assert_array_equal(ord_array, expected)

    def test_custom_ordering(self) -> None:
        """Test custom ordering input."""
        custom_ord = [1, 2, 3, 2, 1]
        n = 3
        _, ord_array, _ = generate_hypothesis_matrix(custom_ord, n)
        # For n=3, np_pairs = 3, but custom_ord has 5 elements
        # This should use the custom ordering as-is
        np.testing.assert_array_equal(ord_array, np.array(custom_ord))

    def test_hypothesis_matrix_values(self) -> None:
        """Test that hypothesis matrix has only 0 and 1."""
        mathyp, _, _ = generate_hypothesis_matrix("circular6", 6)
        assert set(np.unique(mathyp)) <= {0, 1}

    def test_nhyp_count(self) -> None:
        """Test that nhyp equals number of 1s in matrix."""
        mathyp, _, nhyp = generate_hypothesis_matrix("circular6", 6)
        assert nhyp == np.sum(mathyp == 1)


class TestCalculateFit:
    """Test calculate_fit function."""

    def test_simple_matrix(self) -> None:
        """Test fit calculation with simple correlation matrix."""
        # Create a simple 3x3 correlation matrix
        dmat = np.array(
            [
                [1.0, 0.8, 0.6],
                [0.8, 1.0, 0.7],
                [0.6, 0.7, 1.0],
            ]
        )

        # Create simple hypothesis matrix (3 pairs for n=3)
        mathyp = np.array(
            [
                [0, 1, 0],
                [0, 0, 1],
                [0, 0, 0],
            ]
        )

        nagr, ntie = calculate_fit(dmat, mathyp)

        # Basic sanity checks
        assert isinstance(nagr, int)
        assert isinstance(ntie, int)
        assert nagr >= 0
        assert ntie >= 0

    def test_identity_matrix(self) -> None:
        """Test fit with identity matrix (all 1s on diagonal)."""
        dmat = np.eye(4)
        mathyp, _, _ = generate_hypothesis_matrix("circular6", 4)

        nagr, ntie = calculate_fit(dmat, mathyp)

        # With identity matrix, off-diagonal are all 0
        assert nagr >= 0
        assert ntie >= 0


class TestCalculateCI:
    """Test calculate_ci function."""

    def test_ci_calculation(self) -> None:
        """Test CI calculation with known values."""
        # From test data: mat=1, pred=72, met=59, tie=1, CI=0.652777...
        nagr = 59
        ntie = 1
        nhyp = 72

        ci = calculate_ci(nagr, ntie, nhyp)

        # CI = (59 - (72 - (59 + 1))) / 72
        #    = (59 - 12) / 72
        #    = 47 / 72
        #    = 0.652777777...
        expected = 0.652777777777778
        assert abs(ci - expected) < 1e-10

    def test_ci_perfect_fit(self) -> None:
        """Test CI when all predictions are met."""
        nagr = 72
        ntie = 0
        nhyp = 72

        ci = calculate_ci(nagr, ntie, nhyp)

        # CI = (72 - (72 - 72)) / 72 = 72 / 72 = 1.0
        assert abs(ci - 1.0) < 1e-10

    def test_ci_no_fit(self) -> None:
        """Test CI when no predictions are met."""
        nagr = 0
        ntie = 0
        nhyp = 72

        ci = calculate_ci(nagr, ntie, nhyp)

        # CI = (0 - 72) / 72 = -1.0
        assert abs(ci - (-1.0)) < 1e-10
