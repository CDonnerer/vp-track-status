"""Feature engineering utilities."""

import polars as pl


def add_rolling_features(df_rain):
    """Add rolling window rainfall features to dataframe."""
    window_sizes = [1, 2, 3, 5, 7]

    rolling_features = [
        pl.col("rainfall_mm")
        .rolling_sum(window_size=size, min_samples=1)
        .alias(f"rain_{size}d")
        for size in window_sizes
    ]

    return df_rain.sort("date").with_columns(rolling_features)
