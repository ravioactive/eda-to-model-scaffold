# EDA-Driven Model Selection Playbook

How to use this
	1.	Run a simple, honest baseline (linear/logistic with proper preprocessing) and collect diagnostics.
	2.	From EDA + diagnostics, identify patterns (non-linearity, multicollinearity, imbalance, outliers, missingness, etc.).
	3.	Use the pattern → model mapping below to shortlist candidates and rule out poor fits.
	4.	Compare on the right metrics (and for classifiers, calibrated probability quality), then choose the most interpretable model that meets your performance target.

## How to Use This Guide

1. **Run a baseline**: Start with linear/logistic regression with proper preprocessing and collect diagnostics
2. **Identify patterns**: From EDA + diagnostics, identify key patterns (non-linearity, multicollinearity, imbalance, outliers, missingness, etc.)
3. **Map patterns to models**: Use the pattern → model mapping below to shortlist candidates and rule out poor fits
4. **Compare and choose**: Evaluate on appropriate metrics (including calibrated probability quality for classifiers), then choose the most interpretable model that meets your performance target

---

## Regression

### EDA Patterns → Model Choices

| EDA Pattern (How to Detect) | Preferred Models / Remedies (Why) | Usually Unsuitable (Why) | Notes on Interpretability |
|------------------------------|-----------------------------------|--------------------------|---------------------------|
| Strong non-linearity (residuals vs fitted show curves; LOESS/partial residuals; Ramsey RESET) | GAM / EBM (additive, smooth, very interpretable); Gradient Boosting (XGBoost/LightGBM); Random Forest; MLP if large data | Plain OLS without transforms (bias), linear SVR | GAM/EBM gives feature-level curves; monotonic constraints possible |
| Many interactions (PDP/ICE suggests cross-effects; RF/XGB interaction importance) | Boosted Trees (handles higher-order interactions), MLP (if N is big) | Pure additive models (GAM) unless you include 2-way terms; OLS unless you engineer interactions | Use SHAP interaction values to explain GBMs |
| Multicollinearity (VIF > 5–10; condition number high) | Ridge/Elastic Net (stabilizes), Lasso (feature selection), Trees/GBMs (not harmed) | OLS (unstable coefficients, poor inference) | If you need coefficients: ridge/EN; for trees use permutation/SHAP for feature effects |
| Heteroscedasticity (Breusch–Pagan/White; funnel in residuals) | GBMs/RF (variance-robust), Quantile Regression, WLS, target transforms (log/Yeo–Johnson) | Unweighted OLS (inefficient, bad intervals) | Quantile GBM gives interpretable prediction intervals |
| Heavy tails / outliers (QQ plots, leverage/Cook's D, robust z-scores) | Robust regression (Huber, Theil-Sen), Trees/GBMs (resistant), RANSAC (if few outliers) | OLS/kNN reg (sensitive), vanilla MLP without robust loss | Huber loss often a safe drop-in |
| Missing values (patterns, Little's MCAR; missing-indicator correlations) | XGBoost/LightGBM (native missing handling), or impute + linear/GAM; add missingness indicators | OLS/MLP with naive mean impute (bias) | Keep imputation simple + missing flags; document assumptions |
| High cardinality categoricals (wide OHE) | Trees/GBMs (handle splits), target/mean encoding (with CV), embeddings + MLP (large N) | OLS with naive OHE (brittle, many dof) | Prefer CV target encoding to avoid leakage |
| p ≫ n (few rows, many features) | Lasso/Elastic Net, Bayesian linear reg, GAM with few knots | RF/GBM/MLP (high overfit risk) | Stability selection helps interpretability |
| Zero-inflation / counts (many zeros, overdispersion) | Poisson/Tweedie/NegBin GLMs; GBMs with Poisson/Tweedie loss | OLS | Tweedie GBM is great for insurance-like targets |
| Segmented/multimodal data (mixture in KDE; cluster structure) | Tree-based (automatic partitioning), mixture-of-experts, or per-segment models | Single global OLS | Document per-segment partial dependence |

### Quick Regression Ladder (Interpretability → Performance)

1. **Linear/GLM** (with ridge/EN) → diagnose (VIF, residuals)
2. **GAM / EBM** (interpretable non-linearity)
3. **Monotonic GBM** (if domain monotonicity matters) or regular GBM (+ SHAP)
4. **MLP** (only with large data/complexity; use monotonic/shape constraints if needed)

Classification

EDA patterns → model choices (and what to avoid)

### EDA Patterns → Model Choices

| EDA Pattern (How to Detect) | Preferred Models / Remedies (Why) | Usually Unsuitable (Why) | Notes on Interpretability & Calibration |
|------------------------------|-----------------------------------|--------------------------|------------------------------------------|
| Class imbalance (IR>1; minority <10-20%) | Logistic Regression with class_weight, GBMs/XGBoost (scale_pos_weight), calibrated models; consider focal loss (DL) | Plain accuracy-optimized models, uncalibrated RF for probabilities | Evaluate with PR-AUC, F1, balanced accuracy; use Platt/Isotonic or temperature scaling |
| Non-linear boundaries (pairplots, UMAP; logistic baseline underfits) | GBMs/RF, RBF-SVM (if N moderate), MLP (large N) | Logistic without features/terms | SHAP works well for tree ensembles |
| Multicollinearity (as above) | Penalized logistic (ridge/EN), Trees/GBMs | Unpenalized logistic | For coefficients you trust, use ridge/EN |
| Overlapping/noisy classes (kNN error, Bayes error hints) | GBMs with regularization, SVM with soft margin, label smoothing/noise-robust loss for DL | High-variance models without regularization | Use calibration curves + Brier score |
| High cardinality categoricals | GBMs with target/cat encoding (CV), DL with embeddings (large N) | Naive OHE logistic (explodes dof) | Keep encodings leakage-safe |
| Missing values | XGBoost/LightGBM, or impute + logistic/GBM with missing flags | Any model trained on listwise-deleted data (bias) | Calibrate after imputation |
| p ≫ n | Penalized logistic (L1/EN), possibly linear SVM | RF/GBM/MLP (overfit) | Sparse models aid interpretation |
| Segmented/multimodal | Trees/GBMs (automatic splits), mixture-of-experts, per-segment models | Single global logistic | Check per-segment confusion matrices |

### Quick Classification Ladder (Interpretability → Performance)

1. **Penalized Logistic Regression** (class_weight if needed) → inspect coefficients, calibration, confusion matrix
2. **EBM / GAM** (classification) for transparent non-linearity
3. **Gradient Boosting** (+ SHAP and calibration)
4. **RBF-SVM** (if N not huge) or MLP (large N / embeddings for high-cardinality)

---

## Cross-Cutting Diagnostics & Tests

Use these to decide and defend your model choice:

- **Linearity & interactions**: residuals vs fitted; PDP/ICE from a quick RF; RESET test (regression)
- **Multicollinearity**: VIF, correlation heatmap, condition number
- **Heteroscedasticity** (regression): Breusch–Pagan/White; look for residual funnels
- **Outliers/influence**: leverage, Cook's distance, robust z-scores; try a robust fit
- **Distributional quirks**: target skew (Box–Cox/Yeo–Johnson), zero-inflation (Tweedie/NegBin)
- **Class imbalance**: IR, minority support; evaluate with PR-AUC, F1 (macro), balanced accuracy
- **Calibration** (classification): reliability curves, Brier score; post-hoc Platt/Isotonic/temperature scaling
- **Learning curves**: detect high bias (try richer model) vs high variance (regularize/simplify)
- **Data sufficiency**: if rows < 10–20× features (or few events per parameter in logistic), favor penalized linear/GAM over GBM/DL
- **Missingness**: pattern analysis; add missing-indicator features. Prefer models with native missing handling when possible

⸻

Deep learning: when it’s warranted on tabular data
	•	Consider MLP (with embeddings for high-cardinality categoricals) when you have large data, complex interactions, or mixed modalities (text, images + tabular).
	•	Add monotonic/shape constraints or use surrogate explainers (SHAP, integrated gradients).
	•	If data is modest or purely tabular, GBMs typically match or beat MLPs with far better training simplicity and interpretability.

⸻

What to call “unsuitable” (explicit rules of thumb)
	•	Plain OLS/logistic when EDA shows clear non-linearity/interactions and you’re unwilling to add terms/transforms.
	•	Unpenalized linear/logistic in the presence of multicollinearity or p ≫ n.
	•	High-variance models (deep nets, large RF/GBM) with very small datasets.
	•	Naive OHE linear/logistic with very high-cardinality categoricals (unless heavily regularized or encoded).
	•	Uncalibrated classifiers when probabilities matter (choose logistic, calibrated GBM, or apply calibration).
	•	OLS under heteroscedasticity if you need valid intervals (prefer WLS/robust/GBM).
	•	kNN (both tasks) with high dimensional sparse features (curse of dimensionality) or many outliers.
	•	Models that cannot handle missingness unless you impute properly (and record missingness).

⸻

Two concrete, EDA-driven selection recipes

Regression (tabular)
	1.	Run ridge/EN baseline → check residuals (shape), VIF, heteroscedasticity.
	2.	If non-linearity: try GAM/EBM; if big interactions or performance gap persists → GBM (optionally monotonic).
	3.	If outliers/heavy tails: Huber or GBM; if heteroscedastic: Quantile GBM or WLS.
	4.	If high-cardinality categoricals or lots of missing: XGBoost/LightGBM.

Classification (tabular)
	1.	Penalized logistic with class_weight (if imbalanced) + calibration → inspect coefficients and ROC/PR curves.
	2.	If boundary is clearly non-linear or gains needed: EBM → GBM (+ SHAP + calibration).
	3.	If many high-cardinality categoricals: GBM with target/cat encoding; if very large data: MLP with embeddings.
	4.	Keep the most interpretable model that hits the metric goal (PR-AUC / ROC-AUC / F1).

⸻

If you want, I can turn this into a one-page checklist (with exact sklearn/lightgbm/xgboost settings for each scenario and what plots/tests to run in what order).