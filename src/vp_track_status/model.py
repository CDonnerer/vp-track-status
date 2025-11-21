"""Train and export track condition prediction model."""

from pathlib import Path

import polars as pl
from sklearn.linear_model import LogisticRegression
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

from vp_track_status.constants import FEATURE_COLS, LABEL_MAPPING_INVERSE
from vp_track_status.features import add_rolling_features


def load_and_prepare_data(rainfall_file, observations_file):
    df_rain = pl.read_csv(rainfall_file)
    df_rain = df_rain.with_columns(pl.col("date").str.to_date()).sort("date")
    df_rain = add_rolling_features(df_rain)

    df_obs = pl.read_csv(observations_file)
    df_obs = df_obs.with_columns(
        pl.col("Timestamp").str.to_datetime("%m/%d/%Y %H:%M:%S").dt.date().alias("date")
    )

    df = df_rain.join(df_obs, on="date", how="inner").sort("date")

    df = df.with_columns(
        pl.col("State of the track").replace(LABEL_MAPPING_INVERSE).alias("target")
    )

    return df


def train_model(df, feature_cols=None):
    """Train logistic regression model on all data."""
    if feature_cols is None:
        feature_cols = FEATURE_COLS

    X = df.select(feature_cols).to_numpy()
    y = df.select("target").to_numpy().ravel()

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X, y)

    return model, feature_cols


def export_to_onnx(model, feature_cols, output_path):
    """Export trained model to ONNX format."""
    initial_type = [("float_input", FloatTensorType([None, len(feature_cols)]))]

    onnx_model = convert_sklearn(
        model,
        initial_types=initial_type,
        target_opset={"": 15, "ai.onnx.ml": 3},
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(onnx_model.SerializeToString())

    return output_path


def train_and_export(
    rainfall_file,
    observations_file,
    output_path,
    feature_cols=None,
):
    """Complete pipeline: load data, train model, export to ONNX."""
    df = load_and_prepare_data(rainfall_file, observations_file)
    print(f"Loaded {len(df)} observations with rainfall data")

    model, feature_cols = train_model(df, feature_cols)
    print(f"Trained logistic regression model on {len(df)} samples")
    print(f"Features: {feature_cols}")

    output_path = export_to_onnx(model, feature_cols, output_path)
    print(f"Model exported to {output_path}")

    return model, feature_cols
