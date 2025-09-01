Awesome—here’s the corrected, end-to-end implementation plan that folds in every fix and missing piece we discussed. It keeps your original 3-phase structure but tightens the order of operations, adds leakage-safe practice, expands the tests, and maps EDA findings to interpretable-first model choices with concrete starter settings.

⸻

Phase 0 (new): Split, leakage checks, and pipelines
	•	Split first: Train/valid/test (e.g., 60/20/20).
	•	Classification → StratifiedKFold/stratified splits.
	•	Grouped data → GroupKFold.
	•	Time-ordered → TimeSeriesSplit (no shuffling).
	•	Leakage scan: Remove/flag post-outcome fields, future timestamps, data-leaking joins/duplicates.
	•	Pipelines everywhere: All preprocessing (imputation, scaling, encoding, target transforms) must live inside sklearn.Pipeline or model-native handling to keep CV leakage-safe.

⸻

Phase 1: Data profiling & statistical testing (corrected)

1. Structure & completeness
	•	Inspect schema, types, ranges; compute missingness patterns (heatmap, per-feature rates).
	•	If feasible, run Little’s MCAR; expect MAR/MNAR in practice.

Fixes included: add missingness indicators during modeling; impute inside pipelines; prefer model-native missing handling (LightGBM/XGBoost) where applicable.

2. Associations & collinearity (numeric + categorical)
	•	Numeric↔numeric: Pearson (linear), Spearman (monotonic).
	•	Cat↔cat: Cramér’s V.
	•	Cat↔num: Point-biserial (binary), or Mutual Information (generic, non-linear).
	•	VIF (for linear design only): compute on the one-hot encoded matrix with a reference level dropped; VIF is advisory for linear/logistic models, not decisive for trees.

3. Target shape & residual-relevant checks
	•	Regression: check target skew/kurtosis; consider log1p/Yeo–Johnson transforms.
	•	Fit a quick ridge/elastic-net baseline → inspect residuals vs fitted (linearity, heteroscedasticity), Q–Q of residuals, and RESET test for functional form.
	•	Normality tests on features are not required; if you must test, do it on residuals (small n only).
	•	Classification: check class balance; run fast penalized logistic baseline to obtain ROC-AUC, PR-AUC, calibration curve/Brier score; visualize UMAP/PCA for boundary hints.

4. Outliers & influence (leakage-safe)
	•	Detect with robust z-scores, leverage/Cook’s D (after baseline), and optionally IsolationForest fit only on the training fold.
	•	Prefer robust handling (Huber loss, tree-based models), cap/winsorize, or add outlier flags rather than drop. Preserve minority examples.

5. Interactions & non-linearity
	•	Use ALE (preferred with correlated features), PDP/ICE, and Friedman’s H-statistic from a quick RF/GBM to quantify interactions.

6. Temporal structure (only if applicable)
	•	If ordered: ACF/PACF, Ljung–Box, trend/seasonality plots; use TimeSeriesSplit and time-aware features.
	•	If not ordered: skip Durbin–Watson.

⸻

Phase 2: Pattern → Model mapping & baselines (corrected)

1. Decision matrix (expanded factors)

Include rows for:
	•	Non-linearity / interactions → GAM/EBM, GBMs, RBF-SVM, MLP (large N).
	•	Multicollinearity → Ridge/Elastic-Net, Lasso for sparsity; trees unaffected.
	•	Heteroscedasticity (regression) → GBM, Quantile Regression/GBM, WLS.
	•	Heavy tails/outliers → Huber/Theil-Sen, GBM, RANSAC.
	•	Class imbalance → weights (class_weight, scale_pos_weight), PR-AUC focus, calibration.
	•	p ≫ n → L1/EN (classification/regression), GAM with few terms; avoid high-variance models.
	•	High-cardinality categoricals → GBMs (splits), target encoding with CV, or embeddings+MLP at large N.
	•	Monotonic domain knowledge → EBM/GAM or monotone GBM.
	•	Counts/zero-inflation (regression) → Poisson/NegBin/Tweedie GLMs or Tweedie GBM.
	•	Grouped/time splits → GroupKFold / TimeSeriesSplit.

2. Baselines (strong & honest)
	•	Dummy baselines: DummyRegressor/Classifier (mean/stratified).
	•	Linear baselines:
	•	Regression: Ridge(alpha=1.0, random_state=42) or ElasticNet(alpha=0.1, l1_ratio=0.3).
	•	Classification: LogisticRegression(penalty="elasticnet", l1_ratio=0.5, solver="saga", C=1.0, max_iter=5000, class_weight="balanced", random_state=42).
	•	Add missingness flags; for skewed regression target, wrap with TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1).

3. Candidate families (interpretable → performant)
	•	EBM/GAM for transparent non-linearity (pyGAM/InterpretML).
	•	GBMs (LightGBM/XGBoost; monotonic constraints if needed).
	•	Robust regressors: HuberRegressor(epsilon=1.35, alpha=1e-4), RANSACRegressor.
	•	GLMs for counts: Poisson/NegBin/Tweedie (or Tweedie objective in GBM).
	•	RBF-SVM (moderate N) and MLP (large N / embeddings for high-card cats).
	•	Always plan calibration for classifiers when probabilities matter.

Starter GBM settings (both tasks, tune later with early stopping):
	•	LightGBM
	•	Regr: LGBMRegressor(n_estimators=1000, learning_rate=0.05, num_leaves=31, min_data_in_leaf=50, feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, random_state=42)
	•	Clf: LGBMClassifier(..., class_weight="balanced")
	•	XGBoost
	•	Regr: XGBRegressor(n_estimators=2000, learning_rate=0.05, max_depth=6, min_child_weight=5, subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0, tree_method="hist", random_state=42)
	•	Clf: XGBClassifier(..., scale_pos_weight = neg/pos, eval_metric="aucpr")

⸻

Phase 3: Advanced model selection, tuning, and validation (corrected)

1. Preprocessing per model (do only what’s needed)
	•	Trees/GBMs: no scaling; rely on native missing handling; target/mean encoding for high-card cats must be CV-nested.
	•	Linear/SVM/NN: scale numeric; impute inside pipeline; add missingness indicators.
	•	Keep all steps inside Pipeline/ColumnTransformer.

2. Cross-validation design
	•	Classification: StratifiedKFold(n_splits=5–10, shuffle=True, random_state=42).
	•	Grouped: GroupKFold.
	•	Time series: TimeSeriesSplit.
	•	Prefer nested CV for model family comparison, or train/valid with early stopping for GBMs.

3. Hyperparameter tuning & early stopping
	•	Use RandomizedSearchCV / Optuna / Bayes search.
	•	GBMs: reserve a validation fold and set early_stopping_rounds=50.
	•	Consider monotonic constraints where domain knowledge dictates.
	•	Log learning curves (train vs valid) to diagnose bias/variance.

4. Comparative analysis & significance
	•	Optimize metrics aligned to the problem:
	•	Regression → RMSE (select), plus MAE, R²; intervals via quantile GBM or conformal.
	•	Classification → PR-AUC for imbalance, ROC-AUC, Brier score and calibration curves.
	•	Statistical tests:
	•	AUC vs AUC → DeLong.
	•	Per-fold metrics → paired t-test or Wilcoxon; use Nadeau–Bengio correction if heavy resampling.
	•	Forecast errors → Diebold–Mariano.
	•	Avoid routine McNemar unless binary predictions at a fixed threshold are the focal endpoint.

5. Model diagnostics (explicit)
	•	Calibration: If probabilities matter, apply Platt/Isotonic/Temperature scaling (CalibratedClassifierCV) after model selection.
	•	Explainability: SHAP/ALE (prefer ALE when features are correlated); check stability across folds.
	•	Residuals (regression): heteroscedasticity patterns, missed non-linearities; consider WLS/Quantile.
	•	Thresholding (classification): choose threshold on validation to optimize F1/cost; freeze it before test.

6. Final selection & robustness
	•	Choose the most interpretable model that meets metric targets. If a tie, prefer simpler/clearer (coefficients or EBM curves > GBM+SHAP).
	•	Retrain on train+valid with tuned params.
	•	For classifiers, calibrate using a proper split (or CV-calibration) without touching test.
	•	Evaluate once on the held-out test; report bootstrap CIs for key metrics.
	•	Subgroup/segment checks: performance by class/segment/region/time; flag drift-sensitive cohorts.
	•	Stress tests: ablations, small noise perturbations, adversarial missingness.
	•	Intervals: regression → quantile/conformal; classification → probability calibration and decision curves.

7. Handoff & monitoring (minimal but essential)
	•	Document: assumptions (IID vs time, monotonic expectations), preprocessing, hyperparameters, metrics, calibration method, threshold, and known limitations.
	•	Monitoring plan: input drift (PSI), performance drift (rolling metrics), calibration drift (reliability), missingness changes; alerting thresholds; retrain cadence.

⸻

Quick model selection cheatsheet (from EDA → choice)
	•	Non-linearity / interactions: Start EBM/GAM → if more lift needed, GBM (LightGBM/XGB); add monotonic constraints if domain requires.
	•	Multicollinearity: Ridge/Elastic-Net (keep interpretability); trees are fine.
	•	Heteroscedasticity (reg): Quantile GBM or WLS; avoid OLS intervals.
	•	Heavy tails/outliers: HuberRegressor or GBM; avoid OLS/kNN.
	•	Imbalance (clf): weights (class_weight, scale_pos_weight), PR-AUC selection, then calibrate.
	•	High-card cats: GBMs or target encoding (CV-safe); for huge N, embeddings+MLP.
	•	p ≫ n: L1/EN (reg/clf) or small GAM; avoid deep nets/large GBMs.
	•	Counts/zero-inflation: Poisson/NegBin/Tweedie GLMs or Tweedie GBM.

⸻

Minimal starter snippets (copy into your Pipelines)

Penalized logistic (baseline, calibrated later)

LogisticRegression(penalty="elasticnet", l1_ratio=0.5,
                   solver="saga", C=1.0, max_iter=5000,
                   class_weight="balanced", random_state=42)

LightGBM (classification)

LGBMClassifier(n_estimators=1000, learning_rate=0.05, num_leaves=31,
               min_data_in_leaf=50, feature_fraction=0.8,
               bagging_fraction=0.8, bagging_freq=1,
               lambda_l1=0.0, lambda_l2=0.0,
               class_weight="balanced", random_state=42)
# Use early_stopping_rounds=50 with a validation fold

XGBoost (regression)

XGBRegressor(n_estimators=2000, learning_rate=0.05, max_depth=6,
             min_child_weight=5, subsample=0.8, colsample_bytree=0.8,
             reg_lambda=1.0, tree_method="hist", random_state=42)
# eval_metric="rmse", early_stopping_rounds=50

Robust regression

HuberRegressor(epsilon=1.35, alpha=1e-4)

SVM (non-linear boundary, moderate N)

SVC(kernel="rbf", C=1.0, gamma="scale",
    class_weight="balanced", probability=True, random_state=42)

Calibration (after model selection)

CalibratedClassifierCV(base_estimator=best_model, method="isotonic", cv=5)


⸻

This plan is now coverage-complete (leakage-safe, time/group aware), statistically sound (right tests per metric), and interpretability-first with concrete defaults.
