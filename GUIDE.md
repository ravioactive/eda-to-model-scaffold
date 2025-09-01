# EDA-Driven Model Selection Implementation Guide

End-to-end implementation plan that folds in every fix and missing piece we discussed. It keeps your original 3-phase structure but tightens the order of operations, adds leakage-safe practice, expands the tests, and maps EDA findings to interpretable-first model choices with concrete starter settings.

## Table of Contents

- [Phase 0: Data Splitting, Leakage Prevention & Pipeline Setup](#phase-0-data-splitting-leakage-prevention--pipeline-setup)
- [Phase 1: Data Profiling & Statistical Testing](#phase-1-data-profiling--statistical-testing)
- [Phase 2: Pattern → Model Mapping & Baselines](#phase-2-pattern--model-mapping--baselines)
- [Phase 3: Advanced Model Selection, Tuning & Validation](#phase-3-advanced-model-selection-tuning--validation)
- [Quick Model Selection Cheatsheet](#quick-model-selection-cheatsheet)
- [Code Templates & Starter Snippets](#code-templates--starter-snippets)
- [Summary](#summary)

---

## Phase 0: Data Splitting, Leakage Prevention & Pipeline Setup

### Key Principles
- **Split first**: Train/valid/test (e.g., 60/20/20)
- **Classification**: Use `StratifiedKFold` or stratified splits
- **Grouped data**: Use `GroupKFold`
- **Time-ordered data**: Use `TimeSeriesSplit` (no shuffling)
- **Leakage prevention**: Remove/flag post-outcome fields, future timestamps, data-leaking joins/duplicates
- **Pipeline-first**: All preprocessing (imputation, scaling, encoding, target transforms) must live inside `sklearn.Pipeline` or model-native handling to keep CV leakage-safe

---

## Phase 1: Data Profiling & Statistical Testing

### 1. Structure & Completeness
- **Schema inspection**: Check types, ranges, compute missingness patterns (heatmap, per-feature rates)
- **Missing data mechanism**: Run Little's MCAR test if feasible; expect MAR/MNAR in practice
- **Fixes included**: Add missingness indicators during modeling; impute inside pipelines; prefer model-native missing handling (LightGBM/XGBoost) where applicable

### 2. Associations & Collinearity
- **Numeric ↔ Numeric**: Pearson (linear), Spearman (monotonic)
- **Categorical ↔ Categorical**: Cramér's V
- **Categorical ↔ Numeric**: Point-biserial (binary), or Mutual Information (generic, non-linear)
- **VIF (linear models only)**: Compute on one-hot encoded matrix with reference level dropped; VIF is advisory for linear/logistic models, not decisive for trees

### 3. Target Shape & Residual-Relevant Checks

#### Regression
- Check target skew/kurtosis; consider `log1p`/Yeo-Johnson transforms
- Fit quick ridge/elastic-net baseline → inspect residuals vs fitted (linearity, heteroscedasticity), Q-Q of residuals, and RESET test for functional form
- Normality tests on features not required; if testing, do it on residuals (small n only)

#### Classification
- Check class balance
- Run fast penalized logistic baseline to obtain ROC-AUC, PR-AUC, calibration curve/Brier score
- Visualize UMAP/PCA for boundary hints

### 4. Outliers & Influence (Leakage-Safe)
- **Detection**: Robust z-scores, leverage/Cook's D (after baseline), optionally IsolationForest fit only on training fold
- **Handling**: Prefer robust methods (Huber loss, tree-based models), cap/winsorize, or add outlier flags rather than drop. Preserve minority examples

### 5. Interactions & Non-linearity
- Use **ALE** (preferred with correlated features), PDP/ICE, and Friedman's H-statistic from quick RF/GBM to quantify interactions

### 6. Temporal Structure (if applicable)
- **If ordered**: ACF/PACF, Ljung-Box, trend/seasonality plots; use TimeSeriesSplit and time-aware features
- **If not ordered**: Skip Durbin-Watson

---

## Phase 2: Pattern → Model Mapping & Baselines

### 1. Decision Matrix (Expanded Factors)

| **Pattern/Issue** | **Recommended Models** |
|-------------------|------------------------|
| Non-linearity / interactions | GAM/EBM, GBMs, RBF-SVM, MLP (large N) |
| Multicollinearity | Ridge/Elastic-Net, Lasso for sparsity; trees unaffected |
| Heteroscedasticity (regression) | GBM, Quantile Regression/GBM, WLS |
| Heavy tails/outliers | Huber/Theil-Sen, GBM, RANSAC |
| Class imbalance | Weights (`class_weight`, `scale_pos_weight`), PR-AUC focus, calibration |
| p ≫ n | L1/EN (classification/regression), GAM with few terms; avoid high-variance models |
| High-cardinality categoricals | GBMs (splits), target encoding with CV, or embeddings+MLP at large N |
| Monotonic domain knowledge | EBM/GAM or monotone GBM |
| Counts/zero-inflation (regression) | Poisson/NegBin/Tweedie GLMs or Tweedie GBM |
| Grouped/time splits | GroupKFold / TimeSeriesSplit |

### 2. Baselines (Strong & Honest)

#### Dummy Baselines
- `DummyRegressor`/`DummyClassifier` (mean/stratified)

#### Linear Baselines
**Regression:**
```python
Ridge(alpha=1.0, random_state=42)
# or
ElasticNet(alpha=0.1, l1_ratio=0.3)
```

**Classification:**
```python
LogisticRegression(
    penalty="elasticnet", l1_ratio=0.5, solver="saga", 
    C=1.0, max_iter=5000, class_weight="balanced", 
    random_state=42
)
```

**Additional considerations:**
- Add missingness flags
- For skewed regression target, wrap with `TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1)`

### 3. Candidate Families (Interpretable → Performant)

- **EBM/GAM**: Transparent non-linearity (pyGAM/InterpretML)
- **GBMs**: LightGBM/XGBoost; monotonic constraints if needed
- **Robust regressors**: `HuberRegressor(epsilon=1.35, alpha=1e-4)`, `RANSACRegressor`
- **GLMs for counts**: Poisson/NegBin/Tweedie (or Tweedie objective in GBM)
- **RBF-SVM**: Moderate N and MLP (large N / embeddings for high-card cats)
- **Always plan calibration** for classifiers when probabilities matter

### 4. Starter GBM Settings

#### LightGBM
**Regression:**
```python
LGBMRegressor(
    n_estimators=1000, learning_rate=0.05, num_leaves=31,
    min_data_in_leaf=50, feature_fraction=0.8,
    bagging_fraction=0.8, bagging_freq=1, random_state=42
)
```

**Classification:**
```python
LGBMClassifier(
    n_estimators=1000, learning_rate=0.05, num_leaves=31,
    min_data_in_leaf=50, feature_fraction=0.8,
    bagging_fraction=0.8, bagging_freq=1,
    class_weight="balanced", random_state=42
)
```

#### XGBoost
**Regression:**
```python
XGBRegressor(
    n_estimators=2000, learning_rate=0.05, max_depth=6,
    min_child_weight=5, subsample=0.8, colsample_bytree=0.8,
    reg_lambda=1.0, tree_method="hist", random_state=42
)
```

**Classification:**
```python
XGBClassifier(
    n_estimators=2000, learning_rate=0.05, max_depth=6,
    min_child_weight=5, subsample=0.8, colsample_bytree=0.8,
    reg_lambda=1.0, tree_method="hist",
    scale_pos_weight=neg/pos, eval_metric="aucpr",
    random_state=42
)
```

---

## Phase 3: Advanced Model Selection, Tuning & Validation

### 1. Preprocessing Per Model (Do Only What's Needed)

#### Trees/GBMs
- No scaling required
- Rely on native missing handling
- Target/mean encoding for high-cardinality categoricals must be CV-nested

#### Linear/SVM/Neural Networks
- Scale numeric features
- Impute inside pipeline
- Add missingness indicators

**Key principle**: Keep all steps inside `Pipeline`/`ColumnTransformer`

### 2. Cross-Validation Design

- **Classification**: `StratifiedKFold(n_splits=5-10, shuffle=True, random_state=42)`
- **Grouped data**: `GroupKFold`
- **Time series**: `TimeSeriesSplit`
- **Model comparison**: Prefer nested CV for model family comparison, or train/valid with early stopping for GBMs

### 3. Hyperparameter Tuning & Early Stopping

- **Search methods**: `RandomizedSearchCV` / Optuna / Bayesian search
- **GBMs**: Reserve validation fold and set `early_stopping_rounds=50`
- **Domain constraints**: Consider monotonic constraints where domain knowledge dictates
- **Diagnostics**: Log learning curves (train vs valid) to diagnose bias/variance

### 4. Comparative Analysis & Significance

#### Metrics Aligned to Problem
**Regression:**
- Primary: RMSE (for selection)
- Secondary: MAE, R²
- Intervals: Quantile GBM or conformal prediction

**Classification:**
- Primary: PR-AUC (for imbalance), ROC-AUC
- Secondary: Brier score, calibration curves

#### Statistical Tests
- **AUC vs AUC**: DeLong test
- **Per-fold metrics**: Paired t-test or Wilcoxon; use Nadeau-Bengio correction if heavy resampling
- **Forecast errors**: Diebold-Mariano test
- **Avoid routine McNemar** unless binary predictions at fixed threshold are the focal endpoint

### 5. Model Diagnostics

#### Calibration
- If probabilities matter, apply Platt/Isotonic/Temperature scaling (`CalibratedClassifierCV`) after model selection

#### Explainability
- Use **SHAP/ALE** (prefer ALE when features are correlated)
- Check stability across folds

#### Residuals (Regression)
- Check heteroscedasticity patterns, missed non-linearities
- Consider WLS/Quantile regression if needed

#### Thresholding (Classification)
- Choose threshold on validation to optimize F1/cost
- Freeze threshold before test evaluation

### 6. Final Selection & Robustness

#### Model Selection Criteria
- Choose most **interpretable model** that meets metric targets
- If tie, prefer simpler/clearer (coefficients or EBM curves > GBM+SHAP)

#### Final Training & Evaluation
1. **Retrain** on train+valid with tuned parameters
2. **Calibrate** classifiers using proper split (or CV-calibration) without touching test
3. **Evaluate once** on held-out test; report bootstrap CIs for key metrics

#### Robustness Checks
- **Subgroup analysis**: Performance by class/segment/region/time; flag drift-sensitive cohorts
- **Stress tests**: Ablations, small noise perturbations, adversarial missingness
- **Intervals**: 
  - Regression → quantile/conformal prediction
  - Classification → probability calibration and decision curves

### 7. Handoff & Monitoring

#### Documentation Requirements
- **Assumptions**: IID vs time-ordered, monotonic expectations
- **Technical details**: Preprocessing, hyperparameters, metrics, calibration method, threshold
- **Known limitations**: Edge cases, failure modes, data requirements

#### Monitoring Plan
- **Input drift**: Population Stability Index (PSI)
- **Performance drift**: Rolling metrics on new data
- **Calibration drift**: Reliability diagrams over time
- **Data quality**: Missingness pattern changes
- **Operational**: Alerting thresholds, retrain cadence

---

## Quick Model Selection Cheatsheet

### EDA Pattern → Model Choice

| **Pattern** | **Recommended Approach** |
|-------------|--------------------------|
| **Non-linearity / interactions** | Start EBM/GAM → if more lift needed, GBM (LightGBM/XGB); add monotonic constraints if domain requires |
| **Multicollinearity** | Ridge/Elastic-Net (keep interpretability); trees are fine |
| **Heteroscedasticity (regression)** | Quantile GBM or WLS; avoid OLS intervals |
| **Heavy tails/outliers** | HuberRegressor or GBM; avoid OLS/kNN |
| **Class imbalance** | Weights (`class_weight`, `scale_pos_weight`), PR-AUC selection, then calibrate |
| **High-cardinality categoricals** | GBMs or target encoding (CV-safe); for huge N, embeddings+MLP |
| **p ≫ n** | L1/EN (reg/clf) or small GAM; avoid deep nets/large GBMs |
| **Counts/zero-inflation** | Poisson/NegBin/Tweedie GLMs or Tweedie GBM |

---

## Code Templates & Starter Snippets

### Penalized Logistic Regression (Baseline)
```python
LogisticRegression(
    penalty="elasticnet", l1_ratio=0.5, solver="saga", 
    C=1.0, max_iter=5000, class_weight="balanced", 
    random_state=42
)
```

### LightGBM Classification
```python
LGBMClassifier(
    n_estimators=1000, learning_rate=0.05, num_leaves=31,
    min_data_in_leaf=50, feature_fraction=0.8,
    bagging_fraction=0.8, bagging_freq=1,
    lambda_l1=0.0, lambda_l2=0.0,
    class_weight="balanced", random_state=42
)
# Use early_stopping_rounds=50 with a validation fold
```

### XGBoost Regression
```python
XGBRegressor(
    n_estimators=2000, learning_rate=0.05, max_depth=6,
    min_child_weight=5, subsample=0.8, colsample_bytree=0.8,
    reg_lambda=1.0, tree_method="hist", random_state=42
)
# eval_metric="rmse", early_stopping_rounds=50
```

### Robust Regression
```python
HuberRegressor(epsilon=1.35, alpha=1e-4)
```

### SVM (Non-linear Boundary, Moderate N)
```python
SVC(
    kernel="rbf", C=1.0, gamma="scale",
    class_weight="balanced", probability=True, 
    random_state=42
)
```

### Calibration (After Model Selection)
```python
CalibratedClassifierCV(
    base_estimator=best_model, 
    method="isotonic", 
    cv=5
)
```

---

## Summary

This implementation plan is now **coverage-complete** with the following key features:

✅ **Leakage-safe**: Proper data splitting and pipeline design  
✅ **Time/group aware**: Appropriate CV strategies for different data types  
✅ **Statistically sound**: Correct tests for each metric type  
✅ **Interpretability-first**: Prioritizes explainable models with concrete defaults  
✅ **Production-ready**: Includes monitoring and handoff considerations  

The guide provides a systematic approach from EDA insights to model selection with practical code templates and best practices.
