"""Tests for model training."""

import polars as pl

from vp_track_status.model import train_model


def test_train_model():
    df = pl.DataFrame(
        {
            "rain_1d": [5.0, 10.0, 2.0],
            "rain_2d": [5.0, 15.0, 12.0],
            "rain_3d": [5.0, 15.0, 17.0],
            "rain_5d": [5.0, 15.0, 17.0],
            "rain_7d": [5.0, 15.0, 17.0],
            "target": [0, 1, 2],
        }
    )

    model, feature_cols = train_model(df)

    assert model is not None
    assert len(feature_cols) == 5
    assert model.predict([[5.0, 5.0, 5.0, 5.0, 5.0]]).shape == (1,)
