import numpy as np


def detection_rate(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute true positive rate for anomaly class (1)."""

    positives = y_true == 1
    if positives.sum() == 0:
        return 0.0
    return float(((y_pred == 1) & positives).sum() / positives.sum())


def false_alarm_rate(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute false alarm rate over normal class (0)."""

    negatives = y_true == 0
    if negatives.sum() == 0:
        return 0.0
    return float(((y_pred == 1) & negatives).sum() / negatives.sum())


def first_detection_delay(y_true: np.ndarray, y_pred: np.ndarray) -> int | None:
    """Return delay between first true anomaly and first detected anomaly."""

    true_idx = np.where(y_true == 1)[0]
    pred_idx = np.where(y_pred == 1)[0]

    if len(true_idx) == 0 or len(pred_idx) == 0:
        return None

    first_true = int(true_idx[0])
    future_preds = pred_idx[pred_idx >= first_true]
    if len(future_preds) == 0:
        return None

    return int(future_preds[0] - first_true)
