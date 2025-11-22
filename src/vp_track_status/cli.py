"""Command-line interface for Victoria Park Track Status."""

import argparse
import logging

from vp_track_status import __version__
from vp_track_status.constants import (
    DEFAULT_STATION_ID,
    MODEL_FILE,
    OBSERVATIONS_FILE,
    RAINFALL_FILE,
)
from vp_track_status.predict import predict_current_condition
from vp_track_status.rainfall import fetch_and_update
from vp_track_status.website import generate_site


def fetch_command(args):
    """Handle the fetch subcommand."""
    fetch_and_update(
        station_id=args.station_id,
        output_file=args.output,
        mode=args.mode,
        days=args.days,
        start_date=args.start_date,
        end_date=args.end_date,
    )


def train_command(args):
    """Handle the train subcommand."""
    try:
        from vp_track_status.model import train_and_export
    except ImportError as e:
        raise ImportError(
            "Training dependencies not installed. Install with: uv sync --group train"
        ) from e

    train_and_export(
        rainfall_file=args.rainfall,
        observations_file=args.observations,
        output_path=args.output,
    )


def predict_command(args):
    """Handle the predict subcommand."""
    result = predict_current_condition(
        model_path=args.model,
        rainfall_file=args.rainfall,
    )

    print(f"\nTrack Condition Prediction for {result['date']}")
    print(f"Prediction: {result['prediction_label']}")
    print("\nFeatures used:")
    for feature, value in result["features"].items():
        print(f"  {feature}: {value:.2f}mm")


def generate_site_command(args):
    """Handle the generate-site subcommand."""
    output_file = generate_site(output_dir=args.output_dir)
    print("\nWebsite generated successfully!")
    print(f"Output: {output_file}")


def main():
    """Main CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Victoria Park Track Status - Rainfall prediction system",
        prog="vp-track-status",
    )
    parser.add_argument(
        "--version", action="version", version=f"vp-track-status {__version__}"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch and update rainfall data")
    fetch_parser.add_argument(
        "--mode",
        choices=["historical", "latest"],
        default="latest",
        help="Fetch mode: 'historical' for full history or 'latest' for recent data only (default: latest)",
    )
    fetch_parser.add_argument(
        "--station-id",
        default=DEFAULT_STATION_ID,
        help=f"Station ID to fetch data from (default: {DEFAULT_STATION_ID})",
    )
    fetch_parser.add_argument(
        "--output",
        default=str(RAINFALL_FILE),
        help=f"Output CSV file path (default: {RAINFALL_FILE})",
    )
    fetch_parser.add_argument(
        "--start-date",
        help="Start date for historical mode (YYYY-MM-DD). If not provided, defaults to 90 days ago.",
    )
    fetch_parser.add_argument(
        "--end-date",
        help="End date for data fetch (YYYY-MM-DD). Defaults to today.",
    )
    fetch_parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to fetch in 'latest' mode (default: 7)",
    )
    fetch_parser.set_defaults(func=fetch_command)

    # Train command
    train_parser = subparsers.add_parser("train", help="Train and export model to ONNX")
    train_parser.add_argument(
        "--rainfall",
        default=str(RAINFALL_FILE),
        help=f"Path to rainfall CSV file (default: {RAINFALL_FILE})",
    )
    train_parser.add_argument(
        "--observations",
        default=str(OBSERVATIONS_FILE),
        help=f"Path to observations CSV file (default: {OBSERVATIONS_FILE})",
    )
    train_parser.add_argument(
        "--output",
        default=str(MODEL_FILE),
        help=f"Output path for ONNX model (default: {MODEL_FILE})",
    )
    train_parser.set_defaults(func=train_command)

    # Predict command
    predict_parser = subparsers.add_parser(
        "predict", help="Predict current track condition"
    )
    predict_parser.add_argument(
        "--model",
        default=str(MODEL_FILE),
        help=f"Path to ONNX model file (default: {MODEL_FILE})",
    )
    predict_parser.add_argument(
        "--rainfall",
        default=str(RAINFALL_FILE),
        help=f"Path to rainfall CSV file (default: {RAINFALL_FILE})",
    )
    predict_parser.set_defaults(func=predict_command)

    # Generate site command
    site_parser = subparsers.add_parser(
        "generate-site", help="Generate static website with current conditions"
    )
    site_parser.add_argument(
        "--output-dir",
        default="docs",
        help="Output directory for website (default: docs)",
    )
    site_parser.set_defaults(func=generate_site_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
