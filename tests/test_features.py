"""Tests for feature engineering."""

from vp_track_status.features import add_rolling_features


def test_add_rolling_features(sample_rainfall_data):
    result = add_rolling_features(sample_rainfall_data)

    assert "rain_1d" in result.columns
    assert "rain_7d" in result.columns
    assert result["rain_1d"][0] == 5.0
    assert result["rain_2d"][1] == 15.0
