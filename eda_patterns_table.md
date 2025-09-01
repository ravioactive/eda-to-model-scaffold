# EDA Patterns and Model Selection Guide

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
