"""Command-line interface for Victoria Park Track Status."""

import argparse
import sys

from vp_track_status.rainfall import fetch_and_update, DEFAULT_STATION_ID


def fetch_command(args):
    """Handle the fetch subcommand."""
    try:
        fetch_and_update(
            station_id=args.station_id,
            output_file=args.output,
            mode=args.mode,
            days=args.days,
            start_date=args.start_date,
            end_date=args.end_date,
            verbose=True,
        )
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Victoria Park Track Status - Rainfall prediction system",
        prog="vp-track-status",
    )
    parser.add_argument("--version", action="version", version="vp-track-status 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

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
        default="data/rainfall/rainfall_239374TP_daily.csv",
        help="Output CSV file path (default: data/rainfall/rainfall_239374TP_daily.csv)",
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

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
