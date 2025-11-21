"""Feature engineering utilities."""

import polars as pl


def add_rolling_features(df_rain):
    """Add rolling window rainfall features to dataframe."""
    return df_rain.with_columns(
        [
            pl.col("rainfall_mm")
            .rolling_sum(window_size=1, min_samples=1)
            .alias("rain_1d"),
            pl.col("rainfall_mm")
            .rolling_sum(window_size=2, min_samples=1)
            .alias("rain_2d"),
            pl.col("rainfall_mm")
            .rolling_sum(window_size=3, min_samples=1)
            .alias("rain_3d"),
            pl.col("rainfall_mm")
            .rolling_sum(window_size=5, min_samples=1)
            .alias("rain_5d"),
            pl.col("rainfall_mm")
            .rolling_sum(window_size=7, min_samples=1)
            .alias("rain_7d"),
        ]
    )
