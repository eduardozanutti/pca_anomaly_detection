from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

# Rieth, C. A., Amsel, B. D., Tran, R., & Cook, M. B. (2017).
# "Additional Tennessee Eastman Process Simulation Data for Anomaly Detection Evaluation."
# Harvard Dataverse, doi:10.7910/DVN/6C3JR1
DATAVERSE_ACCESS_URL = "https://dataverse.harvard.edu/api/access/datafile/{file_id}"

# file_id confirmed via the Dataverse API file listing for the dataset above.
DATAVERSE_FILES: dict[str, int] = {
    "TEP_FaultFree_Training.RData": 3031241,
    "TEP_Faulty_Training.RData": 3031242,
    "TEP_FaultFree_Testing.RData": 3031240,
    "TEP_Faulty_Testing.RData": 3031243,
}

TRAIN_FILES = ["TEP_FaultFree_Training.RData", "TEP_Faulty_Training.RData"]
TEST_FILES = ["TEP_FaultFree_Testing.RData", "TEP_Faulty_Testing.RData"]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def download_file(file_id: int, destination: Path, *, chunk_size: int = 1 << 20) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    url = DATAVERSE_ACCESS_URL.format(file_id=file_id)
    # Dataverse's S3 redirect rejects the default Python-urllib User-Agent (403).
    request = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})

    with urllib.request.urlopen(request) as response:
        total = response.length or 0
        downloaded = 0
        with destination.open("wb") as f:
            while chunk := response.read(chunk_size):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  {destination.name}: {downloaded / 1e6:.1f}/{total / 1e6:.1f} MB ({pct:.0f}%)", end="")
    print()


def select_file_list(split: str) -> list[str]:
    if split == "train":
        return TRAIN_FILES
    if split == "test":
        return TEST_FILES
    return TRAIN_FILES + TEST_FILES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the Rieth et al. (2017) Tennessee Eastman RData files from Harvard Dataverse."
    )
    parser.add_argument(
        "--split",
        type=str,
        choices=["train", "test", "all"],
        default="all",
        help="train: FaultFree+Faulty training; test: FaultFree+Faulty testing; all: both splits.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=project_root() / "data" / "raw",
        help="Output directory for downloaded .RData files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if the destination file already exists.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    file_list = select_file_list(args.split)

    print(f"Split: {args.split}")
    print(f"Raw output directory: {args.raw_dir}")

    downloaded = 0
    for filename in file_list:
        destination = args.raw_dir / filename
        if destination.exists() and not args.force:
            print(f"[SKIP] {filename} (already exists)")
            continue

        try:
            download_file(DATAVERSE_FILES[filename], destination)
            downloaded += 1
            print(f"[OK] {filename}")
        except Exception as exc:
            print(f"[FAIL] {filename}: {exc}")

    print(f"Finished. Downloaded {downloaded}/{len(file_list)} file(s).")


if __name__ == "__main__":
    main()
