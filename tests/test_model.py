"""Tests for model training."""

from vp_track_status.model import train_model


def test_train_model(sample_training_data):
    model, feature_cols = train_model(sample_training_data)

    assert model is not None
    assert len(feature_cols) == 5
    assert model.predict([[5.0, 5.0, 5.0, 5.0, 5.0]]).shape == (1,)
