from __future__ import annotations

import argparse
import gc
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from pca_anomaly_detection.config import load_column_name_map, load_fault_description_map

SPLIT_FILES = {
    "train": ("TEP_FaultFree_Training.feather", "TEP_Faulty_Training.feather"),
    "test": ("TEP_FaultFree_Testing.feather", "TEP_Faulty_Testing.feather"),
}

OUTPUT_NAMES = {
    "train": "TEP_Training.feather",
    "test": "TEP_Testing.feather",
}


def build_split(
    preprocessed_dir: Path,
    split: str,
    column_map: dict[str, str],
    fault_description_map: dict[int, str],
) -> pa.Table:
    """Build one TEP split as an Arrow Table, avoiding pandas to keep memory low.

    Concatenating and renaming pyarrow Tables only manipulates metadata/chunk
    pointers, never duplicating the underlying column buffers the way
    pandas concat + rename (copy=True by default) does for frames this large.
    """

    fault_free_name, faulty_name = SPLIT_FILES[split]

    fault_free_path = preprocessed_dir / fault_free_name
    faulty_path = preprocessed_dir / faulty_name
    for path in (fault_free_path, faulty_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing preprocessed file: {path}")

    fault_free_table = feather.read_table(fault_free_path)
    faulty_table = feather.read_table(faulty_path)

    # The FaultFree .RData stores faultNumber as double (always 0.0) while
    # Faulty stores it as int32; normalize so the schemas match for concat.
    fault_free_table = fault_free_table.set_column(
        0, "faultNumber", fault_free_table.column("faultNumber").cast(pa.int32())
    )
    faulty_table = faulty_table.set_column(
        0, "faultNumber", faulty_table.column("faultNumber").cast(pa.int32())
    )

    table = pa.concat_tables([fault_free_table, faulty_table])
    del fault_free_table, faulty_table
    gc.collect()

    fault_numbers = table.column("faultNumber").cast(pa.int64())
    keys, descriptions = zip(*fault_description_map.items())
    indices = pc.index_in(fault_numbers, value_set=pa.array(keys, type=pa.int64()))
    fault_description = pc.take(pa.array(descriptions, type=pa.string()), indices)
    table = table.add_column(1, "fault_description", fault_description)

    new_names = [column_map.get(name, name) for name in table.column_names]
    table = table.rename_columns(new_names)
    return table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Concat FaultFree+Faulty feather files and rename xmeas_/xmv_ columns per Downs & Vogel (1993)."
    )
    parser.add_argument("--split", type=str, choices=["train", "test"], default="train")
    parser.add_argument(
        "--preprocessed-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "preprocessed",
        help="Directory with the per-file feather conversions.",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed",
        help="Directory where the combined+mapped feather output is written.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "config.yaml",
        help="Path to config.yaml (column_name_map / fault_description_map).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    column_map = load_column_name_map(args.config)
    fault_description_map = load_fault_description_map(args.config)

    table = build_split(args.preprocessed_dir, args.split, column_map, fault_description_map)

    args.processed_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.processed_dir / OUTPUT_NAMES[args.split]
    feather.write_feather(table, out_path)

    print(f"Saved: {out_path} -> shape=({table.num_rows}, {table.num_columns})")
    print(f"Columns: {table.column_names}")


if __name__ == "__main__":
    main()
