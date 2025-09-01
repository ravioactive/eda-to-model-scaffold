from __future__ import annotations
from typing import Dict, Any, Tuple, Optional
import numpy as np
import optuna

from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.metrics import roc_auc_score, average_precision_score, mean_squared_error
from sklearn.pipeline import Pipeline

# Optional GBMs
try:
    from lightgbm import LGBMClassifier, LGBMRegressor
except Exception:
    LGBMClassifier = LGBMRegressor = None

try:
    from xgboost import XGBClassifier, XGBRegressor
except Exception:
    XGBClassifier = XGBRegressor = None

def _cv_task(task: str):
    return StratifiedKFold if task == "classification" else KFold

def _metric(task: str, prefer_pr_auc: bool = True):
    if task == "classification":
        if prefer_pr_auc:
            return lambda yt, yp: average_precision_score(yt, yp)  # higher is better
        return lambda yt, yp: roc_auc_score(yt, yp)
    else:
        return lambda yt, yhat: -np.sqrt(mean_squared_error(yt, yhat))  # maximize negative RMSE

def _make_model(trial: optuna.Trial, family: str, task: str, monotone_vector=None):
    if family == "lgbm":
        if task == "classification":
            assert LGBMClassifier is not None, "LightGBM not installed"
            return LGBMClassifier(
                n_estimators=trial.suggest_int("n_estimators", 200, 2000),
                learning_rate=trial.suggest_float("learning_rate", 1e-3, 0.2, log=True),
                num_leaves=trial.suggest_int("num_leaves", 15, 127),
                min_data_in_leaf=trial.suggest_int("min_data_in_leaf", 10, 200),
                feature_fraction=trial.suggest_float("feature_fraction", 0.6, 1.0),
                bagging_fraction=trial.suggest_float("bagging_fraction", 0.6, 1.0),
                bagging_freq=1,
                class_weight="balanced",
                random_state=42,
                monotone_constraints=monotone_vector if monotone_vector is not None else None
                monotone_constraints=monotone_vector if monotone_vector is not None else None
                monotone_constraints=monotone_vector if monotone_vector is not None else None
            )
        else:
            assert LGBMRegressor is not None, "LightGBM not installed"
            return LGBMRegressor(
                n_estimators=trial.suggest_int("n_estimators", 200, 2000),
                learning_rate=trial.suggest_float("learning_rate", 1e-3, 0.2, log=True),
                num_leaves=trial.suggest_int("num_leaves", 15, 127),
                min_data_in_leaf=trial.suggest_int("min_data_in_leaf", 10, 200),
                feature_fraction=trial.suggest_float("feature_fraction", 0.6, 1.0),
                bagging_fraction=trial.suggest_float("bagging_fraction", 0.6, 1.0),
                bagging_freq=1,
                random_state=42,
                monotone_constraints=monotone_vector if monotone_vector is not None else None
                monotone_constraints=monotone_vector if monotone_vector is not None else None
                monotone_constraints=monotone_vector if monotone_vector is not None else None
            )
    elif family == "xgb":
        if task == "classification":
            assert XGBClassifier is not None, "XGBoost not installed"
            return XGBClassifier(
                n_estimators=trial.suggest_int("n_estimators", 200, 3000),
                learning_rate=trial.suggest_float("learning_rate", 1e-3, 0.2, log=True),
                max_depth=trial.suggest_int("max_depth", 3, 10),
                min_child_weight=trial.suggest_int("min_child_weight", 1, 20),
                subsample=trial.suggest_float("subsample", 0.6, 1.0),
                colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
                reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
                reg_alpha=trial.suggest_float("reg_alpha", 1e-6, 1.0, log=True),
                tree_method="hist",
                eval_metric="aucpr",
                random_state=42,
                monotone_constraints=monotone_vector if monotone_vector is not None else None
                monotone_constraints=monotone_vector if monotone_vector is not None else None
            )
        else:
            assert XGBRegressor is not None, "XGBoost not installed"
            return XGBRegressor(
                n_estimators=trial.suggest_int("n_estimators", 200, 3000),
                learning_rate=trial.suggest_float("learning_rate", 1e-3, 0.2, log=True),
                max_depth=trial.suggest_int("max_depth", 3, 10),
                min_child_weight=trial.suggest_int("min_child_weight", 1, 20),
                subsample=trial.suggest_float("subsample", 0.6, 1.0),
                colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
                reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
                reg_alpha=trial.suggest_float("reg_alpha", 1e-6, 1.0, log=True),
                tree_method="hist",
                random_state=42,
                monotone_constraints=monotone_vector if monotone_vector is not None else None
                monotone_constraints=monotone_vector if monotone_vector is not None else None
            )
    else:
        raise ValueError("Unknown family: " + family)

def tune_gbm(
    task: str, X, y, preprocessor, family: str = "lgbm",
    n_trials: int = 30, prefer_pr_auc: bool = True, random_state: int = 42,
    monotone_vector: Optional[list] = None
) -> Tuple[Pipeline, Dict[str, Any]]:
    """Tune a GBM with Optuna inside a Pipeline. Returns best pipeline and params."""
    CV = _cv_task(task)
    scorer = _metric(task, prefer_pr_auc=prefer_pr_auc)

    def objective(trial: optuna.Trial):
        model = _make_model(trial, family=family, task=task, monotone_vector=monotone_vector)
        # Manual CV to get out-of-fold metric; early stopping can be added per fold if desired.
        kf = CV(n_splits=5, shuffle=True, random_state=random_state) if task == "classification" else CV(n_splits=5, shuffle=True, random_state=random_state)
        scores = []
        for tr, va in kf.split(X, y if task == "classification" else X):
            X_tr, X_va = X.iloc[tr], X.iloc[va]
            y_tr, y_va = y.iloc[tr], y.iloc[va]
            pipe = Pipeline([("prep", preprocessor), ("model", model)])
            pipe.fit(X_tr, y_tr)
            if task == "classification":
                proba = pipe.predict_proba(X_va)[:,1]
                s = scorer(y_va, proba)
            else:
                pred = pipe.predict(X_va)
                s = scorer(y_va, pred)
            scores.append(s)
        return float(np.mean(scores))

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    best_params = study.best_trial.params
    best_model = _make_model(optuna.trial.FixedTrial(best_params), family=family, task=task, monotone_vector=monotone_vector)
    best_pipe = Pipeline([("prep", preprocessor), ("model", best_model)])
    best_pipe.fit(X, y)
    return best_pipe, best_params
