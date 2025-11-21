"""
Fetch rainfall data from UK Environment Agency API.

Supports fetching historical data and incremental updates with upsert logic.
"""

from datetime import date, timedelta
from pathlib import Path

import polars as pl
import requests

# --- Configuration ---
PARAMETER = "rainfall"
ROOT_URL = "https://environment.data.gov.uk/flood-monitoring"
DEFAULT_STATION_ID = "239374TP"


def get_station_measures(station_id):
    """Fetch all rainfall measure IDs for a given station."""
    url = f"{ROOT_URL}/id/stations/{station_id}/measures"
    params = {"parameter": PARAMETER, "_limit": 10000}
    r = requests.get(url, params=params)
    r.raise_for_status()
    items = r.json().get("items", [])
    measure_ids = [m["@id"] for m in items]
    return measure_ids


def fetch_readings_for_measure(measure_id, start_date, end_date):
    """Fetch all readings for a specific rainfall measure."""
    url = f"{measure_id}/readings"
    params = {
        "startdate": start_date,
        "enddate": end_date,
        "_limit": 10000,
        "_sorted": "",
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("items", [])


def get_available_date_range(measure_id):
    """Get the earliest and latest available dates for a measure."""
    url = f"{measure_id}/readings"
    params = {"_limit": 5000, "_sorted": ""}
    r = requests.get(url, params=params)
    r.raise_for_status()
    readings = r.json().get("items", [])

    if not readings:
        return None, None

    # Readings are sorted newest first
    latest = readings[0]["dateTime"][:10]  # Extract YYYY-MM-DD
    earliest = readings[-1]["dateTime"][:10]

    return earliest, latest


def fetch_rainfall_data(station_id, start_date, end_date, verbose=True):
    """
    Fetch all rainfall readings for a station between start_date and end_date.

    Returns a Polars DataFrame with columns: dateTime, value
    """
    if verbose:
        print(f"Fetching rainfall data for station {station_id}")
        print(f"Date range requested: {start_date} to {end_date}")

    measures = get_station_measures(station_id)
    if not measures:
        raise ValueError(f"No rainfall measures found for station {station_id}")

    if verbose:
        print(f"Found {len(measures)} measure(s)")

    # Check available date range
    earliest_available, latest_available = get_available_date_range(measures[0])
    if earliest_available and latest_available and verbose:
        print(f"Data available from: {earliest_available} to {latest_available}")

    all_readings = []
    for m in measures:
        readings = fetch_readings_for_measure(m, start_date, end_date)
        all_readings.extend(readings)

    if not all_readings:
        if verbose:
            print("\nWARNING: No readings returned for this period")
            if earliest_available and latest_available:
                if start_date < earliest_available:
                    print(
                        f"  → Requested start date ({start_date}) is before earliest available data ({earliest_available})"
                    )
                if end_date > latest_available:
                    print(
                        f"  → Requested end date ({end_date}) is after latest available data ({latest_available})"
                    )
                print(
                    f"\n  Try using dates between {earliest_available} and {latest_available}"
                )
        return pl.DataFrame(schema={"dateTime": pl.Utf8, "value": pl.Float64})

    df = pl.DataFrame(all_readings)
    if verbose:
        print(f"Retrieved {len(df)} readings")
    return df.select(["dateTime", "value"])


def aggregate_daily(df):
    """
    Aggregate rainfall data to daily totals.

    Returns a Polars DataFrame with columns: date, rainfall_mm
    """
    if df.is_empty():
        return pl.DataFrame(schema={"date": pl.Date, "rainfall_mm": pl.Float64})

    daily = (
        df.with_columns(
            [
                pl.col("dateTime")
                .str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%SZ")
                .alias("dateTime"),
                pl.col("value").cast(pl.Float64, strict=False).alias("value"),
            ]
        )
        .drop_nulls(subset=["value", "dateTime"])
        .with_columns(pl.col("dateTime").dt.date().alias("date"))
        .group_by("date")
        .agg(pl.col("value").sum().alias("rainfall_mm"))
        .sort("date")
    )

    return daily


def load_existing_data(output_file):
    """Load existing CSV data if it exists."""
    path = Path(output_file)
    if not path.exists():
        return pl.DataFrame(schema={"date": pl.Date, "rainfall_mm": pl.Float64})

    df = pl.read_csv(output_file, try_parse_dates=True)
    # Ensure date column is Date type (may already be parsed)
    if "date" in df.columns and df["date"].dtype != pl.Date:
        df = df.with_columns(pl.col("date").str.to_date())

    # Only keep base columns, drop any derived columns (rolling windows)
    base_columns = ["date", "rainfall_mm"]
    df = df.select([col for col in base_columns if col in df.columns])

    return df


def upsert_data(existing_df, new_df):
    """
    Merge new data with existing data, updating overlapping dates.

    New data takes precedence over existing data for the same date.
    """
    if existing_df.is_empty():
        return new_df

    if new_df.is_empty():
        return existing_df

    # Combine and keep latest values (new data overwrites old)
    combined = (
        pl.concat([existing_df, new_df])
        .unique(subset=["date"], keep="last")
        .sort("date")
    )

    return combined


def save_data(df, output_file, verbose=True):
    """Save DataFrame to CSV."""
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(path)
    if verbose:
        print(f"Saved {len(df)} daily records to {output_file}")


def fetch_and_update(
    station_id=DEFAULT_STATION_ID,
    output_file="data/rainfall/rainfall_239374TP_daily.csv",
    mode="latest",
    days=7,
    start_date=None,
    end_date=None,
    verbose=True,
):
    """
    Fetch rainfall data and update local CSV file.

    Args:
        station_id: Station ID to fetch from
        output_file: Path to output CSV file
        mode: 'latest' for recent data or 'historical' for full history
        days: Number of days to fetch in 'latest' mode
        start_date: Start date for historical mode (YYYY-MM-DD)
        end_date: End date for data fetch (YYYY-MM-DD)
        verbose: Print progress messages

    Returns:
        Final DataFrame after update
    """
    # Determine date range
    today = date.today()
    end_date = end_date if end_date else str(today)

    if mode == "historical":
        if start_date:
            start_date = start_date
        else:
            # Default to 90 days ago for historical
            start_date = str(today - timedelta(days=90))
    else:  # latest mode
        start_date = str(today - timedelta(days=days))

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Rainfall Data Fetch - {mode.upper()} mode")
        print(f"{'=' * 60}\n")

    # Fetch raw data
    raw_df = fetch_rainfall_data(station_id, start_date, end_date, verbose=verbose)

    # Aggregate to daily
    if verbose:
        print("\nAggregating to daily totals...")
    daily_df = aggregate_daily(raw_df)
    if verbose:
        print(f"Aggregated to {len(daily_df)} days")

    # Load existing data
    if verbose:
        print(f"\nLoading existing data from {output_file}...")
    existing_df = load_existing_data(output_file)
    if verbose:
        print(f"Found {len(existing_df)} existing records")

    # Upsert
    if verbose:
        print("\nMerging data...")
    final_df = upsert_data(existing_df, daily_df)

    # Show summary of changes
    if verbose:
        new_records = len(final_df) - len(existing_df)
        if new_records > 0:
            print(f"Added {new_records} new record(s)")

        # Count updated records
        if not daily_df.is_empty() and not existing_df.is_empty():
            existing_dates = set(existing_df["date"].to_list())
            new_dates = set(daily_df["date"].to_list())
            updated_records = len(existing_dates & new_dates)
            if updated_records > 0:
                print(f"Updated {updated_records} existing record(s)")

    # Save
    save_data(final_df, output_file, verbose=verbose)

    if verbose:
        # Show recent data
        print("\nMost recent data:")
        print(final_df.tail(10))

        print(f"\n{'=' * 60}")
        print("SUCCESS")
        print(f"{'=' * 60}\n")

    return final_df
