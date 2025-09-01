from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd
from pathlib import Path
from src.data.loaders import load_classification_breast_cancer, load_regression_synthetic
from src.features.pipelines import build_leakage_safe_preprocessor
from src.tuning.optuna_tuner import tune_gbm

def main(cfg_path: str):
    cfg = json.loads(Path(cfg_path).read_text())
    task = cfg.get('task', 'classification')
    family = cfg.get('family', 'lgbm')
    n_trials = int(cfg.get('n_trials', 30))

    if task == 'classification':
        X, y = load_classification_breast_cancer()
    else:
        X, y = load_regression_synthetic()

    pre = build_leakage_safe_preprocessor(X)
    pipe, params = tune_gbm(task=task, X=X, y=y, preprocessor=pre, family=family, n_trials=n_trials)
    print('Best params:', params)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config/optuna_config.json')
    args = parser.parse_args()
    main(args.config)
