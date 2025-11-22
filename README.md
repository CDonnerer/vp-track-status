# Victoria Park Track Status

Predicts running conditions at Victoria Park Athletics Track based on rainfall.

**[View current track conditions →](https://cdonnerer.github.io/vp-track-status/)**

## How It Works

- **Data**: Rainfall from UK Environment Agency API (Station 239374TP) + manual track observations
- **Model**: ML model predicting track conditions (Dry/Some puddles/Lots of puddles) from rolling rainfall features
- **Updates**: Automated daily at 6 AM UTC via GitHub Actions

## Development

```bash
# Install dependencies
uv sync

# Install Git hooks (requires lefthook)
lefthook install

# CLI commands
uv run vp-track-status fetch    # Fetch rainfall data
uv run vp-track-status train    # Train model
uv run vp-track-status predict  # Generate prediction
```
