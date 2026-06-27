from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import chi2
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


@dataclass
class PCAThresholds:
    spe: float
    t2: float


class PCAAnomalyDetector:
    """PCA-based anomaly detector using SPE and Hotelling T2 statistics."""

    def __init__(self, n_components: int | float = 0.95, alpha: float = 0.99) -> None:
        self.n_components = n_components
        self.alpha = alpha
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components)
        self.thresholds: PCAThresholds | None = None
        self.feature_columns: list[str] | None = None

    def fit(self, X_train: pd.DataFrame) -> "PCAAnomalyDetector":
        self.feature_columns = X_train.columns.astype(str).tolist()
        train_values = self.scaler.fit_transform(X_train.values)
        self.pca.fit(train_values)

        train_scores = self.pca.transform(train_values)
        train_recon = self.pca.inverse_transform(train_scores)
        residuals = train_values - train_recon

        spe_train = np.sum(residuals**2, axis=1)
        t2_train = self._hotelling_t2(train_scores)

        # SPE threshold from empirical quantile and T2 from chi-square approximation.
        spe_threshold = float(np.quantile(spe_train, self.alpha))
        t2_threshold = float(chi2.ppf(self.alpha, df=self.pca.n_components_))

        self.thresholds = PCAThresholds(spe=spe_threshold, t2=t2_threshold)
        return self

    def score_samples(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.thresholds is None:
            raise RuntimeError("Detector must be fitted before scoring.")
        if self.feature_columns is None:
            raise RuntimeError("Detector features are missing. Refit the model.")

        expected_cols = self.feature_columns
        current_cols = X.columns.astype(str).tolist()
        if current_cols != expected_cols:
            raise ValueError(
                "Input columns differ from training columns. "
                "Ensure same feature order and names for train/test."
            )

        values = self.scaler.transform(X.values)
        scores = self.pca.transform(values)
        recon = self.pca.inverse_transform(scores)
        residuals = values - recon

        spe = np.sum(residuals**2, axis=1)
        t2 = self._hotelling_t2(scores)

        result = pd.DataFrame(
            {
                "spe": spe,
                "t2": t2,
                "is_anomaly_spe": spe > self.thresholds.spe,
                "is_anomaly_t2": t2 > self.thresholds.t2,
            },
            index=X.index,
        )
        result["is_anomaly_combined"] = result["is_anomaly_spe"] | result["is_anomaly_t2"]
        return result

    def _hotelling_t2(self, scores: np.ndarray) -> np.ndarray:
        explained_variance = self.pca.explained_variance_
        safe_variance = np.where(explained_variance == 0.0, 1e-12, explained_variance)
        return np.sum((scores**2) / safe_variance, axis=1)
