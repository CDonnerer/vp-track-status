"""Tests for feature engineering."""

import polars as pl

from vp_track_status.features import add_rolling_features


def test_add_rolling_features():
    df = pl.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "rainfall_mm": [5.0, 10.0, 2.0],
        }
    ).with_columns(pl.col("date").str.to_date())

    result = add_rolling_features(df)

    assert "rain_1d" in result.columns
    assert "rain_7d" in result.columns
    assert result["rain_1d"][0] == 5.0
    assert result["rain_2d"][1] == 15.0
