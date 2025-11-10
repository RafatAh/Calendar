import os
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd
from sklearn.preprocessing import StandardScaler


def _discover_data_dir() -> Optional[Path]:
    """Discover the data directory using env vars or common directory names."""
    env_keys = ("DATA_DIR", "DATA", "UNLOCK_DATA_DIR")
    for key in env_keys:
        value = os.environ.get(key)
        if value:
            candidate = Path(value).expanduser()
            if candidate.is_dir():
                return candidate

    module_dir = Path(__file__).resolve().parent
    candidate_names = ("data", "dataset", "datasets", "unlock_data")
    for name in candidate_names:
        candidate = module_dir / name
        if candidate.is_dir():
            return candidate

    cwd = Path.cwd()
    if cwd != module_dir:
        for name in candidate_names:
            candidate = cwd / name
            if candidate.is_dir():
                return candidate

    return None


def _list_csv_files(data_dir: Path) -> Iterable[Path]:
    return sorted(path for path in data_dir.iterdir() if path.suffix.lower() == ".csv")


def _filter_unlock_events(record: pd.DataFrame) -> pd.DataFrame:
    if record.empty:
        return record

    record = record.copy()
    unlock_mask = pd.Series(False, index=record.index)

    for column in record.columns:
        series = record[column]

        if pd.api.types.is_string_dtype(series) or series.dtype == object:
            contains_unlock = series.astype(str).str.contains("unlock", case=False, na=False)
            if contains_unlock.any():
                unlock_mask = unlock_mask | contains_unlock

        if column.lower() in {"unlock", "unlocked", "is_unlock"}:
            if pd.api.types.is_bool_dtype(series):
                unlock_mask = unlock_mask | series.fillna(False)
            elif pd.api.types.is_numeric_dtype(series):
                unlock_mask = unlock_mask | (series.fillna(0).astype(int) != 0)

    if unlock_mask.any():
        return record[unlock_mask]

    return record


def compute_daily_activity_pattern(files: Iterable[Path]) -> pd.DataFrame:
    res: Dict[str, Dict[int, float]] = {}

    for file_path in files:
        record = pd.read_csv(file_path)
        uid = file_path.stem

        record = _filter_unlock_events(record)

        if "ts" not in record.columns:
            raise KeyError(f"Column 'ts' missing in file {file_path}")

        record["ts"] = pd.to_datetime(record["ts"], errors="coerce", utc=True)
        record = record.dropna(subset=["ts"])

        if record.empty:
            n_days = 1
        else:
            min_day = record["ts"].min().normalize()
            max_day = record["ts"].max().normalize()
            n_days = int((max_day - min_day).days) + 1
            n_days = max(n_days, 1)

        hour_counts = (
            record["ts"]
            .dt.tz_convert(None)
            .dt.hour.value_counts()
            .reindex(range(24), fill_value=0)
            .sort_index()
        )

        u_res = (hour_counts / n_days).to_dict()
        res[uid] = u_res

    df = pd.DataFrame.from_dict(res)
    if not df.empty:
        df = df.reindex(range(24))
        df = df.sort_index()
        df = df.fillna(0.0)

        scaler = StandardScaler()
        scaled = scaler.fit_transform(df.to_numpy(dtype=float))
        df = pd.DataFrame(scaled, index=df.index, columns=df.columns)
    else:
        df = df.reindex(range(24))
        df = df.fillna(0.0)

    return df


DATA_DIR = _discover_data_dir()
if DATA_DIR is not None:
    FILES = _list_csv_files(DATA_DIR)
else:
    FILES = []

df = compute_daily_activity_pattern(FILES) if FILES else pd.DataFrame()

