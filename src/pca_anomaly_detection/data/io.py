from pathlib import Path

import pandas as pd


def load_csv(path: str | Path, index_col: int | None = None) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""

    return pd.read_csv(path, index_col=index_col)


def load_tabular(
    path: str | Path,
    *,
    sep: str | None = None,
    header: int | None = None,
    decimal: str = ".",
) -> pd.DataFrame:
    """Load a tabular file handling Tennessee Eastman-style delimiters.

    When ``sep`` is omitted, a regex delimiter supports whitespace, comma, or semicolon.
    """

    if sep is None:
        return pd.read_csv(path, sep=r"[\s,;]+", engine="python", header=header, decimal=decimal)
    return pd.read_csv(path, sep=sep, header=header, decimal=decimal)


def select_feature_columns(
    df: pd.DataFrame,
    *,
    start_col: int = 0,
    end_col: int | None = None,
    drop_col: int | None = None,
) -> pd.DataFrame:
    """Slice feature columns and optionally drop one column (e.g., label)."""

    features = df.iloc[:, start_col:end_col].copy()
    if drop_col is not None and 0 <= drop_col < df.shape[1]:
        original_col = df.columns[drop_col]
        if original_col in features.columns:
            features = features.drop(columns=[original_col])

    return features.apply(pd.to_numeric, errors="coerce").dropna(axis=0).reset_index(drop=True)


def save_csv(df: pd.DataFrame, path: str | Path) -> None:
    """Save DataFrame to CSV, creating parent folders when needed."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
