from __future__ import annotations
import numpy as np
from scipy.optimize import minimize

def _logit(p, eps=1e-12):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p) - np.log(1 - p)

class TemperatureScaler:
    """Binary temperature scaling on logits from probabilities."""
    def __init__(self):
        self.T_ = 1.0

    def fit(self, y_true, prob):
        z = _logit(prob)
        def nll(logT):
            T = np.exp(logT)
            p = 1.0 / (1.0 + np.exp(-z / T))
            p = np.clip(p, 1e-12, 1 - 1e-12)
            return -np.mean(y_true * np.log(p) + (1 - y_true) * np.log(1 - p))
        res = minimize(nll, x0=np.array([0.0]), method="L-BFGS-B")
        self.T_ = float(np.exp(res.x[0]))
        return self

    def transform(self, prob):
        z = _logit(prob)
        p = 1.0 / (1.0 + np.exp(-z / self.T_))
        return np.clip(p, 1e-12, 1 - 1e-12)

    def fit_transform(self, y_true, prob):
        self.fit(y_true, prob)
        return self.transform(prob)
