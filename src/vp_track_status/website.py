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
    condition_emoji = {
        "Dry": "☀️",
        "Some puddles": "🌧️",
        "Lots puddles": "💧",
    }
    condition_descriptions = {
        "Dry": "Good conditions to run a workout on the athletics track.",
        "Some puddles": "Possible to run workout on the athletics track, but you will likely have to dodge puddles and swerve lanes.",
        "Lots puddles": "The athletics track is very water logged, you might as well run in your bathtub.",
    }

    color = condition_colors.get(condition, "#6b7280")
    emoji = condition_emoji.get(condition, "")
    description = condition_descriptions.get(condition, "")

    recent_rain = (
        rainfall_data.tail(7)
        .select(["date", "rainfall_mm"])
        .with_columns(pl.col("date").dt.strftime("%Y-%m-%d").alias("date"))
    )
    rain_rows = "\n".join(
        f"<tr><td>{row['date']}</td><td>{row['rainfall_mm']:.1f}mm</td></tr>"
        for row in recent_rain.iter_rows(named=True)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Victoria Park Track Status</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }}
        h1 {{
            text-align: center;
            color: #1f2937;
            margin-bottom: 10px;
            font-size: 2em;
        }}
        .subtitle {{
            text-align: center;
            color: #6b7280;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .status-card {{
            background: {color};
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .status-emoji {{
            font-size: 4em;
            margin-bottom: 10px;
        }}
        .status-text {{
            font-size: 2em;
            font-weight: bold;
        }}
        .status-date {{
            margin-top: 10px;
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .status-description {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            color: #374151;
            font-size: 1.05em;
            line-height: 1.6;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 15px;
        }}
        .features {{
            background: #f3f4f6;
            padding: 20px;
            border-radius: 10px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }}
        .feature {{
            text-align: center;
        }}
        .feature-label {{
            color: #6b7280;
            font-size: 0.85em;
            margin-bottom: 5px;
        }}
        .feature-value {{
            color: #1f2937;
            font-size: 1.3em;
            font-weight: 600;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #f9fafb;
            font-weight: 600;
            color: #1f2937;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 0.85em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Victoria Park Track Status</h1>
        <div class="subtitle">London, UK</div>

        <div class="status-card">
            <div class="status-emoji">{emoji}</div>
            <div class="status-text">{condition}</div>
            <div class="status-date">Prediction for {date}</div>
        </div>

        <div class="status-description">
            {description}
        </div>

        <div class="section">
            <div class="section-title">Rainfall Summary</div>
            <div class="features">
                <div class="feature">
                    <div class="feature-label">Last 24h</div>
                    <div class="feature-value">{features["rain_1d"]:.1f}mm</div>
                </div>
                <div class="feature">
                    <div class="feature-label">Last 3 days</div>
                    <div class="feature-value">{features["rain_3d"]:.1f}mm</div>
                </div>
                <div class="feature">
                    <div class="feature-label">Last 7 days</div>
                    <div class="feature-value">{features["rain_7d"]:.1f}mm</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Recent Rainfall</div>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Rainfall</th>
                    </tr>
                </thead>
                <tbody>
                    {rain_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}<br>
            Data from <a href="https://environment.data.gov.uk/flood-monitoring/doc/reference" target="_blank">UK Environment Agency</a>
        </div>
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
