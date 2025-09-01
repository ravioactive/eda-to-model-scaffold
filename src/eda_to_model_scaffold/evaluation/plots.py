from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay, DetCurveDisplay
from sklearn.calibration import calibration_curve

def plot_roc_pr(y_true, y_proba, ax_roc=None, ax_pr=None):
    if ax_roc is None:
        fig1, ax_roc = plt.subplots()
    RocCurveDisplay.from_predictions(y_true, y_proba, ax=ax_roc)
    ax_roc.set_title("ROC Curve")
    if ax_pr is None:
        fig2, ax_pr = plt.subplots()
    PrecisionRecallDisplay.from_predictions(y_true, y_proba, ax=ax_pr)
    ax_pr.set_title("Precision-Recall Curve")

def plot_calibration(y_true, y_proba, n_bins: int = 10):
    prob_true, prob_pred = calibration_curve(y_true, y_proba, n_bins=n_bins, strategy="quantile")
    plt.figure()
    plt.plot(prob_pred, prob_true, marker="o")
    plt.plot([0,1],[0,1], linestyle="--")
    plt.xlabel("Mean predicted probability")
    plt.ylabel("Fraction of positives")
    plt.title("Calibration Curve")
    plt.tight_layout()

def plot_residuals(y_true, y_pred):
    resid = y_true - y_pred
    plt.figure()
    plt.scatter(y_pred, resid, s=10, alpha=0.6)
    plt.axhline(0, linestyle="--")
    plt.xlabel("Fitted")
    plt.ylabel("Residuals")
    plt.title("Residuals vs Fitted")
    plt.tight_layout()
