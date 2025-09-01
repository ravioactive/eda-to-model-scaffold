from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.impute import SimpleImputer

def detect_feature_types(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    cat_cols = [c for c in df.columns if df[c].dtype == 'object' or str(df[c].dtype).startswith('category')]
    num_cols = [c for c in df.columns if c not in cat_cols]
    return num_cols, cat_cols

def add_missing_indicators(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    for col in X.columns:
        if X[col].isna().any():
            X[f"{col}__is_missing"] = X[col].isna().astype(int)
    return X

def numeric_pipeline():
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])

def categorical_pipeline(min_frequency: int = 10):
    return Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", min_frequency=min_frequency))
    ])

def build_preprocessor(X: pd.DataFrame, min_frequency: int = 10) -> ColumnTransformer:
    num_cols, cat_cols = detect_feature_types(X)
    return ColumnTransformer([
        ("num", numeric_pipeline(), num_cols),
        ("cat", categorical_pipeline(min_frequency=min_frequency), cat_cols)
    ])

def build_leakage_safe_preprocessor(X: pd.DataFrame) -> Pipeline:
    # Adds missingness flags then applies ColumnTransformer
    pre = Pipeline([
        ("missing_flags", FunctionTransformer(add_missing_indicators)),
        ("ct", build_preprocessor(X))
    ])
    return pre
