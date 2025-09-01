Here’s a compact, EDA-driven one-page checklist with exact starter settings and the order of plots/tests to run. Copy/paste the snippets and adjust minimally.

General setup (both tasks)
	•	Split: train/valid/test (60/20/20), random_state=42, stratify for classification.
	•	Preprocess (sklearn ColumnTransformer)
	•	Num: SimpleImputer(strategy="median"), StandardScaler()
	•	Cat: SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore", min_frequency=10)
	•	Metrics:
	•	Regression: RMSE (select), MAE, R².
	•	Classification: if imbalance > 1:5 → PR-AUC, else ROC-AUC; also Brier + calibration curve.

## General Setup (Both Tasks)

### Data Splitting
- **Split**: train/valid/test (60/20/20), `random_state=42`, stratify for classification

### Preprocessing (sklearn ColumnTransformer)
- **Numerical**: `SimpleImputer(strategy="median")`, `StandardScaler()`
- **Categorical**: `SimpleImputer(strategy="most_frequent")`, `OneHotEncoder(handle_unknown="ignore", min_frequency=10)`

### Metrics
- **Regression**: RMSE (select), MAE, R²
- **Classification**: if imbalance > 1:5 → PR-AUC, else ROC-AUC; also Brier + calibration curve

---

## Regression

### Step 0: Run Baseline + Diagnostics

**Model: Penalized Linear Baseline (Interpretable)**

```python
Ridge(alpha=1.0, random_state=42)
# or ElasticNet(alpha=0.1, l1_ratio=0.3, random_state=42)
# For skewed target (|skew|>1): wrap with TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1)
```

**Plots/Tests (in order):**
1. Target hist + skew/kurtosis (consider log/Yeo–Johnson)
2. Feature corr heatmap (Pearson/Spearman)
3. VIF (flag > 5–10)
4. Fit baseline → residuals vs fitted (non-linearity, heteroscedasticity)
5. QQ-plot (heavy tails)
6. Breusch–Pagan / White test (heteroscedasticity)
7. Quick RF PDP/ICE on top 3 features (interactions/non-linearity hint)

### If EDA Says...

#### A) Non-linearity (curved residuals, PDP non-linear)

**Prefer**: Gradient Boosting (LightGBM/XGBoost), or GAM-like while staying interpretable.

**LightGBM Regressor (tabular default)**
```python
LGBMRegressor(
    n_estimators=1000, learning_rate=0.05,
    num_leaves=31, max_depth=-1,
    min_data_in_leaf=50, feature_fraction=0.8,
    bagging_fraction=0.8, bagging_freq=1,
    lambda_l1=0.0, lambda_l2=0.0, random_state=42
)  # use early_stopping_rounds=50 on a valid set
```

**XGBoost Regressor**
```python
XGBRegressor(
    n_estimators=2000, learning_rate=0.05,
    max_depth=6, min_child_weight=5,
    subsample=0.8, colsample_bytree=0.8,
    reg_alpha=0.0, reg_lambda=1.0, gamma=0.0,
    tree_method="hist", random_state=42
)  # early_stopping_rounds=50, eval_metric="rmse"
```

**Unsuitable**: Unpenalized OLS without transforms.

#### B) Multicollinearity (VIF>10, unstable coefs)

**Prefer**: Ridge/Elastic Net (keep interpretability), or trees (don't care about collinearity).

```python
RidgeCV(alphas=np.logspace(-3,3,13), scoring="neg_root_mean_squared_error", cv=5)
# or ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42)
```

**Unsuitable**: Unpenalized OLS.

#### C) Heteroscedasticity (BP test p<0.05, residual funnel)

**Prefer**: GBMs (variance-robust) or Quantile approaches.
- **LightGBM**: as above; add `objective="quantile"` for intervals (q=0.1/0.5/0.9)
- **Or WLS** in sklearn (`sample_weight≈1/σ²` if known/estimated)

**Unsuitable**: Plain OLS intervals.

#### D) Heavy tails/outliers (QQ-plot, Cook's D)

**Prefer**:
```python
HuberRegressor(epsilon=1.35, alpha=0.0001)  # robust loss
# or use GBMs as above
```

**Unsuitable**: OLS, kNN regressor.

#### E) High-cardinality categoricals / missing values

**Prefer**: LightGBM/XGBoost (native missing, efficient splits). Keep `min_data_in_leaf` (LGBM) or `min_child_weight` (XGB) ≥ moderate values.

**Unsuitable**: Wide OHE linear reg without strong regularization.

#### F) p ≫ n

**Prefer**: Lasso/Elastic Net (sparse, stable).

```python
Lasso(alpha=0.01, max_iter=10000, random_state=42)  # tune alpha on log-grid
```

**Unsuitable**: Deep nets / large GBMs.

---

## Classification

### Step 0: Run Baseline + Diagnostics

**Model: Penalized Logistic (Interpretable)**

```python
LogisticRegression(
    penalty="elasticnet", l1_ratio=0.5,
    solver="saga", C=1.0, max_iter=5000,
    class_weight="balanced", random_state=42
)
```

**Plots/Tests (in order):**
1. Class counts & imbalance ratio
2. Baseline ROC & PR curves (+ AUCs)
3. Calibration curve + Brier score
4. Confusion matrix at F1-optimal threshold
5. UMAP/PCA scatter (non-linear boundary hint)
6. Permutation importance for baseline

### If EDA Says...

#### A) Class imbalance (IR > 1:5)

**Prefer**: Class weights / focal loss (DL) / thresholding; evaluate PR-AUC.

- **Logistic** as above with `class_weight="balanced"`
- **XGBoostClassifier** (set `scale_pos_weight = (neg/pos)`):

```python
XGBClassifier(
    n_estimators=2000, learning_rate=0.05,
    max_depth=6, min_child_weight=5,
    subsample=0.8, colsample_bytree=0.8,
    reg_alpha=0.0, reg_lambda=1.0, gamma=0.0,
    tree_method="hist", scale_pos_weight=IR, random_state=42,
    eval_metric="aucpr"
)  # early_stopping_rounds=50
```

- **LightGBMClassifier**:

```python
LGBMClassifier(
    n_estimators=1000, learning_rate=0.05,
    num_leaves=31, max_depth=-1,
    min_data_in_leaf=50, feature_fraction=0.8,
    bagging_fraction=0.8, bagging_freq=1,
    lambda_l1=0.0, lambda_l2=0.0,
    class_weight="balanced", random_state=42
)
```

**After training: Calibrate if probabilities matter**

```python
CalibratedClassifierCV(base_estimator=gbm, method="isotonic", cv=5)
```

**Unsuitable**: Accuracy-only selection; uncalibrated probabilities.

#### B) Non-linear boundary (logistic underfits, UMAP structure)

**Prefer**: GBMs (above); RBF-SVM (if N moderate); MLPClassifier (large N).

```python
SVC(kernel="rbf", C=1.0, gamma="scale", class_weight="balanced", probability=True, random_state=42)
# or
MLPClassifier(hidden_layer_sizes=(128,64), activation="relu",
              alpha=1e-4, learning_rate_init=1e-3,
              max_iter=200, early_stopping=True, n_iter_no_change=20,
              random_state=42)
```

**Unsuitable**: Plain logistic without engineered terms.

#### C) Multicollinearity / p ≫ n

**Prefer**: Penalized logistic (above) or LinearSVC with regularization.

```python
LinearSVC(C=1.0, class_weight="balanced", random_state=42)  # wrap with CalibratedClassifierCV for probs
```

**Unsuitable**: Unpenalized logistic; high-variance models on tiny N.

#### D) High-cardinality categoricals / missing values

**Prefer**: LightGBM/XGBoost (native missing; efficient with many splits). Consider CV target encoding if sticking to linear/logistic.

**Unsuitable**: Wide OHE logistic without strong regularization.

#### E) Overlapping/noisy classes

**Prefer**: GBM with stronger regularization (increase `min_child_weight`/`min_data_in_leaf`, add `reg_lambda`, reduce `num_leaves`), label smoothing for MLP, or soft-margin SVM.

**Unsuitable**: Unregularized high-variance models.

---

## Cross-Cutting: Learning Curves & Early Stopping

**Plot learning curves (train vs valid):**
- **High bias** → try GBM (deeper trees) / RBF-SVM / add interactions
- **High variance** → increase regularization, reduce tree depth/num_leaves, add subsampling
- **Use** `early_stopping_rounds=50` with a dedicated validation set for LightGBM/XGBoost

---

## Minimal sklearn Pipelines (Drop-in)

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

num_prep = Pipeline([("impute", SimpleImputer(strategy="median")), 
                     ("scale", StandardScaler())])
cat_prep = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                     ("ohe", OneHotEncoder(handle_unknown="ignore", min_frequency=10))])
prep = ColumnTransformer([("num", num_prep, num_cols), ("cat", cat_prep, cat_cols)])

reg_pipe = Pipeline([("prep", prep), ("model", Ridge(alpha=1.0, random_state=42))])
clf_pipe = Pipeline([("prep", prep), ("model", LogisticRegression(penalty="elasticnet",
                                                                 l1_ratio=0.5, solver="saga",
                                                                 C=1.0, max_iter=5000,
                                                                 class_weight="balanced",
                                                                 random_state=42))])
```

---

## Final Pick Rule

Choose the most interpretable model (penalized linear/logistic → GAM-like → calibrated GBM) that meets your metric target (RMSE/MAE or PR-AUC/ROC-AUC). If two models tie, prefer the one with clearer explanations (coefficients, PDP/ICE, SHAP) and stable diagnostics (no residual pathologies, well-calibrated probabilities).