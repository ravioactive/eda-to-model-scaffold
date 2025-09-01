from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from src.models.gbm import lgbm_regressor, xgb_regressor
from src.models.baselines import ridge_regressor

def timeseries_cv_evaluate(X: pd.DataFrame, y: pd.Series, model, n_splits: int = 5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    rmses = []
    for tr, va in tscv.split(X):
        X_tr, X_va = X.iloc[tr], X.iloc[va]
        y_tr, y_va = y.iloc[tr], y.iloc[va]
        # basic preprocessor: impute+scale numeric, one-hot cyclical
        num_cols = [c for c in X.columns if X[c].dtype != 'object']
        cat_cols = [c for c in X.columns if X[c].dtype == 'object']
        pre = ColumnTransformer([
            ('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), num_cols),
            ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')), ('ohe', OneHotEncoder(handle_unknown='ignore'))]), cat_cols)
        ])
        pipe = Pipeline([('prep', pre), ('model', model)])
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_va)
        rmse = np.sqrt(mean_squared_error(y_va, y_pred))
        rmses.append(rmse)
    return float(np.mean(rmses))
