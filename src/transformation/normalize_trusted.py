"""Normalize raw FastF1 Parquet files into the trusted layer."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


DEFAULT_RAW_ROOT = Path("data/raw")
DEFAULT_TRUSTED_ROOT = Path("data/trusted")

UNIT_SUFFIXES = {
    "air_temp": "air_temp_c",
    "track_temp": "track_temp_c",
    "humidity": "humidity_pct",
    "wind_speed": "wind_speed_kmh",
    "speed": "speed_kmh",
    "speed_i1": "speed_i1_kmh",
    "speed_i2": "speed_i2_kmh",
    "speed_fl": "speed_fl_kmh",
    "speed_st": "speed_st_kmh",
    "distance": "distance_m",
    "distance_to_driver_ahead": "distance_to_driver_ahead_m",
    "x": "x_m",
    "y": "y_m",
    "z": "z_m",
    "throttle": "throttle_pct",
}

INTEGER_COLUMNS = {
    "lap_number",
    "stint",
    "tyre_life",
    "position",
    "grid_position",
    "n_gear",
    "drs",
    "wind_direction",
}

IDENTIFIER_COLUMNS = {
    "driver_number",
    "driver",
    "driver_ahead",
    "driver_id",
    "team_id",
    "abbreviation",
    "country_code",
}

UPPERCASE_IDENTIFIERS = {"driver", "driver_ahead", "abbreviation", "country_code"}


def snake_case(name: str) -> str:
    """Convert a FastF1 column name to the trusted naming convention."""
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    name = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
    return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()


def standard_name(name: str) -> str:
    name = snake_case(name)
    if name in UNIT_SUFFIXES:
        return UNIT_SUFFIXES[name]
    if name.endswith("_time") or name in {"time", "q1", "q2", "q3"}:
        return f"{name}_ms"
    return name


def normalize_identifiers(frame: pd.DataFrame) -> pd.DataFrame:
    for column in frame.columns:
        if column not in IDENTIFIER_COLUMNS:
            continue
        values = frame[column].astype("string").str.strip()
        if column in UPPERCASE_IDENTIFIERS:
            values = values.str.upper()
        frame[column] = values
    return frame


def normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.rename(columns={column: standard_name(column) for column in frame.columns}).copy()

    for column in renamed.columns:
        if pd.api.types.is_timedelta64_dtype(renamed[column]):
            renamed[column] = renamed[column].dt.total_seconds() * 1000
            if not column.endswith("_ms"):
                renamed = renamed.rename(columns={column: f"{column}_ms"})

    for column in renamed.columns:
        if pd.api.types.is_datetime64_any_dtype(renamed[column]):
            renamed[column] = pd.to_datetime(renamed[column], utc=True)

    for column in INTEGER_COLUMNS.intersection(renamed.columns):
        renamed[column] = pd.to_numeric(renamed[column], errors="coerce").round().astype("Int64")

    for column in renamed.select_dtypes(include=["object"]).columns:
        non_null = renamed[column].dropna()
        if not non_null.empty and non_null.map(lambda value: isinstance(value, bool)).all():
            renamed[column] = renamed[column].astype("boolean")

    return normalize_identifiers(renamed)


def transform_file(source_path: Path, raw_root: Path, trusted_root: Path, force: bool) -> Path:
    relative_path = source_path.relative_to(raw_root)
    target_path = trusted_root / relative_path
    if target_path.exists() and not force:
        raise FileExistsError(f"Trusted file already exists: {target_path}. Use --force to replace it.")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    normalize_frame(pd.read_parquet(source_path)).to_parquet(target_path, index=False)
    return target_path


def transform_dataset(raw_root: Path, trusted_root: Path, force: bool = False) -> int:
    source_files = sorted(raw_root.glob("season=*/round=*/session=*/*.parquet"))
    if not source_files:
        raise FileNotFoundError(f"No Parquet files found under {raw_root}")
    for source_path in source_files:
        target_path = transform_file(source_path, raw_root, trusted_root, force)
        print(f"Saved {target_path}")
    return len(source_files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--trusted-root", type=Path, default=DEFAULT_TRUSTED_ROOT)
    parser.add_argument("--force", action="store_true", help="Replace existing trusted files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = transform_dataset(args.raw_root, args.trusted_root, args.force)
    print(f"Transformed {count} Parquet files")


if __name__ == "__main__":
    main()
