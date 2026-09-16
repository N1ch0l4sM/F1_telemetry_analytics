"""Run data-quality checks against normalized trusted Parquet files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_TRUSTED_ROOT = Path("data/trusted")
TIMESTAMP_COLUMNS = {"date", "lap_start_date"}
REQUIRED_COLUMNS = {
    "drivers": {"driver_number", "driver_id", "abbreviation"},
    "laps": {"driver", "driver_number", "lap_number"},
    "telemetry": {"date", "driver", "driver_number", "lap_number"},
}


def result(
    check: str,
    table: str,
    partition: str,
    total: int,
    violations: int,
    details: str,
    passed: bool | None = None,
) -> dict:
    percentage = (violations / total * 100) if total else 0.0
    return {
        "check": check,
        "table": table,
        "partition": partition,
        "passed": violations == 0 if passed is None else passed,
        "total": total,
        "violations": violations,
        "violation_pct": round(percentage, 4),
        "details": details,
    }


def check_duplicates(frame: pd.DataFrame, table: str, partition: str) -> dict:
    # Weather is aligned to lap samples, so repeated readings at the same time
    # are expected and are not duplicate observations in this layer.
    if table == "weather":
        return result(
            "duplicate_records",
            table,
            partition,
            len(frame),
            0,
            "not enforced: readings are repeated while aligned to lap samples",
        )
    key_columns = {
        "drivers": ["driver_number"],
        "laps": ["driver", "lap_number"],
        "telemetry": ["driver", "lap_number", "date"],
    }.get(table)
    duplicate_rows = frame.duplicated(key_columns, keep=False) if key_columns else frame.duplicated(keep=False)
    violations = int(duplicate_rows.sum())
    return result("duplicate_records", table, partition, len(frame), violations, f"key={key_columns or 'all columns'}")


def check_nulls(frame: pd.DataFrame, table: str, partition: str) -> list[dict]:
    checks = []
    required_columns = REQUIRED_COLUMNS.get(table, set())
    for column in frame.columns:
        null_count = int(frame[column].isna().sum())
        checks.append(
            result(
                "null_percentage",
                table,
                partition,
                len(frame),
                null_count,
                f"{column}; required={column in required_columns}",
                passed=column not in required_columns or null_count == 0,
            )
        )
    return checks


def check_lap_times(frame: pd.DataFrame, table: str, partition: str) -> dict | None:
    if table != "laps" or "lap_time_ms" not in frame:
        return None
    invalid = frame["lap_time_ms"].notna() & ~frame["lap_time_ms"].between(1, 10 * 60 * 1000)
    violations = int(invalid.sum())
    return result("invalid_lap_time", table, partition, len(frame), violations, "must be between 1 ms and 10 minutes")


def check_drivers(frame: pd.DataFrame, table: str, partition: str, known_drivers: set[str]) -> dict | None:
    if table not in {"drivers", "laps", "telemetry"}:
        return None
    if "driver" in frame:
        invalid = frame["driver"].isna() | ~frame["driver"].astype("string").str.fullmatch(r"[A-Z]{3}", na=False)
        details = "driver must be a three-letter uppercase code"
    elif "abbreviation" in frame:
        invalid = frame["abbreviation"].isna() | ~frame["abbreviation"].astype("string").str.fullmatch(r"[A-Z]{3}", na=False)
        details = "abbreviation must be a three-letter uppercase code"
    else:
        return None
    if known_drivers and table in {"laps", "telemetry"}:
        invalid |= ~frame["driver"].isin(known_drivers)
        details += "; driver must exist in drivers table"
    return result("invalid_driver", table, partition, len(frame), int(invalid.sum()), details)


def check_missing_telemetry(laps: pd.DataFrame, telemetry: pd.DataFrame, partition: str) -> dict:
    lap_keys = laps[["driver", "lap_number"]].dropna().drop_duplicates()
    telemetry_keys = telemetry[["driver", "lap_number"]].dropna().drop_duplicates()
    missing = lap_keys.merge(telemetry_keys, on=["driver", "lap_number"], how="left", indicator=True)
    missing_keys = missing.loc[missing["_merge"] == "left_only", ["driver", "lap_number"]]
    violations = len(missing_keys)
    missing_examples = missing_keys.astype({"lap_number": "int64"}).to_dict("records")[:10]
    return result(
        "missing_telemetry",
        "laps",
        partition,
        len(lap_keys),
        violations,
        f"each non-null driver/lap_number pair must have telemetry; missing={missing_examples}",
    )


def check_timestamps(frame: pd.DataFrame, table: str, partition: str) -> list[dict]:
    checks = []
    for column in sorted(TIMESTAMP_COLUMNS.intersection(frame.columns)):
        timestamp = frame[column]
        invalid_type = not isinstance(timestamp.dtype, pd.DatetimeTZDtype)
        if invalid_type:
            violations = len(frame)
            details = "timestamp must be timezone-aware UTC"
        else:
            invalid_values = (
                timestamp.isna()
                | (timestamp < pd.Timestamp("2018-01-01", tz="UTC"))
                | (timestamp > pd.Timestamp("2030-12-31", tz="UTC"))
            )
            violations = int(invalid_values.sum())
            details = "non-null UTC timestamp between 2018 and 2030"
        checks.append(result("invalid_timestamp", table, partition, len(frame), violations, f"{column}: {details}"))
    return checks


def validate_partition(session_path: Path) -> list[dict]:
    partition = str(session_path)
    frames = {path.stem: pd.read_parquet(path) for path in sorted(session_path.glob("*.parquet"))}
    known_drivers = set()
    drivers = frames.get("drivers")
    if drivers is not None and "abbreviation" in drivers:
        known_drivers = set(drivers["abbreviation"].dropna().astype("string"))

    checks: list[dict] = []
    for table, frame in frames.items():
        checks.append(check_duplicates(frame, table, partition))
        checks.extend(check_nulls(frame, table, partition))
        lap_time_check = check_lap_times(frame, table, partition)
        if lap_time_check:
            checks.append(lap_time_check)
        driver_check = check_drivers(frame, table, partition, known_drivers)
        if driver_check:
            checks.append(driver_check)
        checks.extend(check_timestamps(frame, table, partition))
    if "laps" in frames and "telemetry" in frames:
        checks.append(check_missing_telemetry(frames["laps"], frames["telemetry"], partition))
    return checks


def validate_dataset(trusted_root: Path) -> pd.DataFrame:
    sessions = sorted(trusted_root.glob("season=*/round=*/session=*"))
    if not sessions:
        raise FileNotFoundError(f"No trusted partitions found under {trusted_root}")
    checks = [check for session in sessions for check in validate_partition(session)]
    return pd.DataFrame(checks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trusted-root", type=Path, default=DEFAULT_TRUSTED_ROOT)
    parser.add_argument("--report", type=Path, help="Optional CSV output path for the detailed report.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = validate_dataset(args.trusted_root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        report.to_csv(args.report, index=False)
    failures = report[~report["passed"]]
    summary = report.groupby("check", as_index=False).agg(
        checks=("check", "size"), failures=("passed", lambda values: int((~values).sum()))
    )
    print(summary.to_string(index=False))
    print(f"Total checks: {len(report)}; failures: {len(failures)}")
    if not failures.empty:
        print(failures.head(20).to_string(index=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
