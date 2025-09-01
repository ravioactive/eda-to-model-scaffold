from __future__ import annotations
import argparse, json, warnings
import numpy as np
import pandas as pd
from pathlib import Path
import os
import json
import datetime

from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score

from src.data.loaders import load_classification_breast_cancer, load_regression_synthetic, split_data
from src.features.pipelines import build_leakage_safe_preprocessor
from src.models.baselines import ridge_regressor, elasticnet_regressor, robust_huber_regressor, penalized_logistic, log1p_wrapper
from src.models.gbm import xgb_regressor, xgb_classifier, lgbm_regressor, lgbm_classifier
from src.evaluation.metrics import classification_metrics, regression_metrics

def _append_compare_result(payload: dict, out_dir: str = "results"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "compare.json")
    try:
        existing = json.loads(open(path).read())
        if not isinstance(existing, list):
            existing = [existing]
    except Exception:
        existing = []
    existing.append(payload)
    with open(path, "w") as f:
        json.dump(existing, f, indent=2)


def main(cfg_path: str):
    cfg = json.loads(Path(cfg_path).read_text())
    task = cfg.get("task", "classification")
    random_state = cfg.get("random_state", 42)

    # Load data
    if task == "classification":
        X, y = load_classification_breast_cancer()
    else:
        X, y = load_regression_synthetic()

    # Split
    data = split_data(X, y, task=task, random_state=random_state)

    # Preprocessor
    pre = build_leakage_safe_preprocessor(data.X_train)

    # Baseline
    if task == "classification":
        base = penalized_logistic(random_state=random_state)
    else:
        base = ridge_regressor(random_state=random_state)

    base_pipe = Pipeline([("prep", pre), ("model", base)])
    base_pipe.fit(data.X_train, data.y_train)

    # Evaluate baseline
    if task == "classification":
        y_proba = base_pipe.predict_proba(data.X_valid)[:,1]
        base_scores = classification_metrics(data.y_valid, y_proba)
    else:
        y_pred = base_pipe.predict(data.X_valid)
        base_scores = regression_metrics(data.y_valid, y_pred)

    print("Baseline valid scores:", base_scores)

    # Candidate GBM
    best_pipe = base_pipe
    best_score = base_scores['roc_auc'] if task == "classification" else -base_scores['rmse']

    if task == "classification":
        # Try LightGBM then XGBoost
        gbm = lgbm_classifier(random_state=random_state) or xgb_classifier(random_state=random_state)
        if gbm is not None:
            gbm_pipe = Pipeline([("prep", pre), ("model", gbm)])
            gbm_pipe.fit(data.X_train, data.y_train)
            y_proba = gbm_pipe.predict_proba(data.X_valid)[:,1]
            gbm_scores = classification_metrics(data.y_valid, y_proba)
            print("GBM valid scores:", gbm_scores)
            if gbm_scores['roc_auc'] > (best_score if isinstance(best_score, float) else 0):
                best_pipe = gbm_pipe
                best_score = gbm_scores['roc_auc']
    else:
        gbm = lgbm_regressor(random_state=random_state) or xgb_regressor(random_state=random_state)
        if gbm is not None:
            gbm_pipe = Pipeline([("prep", pre), ("model", gbm)])
            gbm_pipe.fit(data.X_train, data.y_train)
            y_pred = gbm_pipe.predict(data.X_valid)
            import numpy as np
            from src.evaluation.metrics import regression_metrics
            gbm_scores = regression_metrics(data.y_valid, y_pred)
            print("GBM valid scores:", gbm_scores)
            if -gbm_scores['rmse'] > best_score:
                best_pipe = gbm_pipe
                best_score = -gbm_scores['rmse']

    # Calibration (classification only, optional)
    if task == "classification" and cfg.get("calibrate_probabilities", True):
        try:
            calib = CalibratedClassifierCV(best_pipe, method="isotonic", cv=5)
            calib.fit(data.X_train, data.y_train)
            y_proba = calib.predict_proba(data.X_test)[:,1]
            print("Test ROC-AUC (calibrated):", roc_auc_score(data.y_test, y_proba))
            # Write compare.json entry (classification, calibrated)
            from sklearn.metrics import average_precision_score, brier_score_loss
            test_report = {
                "roc_auc": float(roc_auc_score(data.y_test, y_proba)),
                "pr_auc": float(average_precision_score(data.y_test, y_proba)),
                "brier": float(brier_score_loss(data.y_test, y_proba)),
                "calibrated": True
            }
            payload = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "config": cfg_path,
                "task": task,
                "model": best_pipe.__class__.__name__,
                "tuned": bool(cfg.get("tuning", {}).get("enabled", False)),
                "monotone": bool(monotone_vec is not None),
                "valid_baseline": base_scores,
                "valid_gbm": gbm_scores,
                "test": test_report
            }
            _append_compare_result(payload)

        except Exception as e:
            warnings.warn(f"Calibration failed: {e}")
            best_pipe.fit(data.X_train, data.y_train)
            y_proba = best_pipe.predict_proba(data.X_test)[:,1]
            print("Test ROC-AUC (uncalibrated):", roc_auc_score(data.y_test, y_proba))
        from sklearn.metrics import average_precision_score, brier_score_loss
        test_report = {
            "roc_auc": float(roc_auc_score(data.y_test, y_proba)),
            "pr_auc": float(average_precision_score(data.y_test, y_proba)),
            "brier": float(brier_score_loss(data.y_test, y_proba)),
            "calibrated": False
"
        }
        payload = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "config": cfg_path,
            "task": task,
            "model": best_pipe.__class__.__name__,
            "tuned": bool(cfg.get("tuning", {}).get("enabled", False)),
            "monotone": bool(monotone_vec is not None),
            "valid_baseline": base_scores,
            "valid_gbm": gbm_scores,
            "test": test_report
        }
        _append_compare_result(payload)

    else:
        # Final fit and test evaluation
        best_pipe.fit(pd.concat([data.X_train, data.X_valid]), pd.concat([data.y_train, data.y_valid]))
        if task == "classification":
            from sklearn.metrics import roc_auc_score
            y_proba = best_pipe.predict_proba(data.X_test)[:,1]
            print("Test ROC-AUC:", roc_auc_score(data.y_test, y_proba))
        else:
            y_pred = best_pipe.predict(data.X_test)
            from src.evaluation.metrics import regression_metrics
            print("Test scores:", regression_metrics(data.y_test, y_pred))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config/example_config.json")
    args = parser.parse_args()
    main(args.config)
