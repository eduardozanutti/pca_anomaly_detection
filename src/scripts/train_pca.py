import argparse
from pathlib import Path

import joblib

from pca_anomaly_detection.data.io import load_tabular, select_feature_columns
from pca_anomaly_detection.models.pca_detector import PCAAnomalyDetector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train PCA anomaly detector on normal process data.")
    parser.add_argument("--train", type=Path, required=True, help="Path to training data file.")
    parser.add_argument("--model-out", type=Path, required=True, help="Path to save trained model.")
    parser.add_argument("--n-components", type=float, default=0.95, help="PCA components or variance ratio.")
    parser.add_argument("--alpha", type=float, default=0.99, help="Threshold confidence level.")
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

    header = None if args.header == "none" else "infer"
    train_df_raw = load_tabular(args.train, sep=args.sep, header=header)
    train_df = select_feature_columns(
        train_df_raw,
        start_col=args.start_col,
        end_col=args.end_col,
        drop_col=args.drop_col,
    )

    if train_df.empty:
        raise ValueError("Training data has no valid feature rows after parsing/cleaning.")

    train_df.columns = [f"x_{i:03d}" for i in range(train_df.shape[1])]

    detector = PCAAnomalyDetector(n_components=args.n_components, alpha=args.alpha)
    detector.fit(train_df)

    args.model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(detector, args.model_out)

    print(f"Model saved to: {args.model_out}")
    print(f"Train shape used: {train_df.shape}")
    print(f"SPE threshold: {detector.thresholds.spe:.6f}")
    print(f"T2 threshold: {detector.thresholds.t2:.6f}")


if __name__ == "__main__":
    main()
