# Victoria Park Track Status

Predict track running conditions at Victoria Park, London based on rainfall data from the UK Environment Agency.

## Project Overview

This project fetches rainfall data from the UK Environment Agency Flood Monitoring API, aggregates it daily, and uses machine learning to predict track conditions (Dry/Some puddles/Lots of puddles). The system runs automatically via GitHub Actions, updating data and predictions daily, and publishes results to a GitHub Pages website.

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

### Command-Line Interface

The package provides a comprehensive CLI:

```bash
# Fetch rainfall data
uv run vp-track-status fetch                    # Latest 7 days (default)
uv run vp-track-status fetch --days 30          # Latest 30 days
uv run vp-track-status fetch --mode historical  # Historical data

# Train the prediction model
uv run vp-track-status train

# Generate track condition prediction
uv run vp-track-status predict

# Generate static website
uv run vp-track-status generate-site
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

## Automated Updates & Deployment

The project includes two GitHub Actions workflows:

### Data Update (`.github/workflows/update_data.yml`)
1. Runs daily at 6 AM UTC
2. Fetches the latest 7 days of rainfall data
3. Updates the CSV file in `data/rainfall/`
4. Commits changes back to the repository

### Website Deployment (`.github/workflows/deploy_website.yml`)
1. Runs daily at 7 AM UTC (after data update)
2. Generates prediction for current track conditions
3. Creates static HTML website
4. Deploys to GitHub Pages

Both workflows can be triggered manually via the Actions tab on GitHub.

### GitHub Pages Setup

To enable the website:
1. Go to repository Settings → Pages
2. Under "Build and deployment", select "GitHub Actions" as the source
3. The website will be available at `https://<username>.github.io/<repository>/`

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
