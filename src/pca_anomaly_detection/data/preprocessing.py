import pandas as pd
from sklearn.preprocessing import StandardScaler


class TabularStandardizer:
    """Wrapper around StandardScaler preserving DataFrame metadata."""

    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self.columns: list[str] | None = None

    def fit(self, df: pd.DataFrame) -> "TabularStandardizer":
        self.columns = df.columns.tolist()
        self.scaler.fit(df.values)
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.columns is None:
            raise RuntimeError("Scaler must be fitted before transform.")

        transformed = self.scaler.transform(df[self.columns].values)
        return pd.DataFrame(transformed, columns=self.columns, index=df.index)

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)
