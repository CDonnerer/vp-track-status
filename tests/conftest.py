"""Shared test fixtures."""

import polars as pl
import pytest


@pytest.fixture
def sample_rainfall_data():
    return pl.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "rainfall_mm": [5.0, 10.0, 2.0],
        }
    ).with_columns(pl.col("date").str.to_date())


@pytest.fixture
def sample_training_data():
    return pl.DataFrame(
        {
            "rain_1d": [5.0, 10.0, 2.0],
            "rain_2d": [5.0, 15.0, 12.0],
            "rain_3d": [5.0, 15.0, 17.0],
            "rain_5d": [5.0, 15.0, 17.0],
            "rain_7d": [5.0, 15.0, 17.0],
            "target": [0, 1, 2],
        }
    )
