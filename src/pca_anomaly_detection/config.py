from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml


@dataclass(frozen=True)
class ProjectPaths:
    """Centralized project paths for reproducible scripts and notebooks."""

    root: Path = Path(__file__).resolve().parents[2]

    @property
    def data_raw(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def data_processed(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def results_figures(self) -> Path:
        return self.root / "results" / "figures"

    @property
    def reports(self) -> Path:
        return self.root / "reports"


def load_project_config(config_path: str | Path | None = None) -> dict:
    """Load project YAML configuration from the repository root by default."""

    if config_path is None:
        config_path = Path(__file__).resolve().parents[2] / "config.yaml"

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with config_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("YAML config must define a top-level mapping.")
    return data


def load_column_name_map(config_path: str | Path | None = None) -> dict[str, str]:
    """Return column rename mapping from config.yaml (column_name_map section)."""

    config = load_project_config(config_path)
    column_map = config.get("column_name_map", {})
    if not isinstance(column_map, dict):
        raise ValueError("'column_name_map' must be a mapping in config.yaml")
    return {str(k): str(v) for k, v in column_map.items()}


def apply_column_name_map(df: pd.DataFrame, column_map: dict[str, str]) -> pd.DataFrame:
    """Return a DataFrame copy with columns renamed according to mapping."""

    return df.rename(columns=column_map, errors="ignore")
