import argparse
from pathlib import Path

import joblib
import pandas as pd

from pca_anomaly_detection.data.io import load_tabular, save_csv, select_feature_columns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run anomaly detection with trained PCA model.")
    parser.add_argument("--model", type=Path, required=True, help="Path to trained model (.joblib).")
    parser.add_argument("--input", type=Path, required=True, help="Path to input data file.")
    parser.add_argument("--output", type=Path, required=True, help="Path to output CSV with scores.")
    parser.add_argument(
        "--sep",
        type=str,
        default=None,
        help="Column separator. Default auto-detects whitespace/comma/semicolon.",
    )
    parser.add_argument(
        "--header",
        type=str,
        choices=["none", "infer"],
        default="none",
        help="Whether input file has header row.",
    )
    parser.add_argument("--start-col", type=int, default=0, help="First feature column index.")
    parser.add_argument("--end-col", type=int, default=None, help="Last feature column index (exclusive).")
    parser.add_argument(
        "--drop-col",
        type=int,
        default=None,
        help="Optional absolute column index to drop (e.g., label column).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    detector = joblib.load(args.model)
    header = None if args.header == "none" else "infer"
    input_df_raw = load_tabular(args.input, sep=args.sep, header=header)
    input_df = select_feature_columns(
        input_df_raw,
        start_col=args.start_col,
        end_col=args.end_col,
        drop_col=args.drop_col,
    )

    if input_df.empty:
        raise ValueError("Input data has no valid feature rows after parsing/cleaning.")

    # Enforce same feature naming convention used during training.
    input_df.columns = [f"x_{i:03d}" for i in range(input_df.shape[1])]
    scores_df = detector.score_samples(input_df)
    output_df = pd.concat([input_df.reset_index(drop=True), scores_df.reset_index(drop=True)], axis=1)

    save_csv(output_df, args.output)
    print(f"Scores saved to: {args.output}")


if __name__ == "__main__":
    main()
