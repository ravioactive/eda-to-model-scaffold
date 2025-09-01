from __future__ import annotations
from typing import Dict, Any
import numpy as np

from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    r2_score, mean_absolute_error, mean_squared_error
)

def classification_metrics(y_true, y_proba, y_pred=None) -> Dict[str, float]:
    out = {}
    if y_proba is not None:
        out['roc_auc'] = roc_auc_score(y_true, y_proba)
        out['pr_auc'] = average_precision_score(y_true, y_proba)
        out['brier'] = brier_score_loss(y_true, y_proba)
    if y_pred is not None:
        # threshold-specific metrics could be added here
        pass
    return out

def regression_metrics(y_true, y_pred) -> Dict[str, float]:
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return {
        "rmse": rmse,
        "mae": mean_absolute_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }
