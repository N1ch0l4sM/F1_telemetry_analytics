"""Combine trusted round partitions into curated Parquet tables."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import fastf1
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


TABLES = ("drivers", "teams", "circuits", "sessions", "laps", "telemetry", "weather")
DEFAULT_TRUSTED_ROOT = Path("data/trusted")
DEFAULT_CURATED_ROOT = Path("data/curated")


def slug(value: object) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")
    return text or "unknown"


def session_id(season: int, round_number: int, session_type: str) -> str:
    return f"{season}_{round_number:02d}_{session_type}"


def load_schedule(season: int) -> pd.DataFrame:
    fastf1.Cache.enable_cache(str(Path("cache/fastf1")))
    schedule = fastf1.get_event_schedule(season, include_testing=False).copy()
    schedule["round"] = pd.to_numeric(schedule["RoundNumber"], errors="coerce").astype("Int64")
    schedule["circuit_id"] = schedule["Location"].map(slug)
    schedule["event_date"] = pd.to_datetime(schedule["EventDate"], utc=True)
    return schedule.set_index("round")


def partition_metadata(path: Path, schedule: pd.DataFrame) -> dict:
    season = int(path.parts[-3].split("=", 1)[1])
    round_number = int(path.parts[-2].split("=", 1)[1])
    session_type = path.parts[-1].split("=", 1)[1]
    event = schedule.loc[round_number] if round_number in schedule.index else None
    event_name = event["EventName"] if event is not None else f"Round {round_number}"
    circuit_id = event["circuit_id"] if event is not None else f"round_{round_number:02d}"
    event_date = event["event_date"] if event is not None else pd.NaT
    return {
        "season": season,
        "round": round_number,
        "session_type": session_type,
        "session_id": session_id(season, round_number, session_type),
        "event_name": event_name,
        "circuit_id": circuit_id,
        "event_date": event_date,
    }


def add_metadata(frame: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    result = frame.copy()
    for column, value in reversed(list(metadata.items())):
        result.insert(0, column, value)
    return result


def build_session_and_circuit(metadata: dict, schedule: pd.DataFrame, laps: pd.DataFrame) -> tuple[dict, dict]:
    event = schedule.loc[metadata["round"]] if metadata["round"] in schedule.index else None
    session_date = laps["lap_start_date"].min() if "lap_start_date" in laps else pd.NaT
    session = {
        "session_id": metadata["session_id"],
        "season": metadata["season"],
        "round": metadata["round"],
        "session_type": metadata["session_type"],
        "event_name": metadata["event_name"],
        "circuit_id": metadata["circuit_id"],
        "event_date": metadata["event_date"],
        "session_date": session_date,
    }
    circuit = {
        "circuit_id": metadata["circuit_id"],
        "season": metadata["season"],
        "round": metadata["round"],
        "event_name": metadata["event_name"],
        "location": event["Location"] if event is not None else None,
        "country": event["Country"] if event is not None else None,
        "event_date": metadata["event_date"],
    }
    return session, circuit


def write_frame(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def write_telemetry(chunks: list[pd.DataFrame], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    target_schema = None
    try:
        for chunk in chunks:
            table = pa.Table.from_pandas(chunk, preserve_index=False)
            if writer is None:
                target_schema = table.schema
                writer = pq.ParquetWriter(path, target_schema)
            else:
                table = table.cast(target_schema)
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()


def build_curated(trusted_root: Path, curated_root: Path, season: int, force: bool = False) -> dict[str, int]:
    if force and curated_root.exists():
        shutil.rmtree(curated_root)
    curated_root.mkdir(parents=True, exist_ok=True)
    schedule = load_schedule(season)
    partitions = sorted(trusted_root.glob(f"season={season}/round=*/session=*"))
    if not partitions:
        raise FileNotFoundError(f"No trusted partitions found under {trusted_root}")

    drivers, teams, circuits, sessions, laps, weather = [], [], [], [], [], []
    telemetry_chunks = []
    driver_map: dict[tuple[str, str], str] = {}
    counts = {table: 0 for table in TABLES}

    for partition in partitions:
        metadata = partition_metadata(partition, schedule)
        driver_frame = pd.read_parquet(partition / "drivers.parquet")
        lap_frame = pd.read_parquet(partition / "laps.parquet")
        telemetry_frame = pd.read_parquet(partition / "telemetry.parquet")
        weather_frame = pd.read_parquet(partition / "weather.parquet")
        session, circuit = build_session_and_circuit(metadata, schedule, lap_frame)
        sessions.append(session)
        circuits.append(circuit)

        driver_frame["driver_id"] = driver_frame["driver_id"].astype("string")
        driver_frame["team_id"] = driver_frame["team_id"].astype("string")
        for row in driver_frame[["abbreviation", "driver_id"]].dropna().drop_duplicates().itertuples(index=False):
            driver_map[(metadata["session_id"], row.abbreviation)] = row.driver_id
        drivers.append(driver_frame.assign(season=metadata["season"]))
        teams.append(driver_frame[["team_id", "team_name", "team_color"]].drop_duplicates())

        for frame, collection, table in [
            (lap_frame, laps, "laps"),
            (weather_frame, weather, "weather"),
        ]:
            enriched = add_metadata(frame, metadata)
            if table == "laps":
                enriched["driver_id"] = (
                    enriched["driver"].map(lambda value: driver_map.get((metadata["session_id"], value))).astype("string")
                )
            collection.append(enriched)
            counts[table] += len(enriched)

        telemetry_frame = add_metadata(telemetry_frame, metadata)
        telemetry_frame["driver_id"] = (
            telemetry_frame["driver"].map(lambda value: driver_map.get((metadata["session_id"], value))).astype("string")
        )
        telemetry_chunks.append(telemetry_frame)
        counts["telemetry"] += len(telemetry_frame)

    curated_drivers = pd.concat(drivers, ignore_index=True).drop_duplicates(["season", "driver_id", "team_id", "driver_number"])
    curated_teams = pd.concat(teams, ignore_index=True).drop_duplicates("team_id")
    write_frame(curated_drivers, curated_root / "drivers.parquet")
    write_frame(curated_teams, curated_root / "teams.parquet")
    write_frame(pd.DataFrame(circuits).drop_duplicates("circuit_id"), curated_root / "circuits.parquet")
    write_frame(pd.DataFrame(sessions).drop_duplicates("session_id"), curated_root / "sessions.parquet")
    write_frame(pd.concat(laps, ignore_index=True), curated_root / "laps.parquet")
    write_frame(pd.concat(weather, ignore_index=True), curated_root / "weather.parquet")
    write_telemetry(telemetry_chunks, curated_root / "telemetry.parquet")
    counts["drivers"] = len(curated_drivers)
    counts["teams"] = len(curated_teams)
    counts["circuits"] = len(pd.DataFrame(circuits).drop_duplicates("circuit_id"))
    counts["sessions"] = len(pd.DataFrame(sessions).drop_duplicates("session_id"))
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trusted-root", type=Path, default=DEFAULT_TRUSTED_ROOT)
    parser.add_argument("--curated-root", type=Path, default=DEFAULT_CURATED_ROOT)
    parser.add_argument("--season", type=int, default=2022)
    parser.add_argument("--force", action="store_true", help="Replace the curated directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    counts = build_curated(args.trusted_root, args.curated_root, args.season, args.force)
    print(pd.Series(counts, name="rows").to_string())


if __name__ == "__main__":
    main()
