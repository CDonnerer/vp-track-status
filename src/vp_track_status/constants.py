"""Constants used across the vp-track-status package."""

from pathlib import Path

# API configuration
PARAMETER = "rainfall"
ROOT_URL = "https://environment.data.gov.uk/flood-monitoring"
DEFAULT_STATION_ID = "239374TP"

# Model configuration
LABEL_MAPPING = {0: "Dry", 1: "Some puddles", 2: "Lots puddles"}
LABEL_MAPPING_INVERSE = {"Dry": 0, "Some puddles": 1, "Lots puddles": 2}
FEATURE_COLS = ["rain_1d", "rain_2d", "rain_3d", "rain_5d", "rain_7d"]

# File paths
DATA_DIR = Path("data")
RAINFALL_FILE = DATA_DIR / "rainfall" / "rainfall_239374TP_daily.csv"
OBSERVATIONS_FILE = DATA_DIR / "observations" / "track_observations.csv"
MODEL_FILE = DATA_DIR / "models" / "track_condition_model.onnx"
