# Victoria Park Track Status

Predict track running conditions at Victoria Park, London based on rainfall data from the UK Environment Agency.

## Project Overview

This project fetches rainfall data from the UK Environment Agency Flood Monitoring API, aggregates it daily, and will eventually use machine learning to predict track conditions (Dry/Some puddles/Lots of puddles). The system is designed to run automatically via GitHub Actions, updating data daily.

## Project Structure

```
vp-track-status/
├── src/vp_track_status/       # Installable Python package
│   ├── __init__.py
│   ├── rainfall.py            # Rainfall data fetching and aggregation
│   └── cli.py                 # Command-line interface
├── data/                       # Version-controlled data
│   ├── rainfall/              # Daily rainfall data
│   ├── observations/          # Manual track condition observations
│   └── predictions/           # Model predictions (future)
├── scripts/
│   └── update_data.sh         # Entry point for automated updates
├── .github/workflows/
│   └── update_data.yml        # GitHub Actions workflow
├── pyproject.toml             # Package configuration
└── README.md
```

## Installation

This project uses `uv` for dependency management.

```bash
# Install dependencies and package
uv sync

# Verify installation
uv run vp-track-status --help
```

## Usage

### Fetch Rainfall Data

The package provides a CLI for fetching rainfall data:

```bash
# Fetch latest 7 days (default)
uv run vp-track-status fetch

# Fetch latest 30 days
uv run vp-track-status fetch --days 30

# Fetch historical data (defaults to last 90 days)
uv run vp-track-status fetch --mode historical

# Fetch specific date range
uv run vp-track-status fetch --mode historical --start-date 2024-01-01 --end-date 2024-12-31

# Custom output location
uv run vp-track-status fetch --output data/rainfall/custom.csv
```

### Using as a Python Module

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

## Automated Data Updates

The project includes a GitHub Actions workflow (`.github/workflows/update_data.yml`) that:

1. Runs daily at 6 AM UTC
2. Fetches the latest 7 days of rainfall data
3. Updates the CSV file in `data/rainfall/`
4. Commits changes back to the repository

The workflow can also be triggered manually via the Actions tab on GitHub.

## Data Sources

- **Rainfall Data**: UK Environment Agency Flood Monitoring API
  - Station: 239374TP (Victoria Park, London)
  - Location: 51.536°N, -0.053°W
  - API: https://environment.data.gov.uk/flood-monitoring

- **Track Observations**: Manual observations from Google Forms
  - File: `data/observations/track_observations.csv`

## Development

### Setup

```bash
# Install dependencies
uv sync

# Install lefthook Git hooks
lefthook install
```

### Pre-commit Hooks

This project uses [lefthook](https://github.com/evilmartians/lefthook) to run pre-commit hooks:

- **ruff check**: Lints staged Python files
- **ruff format**: Formats staged Python files

Install lefthook:

```bash
# macOS
brew install lefthook

# Then install hooks in the project
lefthook install
```

Run hooks manually:

```bash
lefthook run pre-commit
```

### Testing the Update Script

```bash
# Run the update script locally
bash scripts/update_data.sh
```
