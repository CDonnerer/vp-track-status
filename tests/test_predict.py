"""Tests for prediction module."""

import tempfile
from pathlib import Path

from vp_track_status.model import train_model, export_to_onnx
from vp_track_status.predict import predict_current_condition


def test_predict_current_condition(sample_rainfall_data, sample_training_data):
    with tempfile.TemporaryDirectory() as tmpdir:
        rainfall_file = Path(tmpdir) / "rainfall.csv"
        model_file = Path(tmpdir) / "model.onnx"

        sample_rainfall_data.write_csv(rainfall_file)

        model, feature_cols = train_model(sample_training_data)
        export_to_onnx(model, feature_cols, model_file)

        result = predict_current_condition(
            model_path=str(model_file),
            rainfall_file=str(rainfall_file),
        )

        assert "date" in result
        assert "prediction" in result
        assert "prediction_label" in result
        assert result["prediction"] in [0, 1, 2]
