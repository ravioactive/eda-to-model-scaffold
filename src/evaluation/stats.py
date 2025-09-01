from __future__ import annotations
from typing import Sequence, Tuple
import numpy as np
from math import comb
from scipy import stats

# --- Paired tests on per-fold scores ---
def paired_ttest(a: Sequence[float], b: Sequence[float]) -> Tuple[float, float]:
    a, b = np.asarray(a), np.asarray(b)
    t, p = stats.ttest_rel(a, b)
    return float(t), float(p)

def wilcoxon_signed(a: Sequence[float], b: Sequence[float]) -> Tuple[float, float]:
    a, b = np.asarray(a), np.asarray(b)
    w, p = stats.wilcoxon(a, b, zero_method='wilcox', correction=True, alternative='two-sided', mode='auto')
    return float(w), float(p)

# --- DeLong test for ROC-AUC difference (binary classification) ---
# Based on Sun & Xu (2014) vectorized implementation; simplified for binary labels
def _compute_midrank(x):
    J = np.argsort(x)
    Z = x[J]
    N = len(x)
    T = np.zeros(N, dtype=float)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = 0.5 * (i + j - 1) + 1
        i = j
    T2 = np.empty(N, dtype=float)
    T2[J] = T
    return T2

def _fast_delong(predictions_sorted_transposed, label_1_count):
    m = label_1_count
    n = predictions_sorted_transposed.shape[1] - m
    positive_examples = predictions_sorted_transposed[:, :m]
    negative_examples = predictions_sorted_transposed[:, m:]
    k = predictions_sorted_transposed.shape[0]
    aucs = np.zeros(k, dtype=float)
    v01 = np.zeros((k, m), dtype=float)
    v10 = np.zeros((k, n), dtype=float)
    for r in range(k):
        pos = positive_examples[r]
        neg = negative_examples[r]
        all_scores = np.concatenate((pos, neg))
        tx = _compute_midrank(all_scores)
        tx_pos = tx[:m]
        tx_neg = tx[m:]
        aucs[r] = (tx_pos.mean() - tx_neg.mean()) / (m * n) * (m * n) + 0.5
        v01[r, :] = (tx_pos - (m + 1) / 2.0) / n
        v10[r, :] = (tx_neg - (n + 1) / 2.0) / m
    sx = np.cov(v01)
    sy = np.cov(v10)
    delongcov = sx / m + sy / n
    return aucs, delongcov

def delong_roc_variance(y_true, y_scores):
    y_true = np.asarray(y_true)
    y_scores = np.asarray(y_scores)[np.newaxis, :]
    order = np.argsort(-y_scores[0])
    y_scores = y_scores[:, order]
    y_true = y_true[order]
    label_1_count = int(np.sum(y_true))
    aucs, delongcov = _fast_delong(y_scores, label_1_count)
    return aucs[0], delongcov[0, 0]

def delong_roc_test(y_true, y_scores_a, y_scores_b):
    auc_a, var_a = delong_roc_variance(y_true, y_scores_a)
    auc_b, var_b = delong_roc_variance(y_true, y_scores_b)
    se = np.sqrt(var_a + var_b)
    z = (auc_a - auc_b) / se if se > 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(z), float(p), float(auc_a), float(auc_b)
