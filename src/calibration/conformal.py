from __future__ import annotations
import numpy as np

def selective_threshold(y_true, y_proba, alpha: float = 0.1):
    """Calibrate a threshold tau for selective classification (abstain) so that
    the empirical error rate among *predicted* samples is <= alpha on the calibration set.

    Returns tau and summary dict.
    """
    y_true = np.asarray(y_true)
    y_proba = np.asarray(y_proba)
    if y_proba.ndim == 1:
        # binary: y_proba = P(y=1)
        p_max = np.maximum(y_proba, 1 - y_proba)
        y_hat = (y_proba >= 0.5).astype(int)
    else:
        p_max = y_proba.max(axis=1)
        y_hat = y_proba.argmax(axis=1)

    order = np.argsort(-p_max)  # descending confidence
    p_sorted = p_max[order]
    y_hat_sorted = y_hat[order]
    y_true_sorted = y_true[order]

    correct = (y_hat_sorted == y_true_sorted).astype(int)
    cum_n = np.arange(1, len(correct) + 1)
    cum_err = np.cumsum(1 - correct)
    err_rate = cum_err / cum_n

    # Find largest prefix with error rate <= alpha
    valid_ix = np.where(err_rate <= alpha)[0]
    if len(valid_ix) == 0:
        # No threshold satisfies constraint; return tau=1.0 => always abstain
        tau = 1.0
        coverage = 0.0
    else:
        k = valid_ix[-1]
        tau = float(p_sorted[k])
        coverage = float(cum_n[k] / len(correct))
    return tau, {"coverage": coverage, "emp_err": float(err_rate[k]) if len(valid_ix)>0 else None}

def selective_predict(y_proba, tau: float):
    y_proba = np.asarray(y_proba)
    if y_proba.ndim == 1:
        p_max = np.maximum(y_proba, 1 - y_proba)
        pred = (y_proba >= 0.5).astype(int)
    else:
        p_max = y_proba.max(axis=1)
        pred = y_proba.argmax(axis=1)
    abstain = p_max < tau
    pred_with_abstain = pred.copy()
    pred_with_abstain[abstain] = -1  # -1 marks abstention
    return pred_with_abstain, abstain
