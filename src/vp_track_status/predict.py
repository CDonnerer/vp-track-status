"""Predict current track conditions using trained model and latest rainfall data."""

from pathlib import Path

import numpy as np
import onnxruntime as ort
import polars as pl

from vp_track_status.model import add_rolling_features


LABEL_MAPPING = {0: "Dry", 1: "Some puddles", 2: "Lots puddles"}
FEATURE_COLS = ["rain_1d", "rain_2d", "rain_3d", "rain_5d", "rain_7d"]


def predict_current_condition(
    model_path="data/models/track_condition_model.onnx",
    rainfall_file="data/rainfall/rainfall_239374TP_daily.csv",
):
    """Predict current track condition based on latest rainfall data."""
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model not found at {model_path}")
    if not Path(rainfall_file).exists():
        raise FileNotFoundError(f"Rainfall data not found at {rainfall_file}")

    session = ort.InferenceSession(str(model_path))

    df_rain = pl.read_csv(rainfall_file)
    df_rain = df_rain.with_columns(pl.col("date").str.to_date()).sort("date")
    df_rain = add_rolling_features(df_rain)

    if df_rain.is_empty():
        raise ValueError("No rainfall data available")

    df_latest = df_rain.tail(1)
    features = df_latest.select(FEATURE_COLS).to_numpy().astype(np.float32)

    input_name = session.get_inputs()[0].name
    label_name = session.get_outputs()[0].name

    result = session.run([label_name], {input_name: features})
    prediction = int(result[0][0])

    return {
        "date": df_latest["date"][0],
        "prediction": prediction,
        "prediction_label": LABEL_MAPPING[prediction],
        "features": {col: float(df_latest[col][0]) for col in FEATURE_COLS},
    }
