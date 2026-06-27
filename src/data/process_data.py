from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# Allow imports when running `python src/data/process_data.py` from project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from pca_anomaly_detection.config import apply_column_name_map, load_column_name_map

FAULT_DESCRIPTIONS: dict[int, str] = {
    1: "A/C feed ratio, B composition constant (Stream 4)",
    2: "B composition, A/C ratio constant (Stream 4)",
    3: "D feed temperature (Stream 2)",
    4: "Reactor cooling water inlet temperature",
    5: "Condenser cooling water inlet temperature",
    6: "A feed loss (Stream 1)",
    7: "C header pressure loss-reduced availability (Stream 4)",
    8: "A, B, C feed composition (Stream 4)",
    9: "D feed temperature (Stream 2)",
    10: "C feed temperature (Stream 4)",
    11: "Reactor cooling water inlet temperature",
    12: "Condenser cooling water inlet temperature",
    13: "Reaction kinetics",
    14: "Reactor cooling water valve",
    15: "Condenser cooling water valve",
    16: "Unknown",
    17: "Unknown",
    18: "Unknown",
    19: "Unknown",
    20: "Unknown",
    21: "The valve for Stream 4 was fixed at the steady state position",
}


def _load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported file type: {path}")


def _read_normal_file(raw_dir: Path, preprocessed_dir: Path, file_stem: str) -> pd.DataFrame:
    raw_xlsx = raw_dir / f"{file_stem}.xlsx"
    pre_csv = preprocessed_dir / f"{file_stem}.csv"

    if raw_xlsx.exists():
        return _load_table(raw_xlsx)
    if pre_csv.exists():
        return _load_table(pre_csv)

    raise FileNotFoundError(f"Missing normal file: {raw_xlsx} or {pre_csv}")


def _read_fault_file(raw_dir: Path, preprocessed_dir: Path, fault_id: int, batch_id: int) -> pd.DataFrame:
    filename = f"mode1_{fault_id}_{batch_id}"
    raw_xlsx = raw_dir / "faults" / f"{filename}.xlsx"
    pre_csv = preprocessed_dir / "faults" / f"{filename}.csv"

    if raw_xlsx.exists():
        return _load_table(raw_xlsx)
    if pre_csv.exists():
        return _load_table(pre_csv)

    raise FileNotFoundError(f"Missing fault file: {raw_xlsx} or {pre_csv}")


def _add_metadata(
    df: pd.DataFrame,
    *,
    type_fault: str,
    n_type_fault: int,
    batch_number: int,
    batch_name: str,
) -> pd.DataFrame:
    out = df.copy()
    out["type_fault"] = type_fault
    out["n_type_fault"] = n_type_fault
    out["batch_number"] = batch_number
    out["batch_name"] = batch_name
    return out


def process_and_save(
    *,
    config_path: Path,
    raw_dir: Path,
    preprocessed_dir: Path,
    processed_dir: Path,
    strict: bool,
) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)

    column_map = load_column_name_map(config_path)

    # Normal operation files
    normal_50 = _read_normal_file(raw_dir, preprocessed_dir, "mode1_normal_50")
    normal_500 = _read_normal_file(raw_dir, preprocessed_dir, "mode1_normal_500")

    normal_50 = apply_column_name_map(normal_50, column_map)
    normal_500 = apply_column_name_map(normal_500, column_map)

    normal_50 = _add_metadata(
        normal_50,
        type_fault="normal_operation",
        n_type_fault=0,
        batch_number=0,
        batch_name="normal_operation_50_hours",
    )
    normal_500 = _add_metadata(
        normal_500,
        type_fault="normal_operation",
        n_type_fault=0,
        batch_number=0,
        batch_name="normal_operation_500_hours",
    )

    normal_50_out = processed_dir / "normal_operation_50_hours.parquet"
    normal_500_out = processed_dir / "normal_operation_500_hours.parquet"

    normal_50.to_parquet(normal_50_out, index=False)
    normal_500.to_parquet(normal_500_out, index=False)

    # Fault files consolidated
    fault_frames: list[pd.DataFrame] = []
    missing_files: list[str] = []

    for fault_id in range(1, 22):
        for batch_id in range(1, 6):
            try:
                df = _read_fault_file(raw_dir, preprocessed_dir, fault_id, batch_id)
            except FileNotFoundError as exc:
                missing_files.append(str(exc))
                continue

            df = apply_column_name_map(df, column_map)
            df = _add_metadata(
                df,
                type_fault=FAULT_DESCRIPTIONS[fault_id],
                n_type_fault=fault_id,
                batch_number=batch_id,
                batch_name=f"simulation_{batch_id}",
            )
            fault_frames.append(df)

    if not fault_frames:
        raise RuntimeError("No fault files found to build abnormal_operation parquet.")

    abnormal_df = pd.concat(fault_frames, ignore_index=True)

    abnormal_out = processed_dir / "abnormal_operation_50_hours.parquet"
    abnormal_alias_out = processed_dir / "abdnormal_operation_50_hours.parquet"

    abnormal_df.to_parquet(abnormal_out, index=False)
    # Alias kept to match the user-requested filename variant.
    abnormal_df.to_parquet(abnormal_alias_out, index=False)

    print(f"Saved: {normal_50_out} -> shape={normal_50.shape}")
    print(f"Saved: {normal_500_out} -> shape={normal_500.shape}")
    print(f"Saved: {abnormal_out} -> shape={abnormal_df.shape}")
    print(f"Saved: {abnormal_alias_out} -> shape={abnormal_df.shape}")

    if missing_files:
        print(f"Missing fault files: {len(missing_files)}")
        if strict:
            sample = "\n".join(missing_files[:5])
            raise RuntimeError(f"Strict mode enabled and files are missing. Sample:\n{sample}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consolidate TEP data into parquet files.")
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "config.yaml",
        help="Path to config.yaml with column mapping.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Directory for raw downloaded files.",
    )
    parser.add_argument(
        "--preprocessed-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "preprocessed",
        help="Directory for optional CSV intermediates.",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed",
        help="Directory where parquet outputs are written.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any expected fault file (21 x 5) is missing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    process_and_save(
        config_path=args.config,
        raw_dir=args.raw_dir,
        preprocessed_dir=args.preprocessed_dir,
        processed_dir=args.processed_dir,
        strict=args.strict,
    )


if __name__ == "__main__":
    main()
