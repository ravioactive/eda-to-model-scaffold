# Classification EDA Patterns and Model Selection Guide

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
