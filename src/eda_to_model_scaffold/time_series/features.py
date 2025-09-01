from __future__ import annotations
import numpy as np
import pandas as pd

def make_synthetic_series(n: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    trend = 0.05 * t
    season = 2.0 * np.sin(2*np.pi*t/24)
    noise = rng.normal(0, 1.0, size=n)
    y = 10 + trend + season + noise
    df = pd.DataFrame({'y': y}, index=pd.date_range('2020-01-01', periods=n, freq='H'))
    return df

def build_lagged_features(df: pd.DataFrame, target: str = 'y', lags=(1,2,3,6,12,24), rolls=(3,6,12)):
    X = pd.DataFrame(index=df.index)
    for L in lags:
        X[f'lag_{L}'] = df[target].shift(L)
    for R in rolls:
        X[f'rollmean_{R}'] = df[target].rolling(R).mean()
        X[f'rollstd_{R}'] = df[target].rolling(R).std()
    # time features
    X['hour'] = df.index.hour
    X['dayofweek'] = df.index.dayofweek
    y = df[target]
    return X, y
