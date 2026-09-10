import argparse
from pathlib import Path

import pandas as pd

from src.ingestion.fastf1_loader import (
    get_laps,
    get_session,
    get_telemetry,
    get_weather,
)
from src.ingestion.raw_writer import save_dataframe


SESSION_TYPES = {
    "race": "R",
    "qualifying": "Q",
    "practice": "FP1",
    "fp1": "FP1",
    "fp2": "FP2",
    "fp3": "FP3",
    "sprint": "S",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Extract a FastF1 session and persist its raw data as Parquet.")
    parser.add_argument("--year", type=int, required=True, help="Season year.")
    parser.add_argument(
        "--round",
        type=int,
        required=True,
        dest="round_number",
        help="Race round number.",
    )
    parser.add_argument(
        "--session",
        choices=sorted(SESSION_TYPES),
        required=True,
        help="Session type, such as race or qualifying.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Root directory for raw Parquet files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite files that already exist.",
    )
    return parser.parse_args()


def save_if_needed(dataframe, path, force):
    if path.exists() and not force:
        print(f"Skipping existing file: {path}")
        return
    save_dataframe(dataframe, path)
    print(f"Saved {len(dataframe)} rows: {path}")


def extract_telemetry(laps):
    telemetry_frames = []
    for lap_index, (_, lap) in enumerate(laps.iterrows(), start=1):
        try:
            telemetry = get_telemetry(lap)
        except (KeyError, RuntimeError, ValueError) as exc:
            print(f"Skipping telemetry for lap {lap_index}: {exc}")
            continue

        if telemetry is None or telemetry.empty:
            continue

        telemetry = telemetry.copy()
        telemetry["Driver"] = lap["Driver"]
        telemetry["DriverNumber"] = lap["DriverNumber"]
        telemetry["LapNumber"] = lap["LapNumber"]
        telemetry_frames.append(telemetry)

    if not telemetry_frames:
        return pd.DataFrame()
    return pd.concat(telemetry_frames, ignore_index=True)


def run_ingestion(year, round_number, session_name, output_dir, force=False):
    session_type = SESSION_TYPES[session_name]
    session = get_session(year, round_number, session_type)
    laps = get_laps(session)

    session_dir = output_dir / f"season={year}" / f"round={round_number:02d}" / f"session={session_name}"

    save_if_needed(session.results, session_dir / "drivers.parquet", force)
    save_if_needed(laps, session_dir / "laps.parquet", force)
    save_if_needed(get_weather(session), session_dir / "weather.parquet", force)

    telemetry_path = session_dir / "telemetry.parquet"
    if telemetry_path.exists() and not force:
        print(f"Skipping existing file: {telemetry_path}")
    else:
        telemetry = extract_telemetry(laps)
        save_if_needed(telemetry, telemetry_path, force)


def main():
    args = parse_args()
    run_ingestion(
        year=args.year,
        round_number=args.round_number,
        session_name=args.session,
        output_dir=args.output_dir,
        force=args.force,
    )


if __name__ == "__main__":
    main()
