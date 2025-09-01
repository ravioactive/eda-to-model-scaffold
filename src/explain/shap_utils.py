from __future__ import annotations
from typing import Optional
import numpy as np
import shap

def pick_explainer(model):
    # Prefer TreeExplainer when possible
    try:
        return shap.TreeExplainer(model)
    except Exception:
        return None

def shap_values(model, X_sample, background_size: int = 200):
    explainer = pick_explainer(model)
    if explainer is not None:
        sv = explainer.shap_values(X_sample)
        return explainer, sv
    # Kernel fallback
    bg = shap.sample(X_sample, background_size, random_state=42) if hasattr(shap, "sample") else X_sample.sample(min(background_size, len(X_sample)), random_state=42)
    explainer = shap.KernelExplainer(model.predict_proba if hasattr(model, "predict_proba") else model.predict, bg)
    sv = explainer.shap_values(X_sample, nsamples="auto")
    return explainer, sv

def plot_summary(model, X_sample, max_display: int = 20):
    explainer, sv = shap_values(model, X_sample)
    shap.summary_plot(sv, X_sample, max_display=max_display)

def plot_dependence(model, X_sample, feature, interaction_index=None):
    explainer, sv = shap_values(model, X_sample)
    shap.dependence_plot(feature, sv, X_sample, interaction_index=interaction_index)
