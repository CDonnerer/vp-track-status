# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Victoria Park Track Status is a Python project that predicts track running conditions at Victoria Park, London based on rainfall data. The system fetches rainfall data from UK Environment Agency APIs, aggregates it daily, and will use machine learning to predict track conditions (Dry/Some puddles/Lots of puddles).

The project runs automated daily updates via GitHub Actions, fetching and storing rainfall data in version control.

## Project Structure

```
vp-track-status/
├── src/vp_track_status/       # Installable Python package
│   ├── __init__.py
│   ├── rainfall.py            # Rainfall data fetching and aggregation
│   └── cli.py                 # Command-line interface
├── data/                       # Version-controlled data
│   ├── rainfall/              # Daily rainfall data (CSV)
│   ├── observations/          # Manual track condition observations (CSV)
│   └── predictions/           # Model predictions (future)
├── scripts/
│   └── update_data.sh         # Entry point for automated updates
├── .github/workflows/
│   └── update_data.yml        # GitHub Actions workflow for daily updates
├── rain.py                    # Legacy script (use src/vp_track_status instead)
├── get_waterfall_data.py      # Legacy script
├── create_dataset.py          # Legacy script for ML training
├── maps.py                    # Experimental geospatial tools
├── pyproject.toml             # Package configuration
├── lefthook.yml               # Git hooks (ruff check & format)
└── vicpark_track.geojson      # Track boundary coordinates
```

## Development Setup

This project uses `uv` for dependency management and `lefthook` for Git hooks.

```bash
# Install dependencies and package
uv sync

# Install lefthook Git hooks (requires lefthook to be installed)
lefthook install

# Verify installation
uv run vp-track-status --help
```

### Pre-commit Hooks

Lefthook runs `ruff check` and `ruff format` on staged Python files automatically. Install lefthook:

```bash
# macOS
brew install lefthook

# Then install hooks in the project
lefthook install
```

## Testing

The project uses pytest for testing. Tests cover feature generation and model training:

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v
```

Tests run automatically in CI via `.github/workflows/test.yml` on push and pull requests.

Current test coverage:
- `tests/test_features.py`: Tests rolling window feature generation
- `tests/test_model.py`: Tests model training and prediction

## Usage

### Command-Line Interface

The package provides a CLI for data fetching, model training, prediction, and website generation:

```bash
# Fetch latest rainfall data
uv run vp-track-status fetch                    # Latest 7 days (default)
uv run vp-track-status fetch --days 30          # Latest 30 days
uv run vp-track-status fetch --mode historical  # Historical (90 days default)

# Train model
uv run vp-track-status train

# Generate prediction
uv run vp-track-status predict

# Generate static website
uv run vp-track-status generate-site
uv run vp-track-status generate-site --output-dir custom/path
```

### Python Module Usage

```python
from vp_track_status.rainfall import fetch_and_update

# Fetch latest 7 days and update local CSV
df = fetch_and_update(
    station_id="239374TP",
    output_file="data/rainfall/rainfall_239374TP_daily.csv",
    mode="latest",
    days=7
)
```

## Architecture

### Current Implementation

The main package (`src/vp_track_status/`) provides:

1. **Data Collection** (`rainfall.py`)
   - Fetches rainfall data from UK Environment Agency Flood Monitoring API
   - Location: Victoria Park, London (lat: 51.536, lon: -0.053)
   - Station: 239374TP (nearest rainfall monitoring station)
   - API root: `https://environment.data.gov.uk/flood-monitoring`
   - Aggregates raw readings into daily totals
   - Supports incremental updates (upsert logic)
   - Uses Polars for data processing

2. **Automated Updates** (`scripts/update_data.sh`, `.github/workflows/update_data.yml`)
   - GitHub Actions workflow runs daily at 6 AM UTC
   - Fetches latest 7 days of rainfall data
   - Updates `data/rainfall/rainfall_239374TP_daily.csv`
   - Commits changes back to repository

3. **Model Training & Prediction** (`model.py`, `predict.py`)
   - Train models using rainfall data and manual observations
   - Exports model to ONNX format for deployment
   - Generates predictions for current track conditions
   - Uses rolling window features (1d, 2d, 3d, 5d, 7d rainfall)

4. **Website Generation** (`website.py`, `.github/workflows/deploy_website.yml`)
   - Generates static HTML website displaying current track conditions
   - Deployed to GitHub Pages automatically
   - Updates daily after rainfall data fetch (7 AM UTC)
   - Shows prediction, recent rainfall, and last update time

### Legacy Scripts

Root-level scripts are legacy code from initial development:
- `rain.py`: Original API wrapper (superseded by `src/vp_track_status/rainfall.py`)
- `get_waterfall_data.py`: Direct station-based fetcher
- `create_dataset.py`: ML training pipeline (uses pandas, not integrated with new package)
- `maps.py`: Experimental Sentinel-1 satellite imagery tools

### GitHub Pages Deployment

The project uses GitHub Pages to serve a static website showing current track conditions:

1. **Setup** (one-time):
   - Go to repository Settings → Pages
   - Under "Build and deployment", select "GitHub Actions" as the source
   - The deploy_website.yml workflow will handle deployment

2. **Automated deployment**:
   - Runs daily at 7 AM UTC (after data update at 6 AM UTC)
   - Triggers automatically when data update workflow completes
   - Can be manually triggered via "Actions" tab

3. **Local testing**:
   ```bash
   uv run vp-track-status generate-site
   open docs/index.html  # View locally
   ```

## Data Sources

- **Rainfall Data**: UK Environment Agency Flood Monitoring API
  - Station: 239374TP (Victoria Park, London)
  - Location: 51.536°N, -0.053°W
  - Stored in: `data/rainfall/rainfall_239374TP_daily.csv`

- **Track Observations**: Manual observations from Google Forms
  - File: `data/observations/track_observations.csv`

- **Geographic Data**: Track boundary
  - File: `vicpark_track.geojson`

## API Usage Patterns

When working with the UK Environment Agency API:

- **Station queries**: `{ROOT_URL}/id/stations?parameter=rainfall&lat={lat}&long={lon}&dist={radius_km}`
- **Readings endpoint**: `{ROOT_URL}/data/readings?measure={measure_id}&startdate={start}&enddate={end}&_sorted`
- **Station measures**: `{ROOT_URL}/id/stations/{station_id}/measures`

The API returns JSON with an `items` array containing the actual data.

## Python Style Guide

This project prioritizes clean, concise, self-documenting code:

### Documentation
- **Minimal docstrings**: Only add docstrings for public APIs and complex functions where the purpose isn't obvious
- **No redundant comments**: Avoid comments that simply restate what the code does
- **Module-level docstrings**: Brief description only when the module purpose isn't clear from the filename
- **Prefer clear naming**: Use descriptive variable and function names instead of comments

### Code Style
- **Clean and concise**: Write straightforward code; avoid over-engineering
- **Self-documenting**: Code should be readable without extensive comments
- **Ruff formatting**: All code is auto-formatted via pre-commit hooks
- **Type hints**: Use when they clarify intent, but don't require them everywhere

### Examples

Good:
```python
def aggregate_daily(df):
    """Aggregate rainfall data to daily totals."""
    if df.is_empty():
        return pl.DataFrame(schema={"date": pl.Date, "rainfall_mm": pl.Float64})

    daily = (
        df.with_columns(...)
        .drop_nulls(subset=["value", "dateTime"])
        .group_by("date")
        .agg(pl.col("value").sum().alias("rainfall_mm"))
    )
    return daily
```

Avoid:
```python
def aggregate_daily(df):
    """
    Aggregate rainfall data to daily totals.

    This function takes a DataFrame with dateTime and value columns,
    converts the dateTime to dates, groups by date, and sums the values.
    It handles empty DataFrames by returning an empty DataFrame with the
    correct schema.

    Args:
        df (pl.DataFrame): Input DataFrame with dateTime and value columns

    Returns:
        pl.DataFrame: DataFrame with date and rainfall_mm columns
    """
    # Check if dataframe is empty
    if df.is_empty():
        # Return empty DataFrame with correct schema
        return pl.DataFrame(schema={"date": pl.Date, "rainfall_mm": pl.Float64})

    # Aggregate the data by date
    daily = (
        df.with_columns(...)  # Parse datetime and cast value
        .drop_nulls(subset=["value", "dateTime"])  # Remove null values
        .group_by("date")  # Group by date
        .agg(pl.col("value").sum().alias("rainfall_mm"))  # Sum rainfall
    )
    return daily  # Return aggregated data
```
