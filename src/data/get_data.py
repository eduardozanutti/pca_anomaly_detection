from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

import pandas as pd

BASE_URL = "https://github.com/mv-per/tennessee-eastman-dataset/raw/main/simulations/mode_1"

# Curated subset for quick experiments and initial EDA.
EASY_FAULTS = [1, 2, 6]
MEDIUM_FAULTS = [10, 14]
HARD_FAULTS = [18]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        destination.write_bytes(response.read())


def convert_xlsx_to_csv(xlsx_path: Path, csv_path: Path) -> None:
    df = pd.read_excel(xlsx_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)


def build_quick_file_list() -> list[str]:
    return [
        "mode1_normal_50.xlsx",
        "mode1_normal_500.xlsx",
        "faults/mode1_1_1.xlsx",
    ]


def build_eda_file_list() -> list[str]:
    files = ["mode1_normal_50.xlsx", "mode1_normal_500.xlsx"]
    selected_faults = EASY_FAULTS + MEDIUM_FAULTS + HARD_FAULTS
    for fault_id in selected_faults:
        files.append(f"faults/mode1_{fault_id}_1.xlsx")
    return files


def build_all_faults_file_list() -> list[str]:
    files = ["mode1_normal_50.xlsx", "mode1_normal_500.xlsx"]
    for fault_id in range(1, 22):
        for batch_id in range(1, 6):
            files.append(f"faults/mode1_{fault_id}_{batch_id}.xlsx")
    return files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Tennessee Eastman dataset files.")
    parser.add_argument(
        "--profile",
        type=str,
        choices=["quick", "eda", "all"],
        default="quick",
        help="quick: normals (50h, 500h) + fault 1; eda: normals + mixed easy/medium/hard set; all: normals + all 21 faults x 5 batches.",
    )
    parser.add_argument(
        "--to-csv",
        action="store_true",
        help="Also convert downloaded .xlsx files to .csv in data/preprocessed/.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=project_root() / "data" / "raw",
        help="Output directory for downloaded raw files.",
    )
    parser.add_argument(
        "--preprocessed-dir",
        type=Path,
        default=project_root() / "data" / "preprocessed",
        help="Output directory for converted CSV files.",
    )
    return parser.parse_args()


def select_file_list(profile: str) -> list[str]:
    if profile == "quick":
        return build_quick_file_list()
    if profile == "eda":
        return build_eda_file_list()
    return build_all_faults_file_list()


def main() -> None:
    args = parse_args()
    file_list = select_file_list(args.profile)

    print(f"Profile: {args.profile}")
    print(f"Downloading {len(file_list)} file(s) from Tennessee Eastman public repository...")
    print(f"Raw output directory: {args.raw_dir}")
    if args.to_csv:
        print(f"Preprocessed output directory: {args.preprocessed_dir}")

    downloaded = 0
    for relative_path in file_list:
        source_url = f"{BASE_URL}/{relative_path}"
        destination = args.raw_dir / relative_path

        try:
            download_file(source_url, destination)
            downloaded += 1
            print(f"[OK] {relative_path}")
        except Exception as exc:
            print(f"[FAIL] {relative_path}: {exc}")
            continue

        if args.to_csv:
            csv_relative = Path(relative_path).with_suffix(".csv")
            csv_destination = args.preprocessed_dir / csv_relative
            try:
                convert_xlsx_to_csv(destination, csv_destination)
                print(f"[CSV] {csv_relative}")
            except Exception as exc:
                print(f"[CSV-FAIL] {csv_relative}: {exc}")

    print(f"Finished. Downloaded {downloaded}/{len(file_list)} file(s).")


if __name__ == "__main__":
    main()
