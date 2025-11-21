# Victoria Park Track Status

**View current track conditions: [https://cdonnerer.github.io/vp-track-status/](https://cdonnerer.github.io/vp-track-status/)**

Predicts running conditions at the Victoria Park Athletics Track.

## Installation

```bash
uv sync
```

## Usage

```bash
# Fetch rainfall data
uv run vp-track-status fetch

# Train model
uv run vp-track-status train

# Generate prediction
uv run vp-track-status predict

# Generate website
uv run vp-track-status generate-site
```

## Data Sources

- **Rainfall**: UK Environment Agency Flood Monitoring API (Station 239374TP, Victoria Park)
- **Track Observations**: Manual observations stored in `data/observations/`

## Development

```bash
# Install dependencies
uv sync

# Install Git hooks (requires lefthook)
lefthook install
```
