"""
Regression tests against R RTHORR package outputs.

These tests ensure that the Python implementation produces identical results
to the original R implementation.
"""

# ruff: noqa: PLC0415
from pathlib import Path

import pandas as pd
import pytest

# pythor will be implemented, but we'll write tests first (TDD)
# When implementing functions, import them from pythor and remove @pytest.mark.skip


class TestRandallRegression:
    """Test randall() function against R outputs."""

    def test_randall_matches_r_output(
        self,
        input_matrix_file: Path,
        expected_randall_output: pd.DataFrame,
    ) -> None:
        """Test that randall() produces identical results to R."""
        from pythor import randall

        result = randall(
            n=6,
            nmat=3,
            filepath=input_matrix_file,
            order="circular6",
            description=["sample_one", "sample_two", "sample_three"],
        )

        # Check DataFrame shape
        assert result.shape == expected_randall_output.shape

        # Check column names
        assert list(result.columns) == list(expected_randall_output.columns)

        # Check numerical columns match (allowing for floating point tolerance)
        numerical_cols = ["mat", "pred", "met", "tie", "CI", "p"]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                result[col].astype(float),
                expected_randall_output[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

        # Check description column
        pd.testing.assert_series_equal(
            result["description"],
            expected_randall_output["description"],
            check_names=False,
        )


class TestRandmfRegression:
    """Test randmf() function against R outputs."""

    def test_randmf_matches_r_output(
        self,
        input_matrix_file: Path,
        expected_randmf_output: dict[str, pd.DataFrame],
    ) -> None:
        """Test that randmf() produces identical results to R."""
        from pythor import randmf

        result = randmf(
            n=6,
            nmat=3,
            filepath=input_matrix_file,
            order="circular6",
        )

        # Check that result is a dict with correct keys
        assert isinstance(result, dict)
        assert set(result.keys()) == {"RTHOR", "comparisons"}

        # Test RTHOR DataFrame
        rthor_result = result["RTHOR"]
        rthor_expected = expected_randmf_output["RTHOR"]

        assert rthor_result.shape == rthor_expected.shape
        assert list(rthor_result.columns) == list(rthor_expected.columns)

        numerical_cols = ["mat", "pred", "met", "tie", "CI", "p"]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                rthor_result[col].astype(float),
                rthor_expected[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

        # Test comparisons DataFrame
        comp_result = result["comparisons"]
        comp_expected = expected_randmf_output["comparisons"]

        assert comp_result.shape == comp_expected.shape
        assert list(comp_result.columns) == list(comp_expected.columns)

        numerical_cols = [
            "mat1",
            "mat2",
            "bothmet",
            "1met2not",
            "2met1not",
            "neither",
            "CI",
            "p",
        ]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                comp_result[col].astype(float),
                comp_expected[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )


class TestRandallFromDfRegression:
    """Test randall_from_df() function against R outputs."""

    def test_randall_from_df_matches_r_output(
        self,
        df_list: list[pd.DataFrame],
        expected_randall_from_df_output: pd.DataFrame,
    ) -> None:
        """Test that randall_from_df() produces identical results to R."""
        from pythor import randall_from_df

        result = randall_from_df(
            df_list=df_list,
            description=["whole sample", "t1", "t2", "t3", "t4"],
            order="circular6",
        )

        # Check DataFrame structure
        assert result.shape == expected_randall_from_df_output.shape
        assert list(result.columns) == list(expected_randall_from_df_output.columns)

        # Check numerical columns
        numerical_cols = ["mat", "pred", "met", "tie", "CI", "p"]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                result[col].astype(float),
                expected_randall_from_df_output[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

        # Check description column
        pd.testing.assert_series_equal(
            result["description"],
            expected_randall_from_df_output["description"],
            check_names=False,
        )


class TestRandmfFromDfRegression:
    """Test randmf_from_df() function against R outputs."""

    @pytest.mark.skip(reason="randmf_from_df() not yet implemented")
    def test_randmf_from_df_matches_r_output(
        self,
        df_list: list[pd.DataFrame],
        expected_randmf_from_df_output: dict[str, pd.DataFrame],
    ) -> None:
        """Test that randmf_from_df() produces identical results to R."""
        from pythor import randmf_from_df

        result = randmf_from_df(
            df_list=df_list,
            ord="circular6",
        )

        # Check structure
        assert isinstance(result, dict)
        assert set(result.keys()) == {"RTHOR", "comparisons"}

        # Test RTHOR DataFrame
        rthor_result = result["RTHOR"]
        rthor_expected = expected_randmf_from_df_output["RTHOR"]

        assert rthor_result.shape == rthor_expected.shape
        assert list(rthor_result.columns) == list(rthor_expected.columns)

        numerical_cols = ["mat", "pred", "met", "tie", "CI", "p"]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                rthor_result[col].astype(float),
                rthor_expected[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )

        # Test comparisons DataFrame
        comp_result = result["comparisons"]
        comp_expected = expected_randmf_from_df_output["comparisons"]

        assert comp_result.shape == comp_expected.shape
        assert list(comp_result.columns) == list(comp_expected.columns)

        numerical_cols = [
            "mat1",
            "mat2",
            "bothmet",
            "1met2not",
            "2met1not",
            "neither",
            "CI",
            "p",
        ]
        for col in numerical_cols:
            pd.testing.assert_series_equal(
                comp_result[col].astype(float),
                comp_expected[col].astype(float),
                rtol=1e-10,
                atol=1e-12,
                check_names=False,
            )
