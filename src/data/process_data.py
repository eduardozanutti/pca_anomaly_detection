from __future__ import annotations

import argparse
import gc
from pathlib import Path

import pyreadr

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RDATA_FILES = [
    "TEP_FaultFree_Training.RData",
    "TEP_Faulty_Training.RData",
    "TEP_FaultFree_Testing.RData",
    "TEP_Faulty_Testing.RData",
]


def convert_one(rdata_path: Path, out_path: Path) -> tuple[int, int]:
    """Convert a single Rieth et al. .RData file into a .feather file.

    Processes exactly one file per call so memory is bounded by a single
    dataframe; the caller is expected to run this once per OS process
    (e.g. one `python` invocation per file) so the OS reclaims memory
    fully between files instead of relying on in-process garbage collection.
    """

    result = pyreadr.read_r(str(rdata_path))
    if len(result) != 1:
        raise ValueError(f"Expected exactly one object in {rdata_path}, found {len(result)}")

    df = next(iter(result.values()))
    shape = df.shape

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_feather(out_path)

    del df, result
    gc.collect()

    return shape


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert ONE Rieth et al. (2017) Tennessee Eastman .RData file into .feather. "
            "Run this once per file (separate process each time) to keep peak memory low."
        )
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        choices=RDATA_FILES,
        help="Which RData file to convert.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Directory containing the downloaded .RData files.",
    )
    parser.add_argument(
        "--preprocessed-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "preprocessed",
        help="Directory where the .feather output is written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rdata_path = args.raw_dir / args.file
    if not rdata_path.exists():
        raise FileNotFoundError(f"Missing RData file: {rdata_path}")

    out_path = args.preprocessed_dir / Path(args.file).with_suffix(".feather").name

    print(f"Reading: {rdata_path}")
    shape = convert_one(rdata_path, out_path)
    print(f"Saved: {out_path} -> shape={shape}")


if __name__ == "__main__":
    main()
