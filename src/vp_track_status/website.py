"""Generate static website displaying current track conditions."""

from datetime import datetime
from pathlib import Path

import polars as pl

from vp_track_status.constants import RAINFALL_FILE
from vp_track_status.predict import predict_current_condition


def generate_html(prediction_result, rainfall_data):
    """Generate HTML page from prediction and rainfall data."""
    condition = prediction_result["prediction_label"]
    date = prediction_result["date"]
    features = prediction_result["features"]

    condition_colors = {
        "Dry": "#22c55e",
        "Some puddles": "#f59e0b",
        "Lots puddles": "#ef4444",
    }
    condition_descriptions = {
        "Dry": "Good conditions to run a workout on the athletics track.",
        "Some puddles": "Possible to run workout on the athletics track, but you will likely have to dodge puddles and swerve lanes.",
        "Lots puddles": "The athletics track is very water logged, you might as well run in your bathtub.",
    }

    color = condition_colors.get(condition, "#6b7280")
    description = condition_descriptions.get(condition, "")

    recent_rain = (
        rainfall_data.tail(7)
        .select(["date", "rainfall_mm"])
        .with_columns(pl.col("date").dt.strftime("%Y-%m-%d").alias("date"))
        .reverse()
    )

    # Calculate max rainfall for bar chart scaling
    max_rainfall = max(row["rainfall_mm"] for row in recent_rain.iter_rows(named=True))
    if max_rainfall == 0:
        max_rainfall = 1

    # Build rainfall bars
    rain_bars = ""
    for row in recent_rain.iter_rows(named=True):
        width_pct = (row["rainfall_mm"] / max_rainfall) * 100 if max_rainfall > 0 else 0
        rain_bars += f"""
        <div class="rain-row">
            <div class="rain-date">{row["date"]}</div>
            <div class="rain-bar-container">
                <div class="rain-bar" style="width: {width_pct}%"></div>
            </div>
            <div class="rain-value">{row["rainfall_mm"]:.1f} mm</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Victoria Park Athletics Track Status</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: #ffffff;
            color: #000000;
            line-height: 1.6;
            padding: 30px 40px;
            max-width: 900px;
            margin: 0 auto;
        }}
        .accent-bar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 8px;
            height: 100vh;
            background: {color};
        }}
        .header {{
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2.5em;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #000000;
        }}
        .subtitle {{
            font-size: 0.85em;
            color: #999999;
            margin-top: 8px;
            letter-spacing: 0.02em;
        }}
        .subtitle a {{
            color: #666666;
            text-decoration: none;
            border-bottom: 1px solid #e0e0e0;
        }}
        .subtitle a:hover {{
            color: #000000;
            border-bottom: 1px solid #000000;
        }}
        .status-section {{
            margin-bottom: 50px;
            border-top: 1px solid #000000;
            padding-top: 30px;
        }}
        .status-label {{
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #666666;
            margin-bottom: 12px;
            font-weight: 500;
        }}
        .status-value {{
            font-size: 3em;
            font-weight: 700;
            color: {color};
            margin-bottom: 16px;
            letter-spacing: -0.02em;
        }}
        .status-description {{
            font-size: 1.1em;
            color: #333333;
            line-height: 1.7;
            max-width: 600px;
        }}
        .data-section {{
            margin-bottom: 60px;
        }}
        .section-title {{
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #666666;
            margin-bottom: 20px;
            font-weight: 500;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            margin-bottom: 60px;
        }}
        .metric {{
            border-left: 3px solid #000000;
            padding-left: 16px;
        }}
        .metric-label {{
            font-size: 0.85em;
            color: #666666;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: 2.2em;
            font-weight: 700;
            color: #000000;
            letter-spacing: -0.02em;
        }}
        .metric-unit {{
            font-size: 0.5em;
            color: #666666;
            font-weight: 400;
            margin-left: 4px;
        }}
        .rain-row {{
            display: grid;
            grid-template-columns: 100px 1fr 90px;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }}
        .rain-date {{
            font-size: 0.95em;
            color: #666666;
            font-variant-numeric: tabular-nums;
        }}
        .rain-bar-container {{
            height: 8px;
            background: #f0f0f0;
        }}
        .rain-bar {{
            height: 100%;
            background: #000000;
            transition: width 0.3s ease;
        }}
        .rain-value {{
            font-size: 0.95em;
            font-weight: 600;
            color: #000000;
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 0.85em;
            color: #999999;
            line-height: 1.8;
        }}
        .footer a {{
            color: #000000;
            text-decoration: none;
            border-bottom: 1px solid #cccccc;
        }}
        .footer a:hover {{
            border-bottom: 1px solid #000000;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 40px 24px;
            }}
            h1 {{
                font-size: 2em;
            }}
            .status-value {{
                font-size: 2.2em;
            }}
            .metrics {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            .rain-row {{
                grid-template-columns: 90px 1fr 70px;
                gap: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="accent-bar"></div>

    <div class="header">
        <h1>Victoria Park Athletics Track</h1>
        <div class="subtitle">
            Tower Hamlets, London E3 · <a href="https://what3words.com/reds.dogs.cube" target="_blank">///reds.dogs.cube</a>
        </div>
    </div>

    <div class="status-section">
        <div class="status-label">Track Condition for {date}</div>
        <div class="status-value">{condition}</div>
        <div class="status-description">{description}</div>
    </div>

    <div class="data-section">
        <div class="section-title">Rainfall Summary</div>
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Last 24h</div>
                <div class="metric-value">{features["rain_1d"]:.1f}<span class="metric-unit">mm</span></div>
            </div>
            <div class="metric">
                <div class="metric-label">Last 3 days</div>
                <div class="metric-value">{features["rain_3d"]:.1f}<span class="metric-unit">mm</span></div>
            </div>
            <div class="metric">
                <div class="metric-label">Last 7 days</div>
                <div class="metric-value">{features["rain_7d"]:.1f}<span class="metric-unit">mm</span></div>
            </div>
        </div>
    </div>

    <div class="data-section">
        <div class="section-title">Recent Rainfall</div>
        {rain_bars}
    </div>

    <div class="footer">
        Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}<br>
        Predictions use AI trained on puddle observations and rainfall data from <a href="https://environment.data.gov.uk/flood-monitoring/doc/reference" target="_blank">UK Environment Agency</a><br>
        <a href="https://github.com/CDonnerer/vp-track-status" target="_blank">View source on GitHub</a>
    </div>
</body>
</html>"""

    return html


def generate_site(output_dir=None):
    """Generate static website with current track conditions."""
    if output_dir is None:
        output_dir = Path("docs")
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    prediction = predict_current_condition()

    rainfall_data = pl.read_csv(RAINFALL_FILE)
    rainfall_data = rainfall_data.with_columns(pl.col("date").str.to_date())

    html = generate_html(prediction, rainfall_data)

    output_file = output_dir / "index.html"
    output_file.write_text(html)

    return output_file
