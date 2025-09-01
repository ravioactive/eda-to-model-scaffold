# EDA → Model Selection Scaffold (sklearn-first)

This scaffold operationalizes the corrected plan for EDA-driven model selection with **interpretability-first** pipelines.
It includes baselines (penalized linear/logistic), GBMs (LightGBM/XGBoost if installed), calibration, residual/diagnostic plots,
and significance-friendly CV evaluation.

## Quickstart
```bash
# (Recommended) Create a venv
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install minimal or full requirements
pip install -r requirements-min.txt
# or
pip install -r requirements-full.txt

# Open the evaluation notebook
jupyter notebook notebooks/02_train_evaluate.ipynb
```

## UV Workflow Management (Recommended)

This project includes a comprehensive `pyproject.toml` for modern Python dependency management with UV. UV provides faster dependency resolution and better environment management.

### Initial Setup with UV

```bash
# Navigate to project directory
cd /path/to/eda_to_model_scaffold

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
```

### Dependency Management

#### **Core Dependencies** (Always Installed)
```bash
# Install minimal dependencies: numpy, pandas, scikit-learn, matplotlib
uv pip install -e .
```

#### **Optional Dependencies** - Choose Your Workflow

```bash
# Full ML Stack - XGBoost, LightGBM, SHAP, Optuna, statsmodels, scipy
uv pip install -e ".[full]"

# Development Environment - Jupyter, Black, isort, flake8, mypy, pytest
uv pip install -e ".[dev]"

# Testing Suite - pytest with coverage and parallel execution
uv pip install -e ".[test]"

# Documentation - Sphinx documentation tools
uv pip install -e ".[docs]"

# Everything - All optional dependencies
uv pip install -e ".[all]"
```

### Development Workflows

#### **Data Science Exploration**
```bash
# Setup for interactive analysis
uv pip install -e ".[full,dev]"

# Start Jupyter
jupyter notebook notebooks/02_train_evaluate.ipynb

# Available: All ML libraries + interactive notebooks + visualization
```

#### **Model Development & Training**
```bash
# Install core ML stack
uv pip install -e ".[full]"

# Use CLI scripts (defined in pyproject.toml)
eda-train --config config/example_config.json
eda-optuna --config config/optuna_config.json
eda-compare --path results/compare.json
```

#### **Code Quality & Testing**
```bash
# Setup development environment
uv pip install -e ".[dev,test]"

# Format code
black src/ scripts/
isort src/ scripts/

# Type checking
mypy src/

# Modern linting
ruff check src/
ruff format src/

# Run tests with coverage
pytest --cov=src
```

### Daily Workflow Examples

#### **Quick Start - Minimal Setup**
```bash
# For basic data analysis
uv pip install -e .
python scripts/train.py --config config/example_config.json
```

#### **Full ML Development**
```bash
# Complete ML stack
uv pip install -e ".[full,dev]"

# Interactive development
jupyter notebook notebooks/02_train_evaluate.ipynb

# Hyperparameter tuning
eda-optuna --config config/optuna_config.json

# Model comparison
eda-compare --path results/compare.json --task classification
```

### UV-Specific Commands

```bash
# Create fresh environment with specific Python version
uv venv --python 3.10

# Sync with exact requirements
uv pip sync requirements-full.txt

# Check what would be installed (dry run)
uv pip install -e ".[full]" --dry-run

# Generate lock file equivalent
uv pip freeze > requirements-lock.txt

# Update all packages
uv pip install --upgrade -e ".[all]"
```

### PyProject.toml Integration

The `pyproject.toml` defines:
- **[project.scripts]**: CLI commands (`eda-train`, `eda-optuna`, `eda-compare`)
- **[project.optional-dependencies]**: Modular installation options
- **[tool.black]**: Code formatting configuration
- **[tool.mypy]**: Type checking settings
- **[tool.pytest]**: Testing configuration with coverage
- **[tool.ruff]**: Modern linting and formatting

### Key Benefits

✅ **Fast Performance**: UV's Rust-based resolver (3-5x faster than pip)  
✅ **Modular Installation**: Install only what you need  
✅ **Consistent Environments**: Exact version pinning  
✅ **CLI Integration**: Built-in scripts for common tasks  
✅ **Development Tools**: Integrated formatting, linting, testing  
✅ **Python 3.10+ Optimized**: Modern Python features and performance  

## PyProject.toml Configuration Guide

This project uses a comprehensive `pyproject.toml` file for modern Python packaging and development tooling. Here's a detailed breakdown of each section:

### **[build-system]** - Package Building
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```
**Purpose**: Defines how the package is built  
**Usage**: Automatically used by UV/pip when installing with `-e .`

### **[project]** - Core Package Metadata
```toml
[project]
name = "eda-to-model-scaffold"
version = "0.1.0"
description = "EDA-driven model selection scaffold..."
requires-python = ">=3.10"
```
**Purpose**: Package identity, version, and Python compatibility  
**Key Settings**:
- `requires-python = ">=3.10"`: Enforces Python 3.10+ requirement
- `dependencies`: Core libraries always installed (numpy, pandas, scikit-learn, matplotlib)

### **[project.optional-dependencies]** - Modular Installation
```toml
[project.optional-dependencies]
full = ["xgboost>=2.0", "lightgbm>=4.0", "shap>=0.44", ...]
dev = ["jupyter>=1.0.0", "black>=23.0.0", ...]
test = ["pytest>=7.0.0", "pytest-cov>=4.0.0", ...]
```
**Purpose**: Define optional dependency groups for different use cases  
**Usage**:
```bash
uv pip install -e ".[full]"     # ML stack
uv pip install -e ".[dev]"      # Development tools
uv pip install -e ".[test]"     # Testing framework
uv pip install -e ".[all]"      # Everything
```

### **[project.scripts]** - CLI Entry Points
```toml
[project.scripts]
eda-train = "scripts.train:main"
eda-optuna = "scripts.optuna_tune:main"
eda-compare = "scripts.compare:main"
```
**Purpose**: Creates command-line tools after installation  
**Usage**: After `uv pip install -e .`, these commands become available system-wide:
```bash
eda-train --config config/example_config.json
eda-optuna --config config/optuna_config.json
eda-compare --path results/compare.json
```

### **[tool.setuptools]** - Package Structure
```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["*"]

[tool.setuptools.package-dir]
"" = "src"
```
**Purpose**: Tells setuptools to find packages in the `src/` directory  
**Effect**: Enables `src/` layout (recommended modern Python structure)

### **[tool.black]** - Code Formatting
```toml
[tool.black]
line-length = 88
target-version = ["py310", "py311", "py312"]
```
**Purpose**: Configures Black code formatter  
**Usage**:
```bash
black src/ scripts/          # Format code
black --check src/           # Check without modifying
```
**Settings**:
- 88 character line length (Black's default)
- Targets Python 3.10+ syntax

### **[tool.isort]** - Import Sorting
```toml
[tool.isort]
profile = "black"
known_first_party = ["src"]
known_third_party = ["numpy", "pandas", ...]
```
**Purpose**: Sorts and organizes imports consistently  
**Usage**:
```bash
isort src/ scripts/          # Sort imports
isort --check-only src/      # Check without modifying
```
**Settings**:
- Compatible with Black formatting
- Recognizes project modules vs third-party libraries

### **[tool.mypy]** - Type Checking
```toml
[tool.mypy]
python_version = "3.10"
disallow_untyped_defs = true
warn_return_any = true
```
**Purpose**: Static type checking for better code quality  
**Usage**:
```bash
mypy src/                    # Type check source code
mypy --strict src/           # Extra strict checking
```
**Settings**:
- Requires type annotations on functions
- Warns about potential type issues
- Ignores missing imports for ML libraries

### **[tool.pytest]** - Testing Configuration
```toml
[tool.pytest.ini_options]
addopts = ["--cov=src", "--cov-report=html"]
testpaths = ["tests"]
markers = ["slow", "integration", "unit"]
```
**Purpose**: Configures pytest testing framework  
**Usage**:
```bash
pytest                       # Run all tests
pytest --cov=src            # With coverage report
pytest -m "not slow"        # Skip slow tests
```
**Features**:
- Automatic coverage reporting (HTML + terminal)
- Test markers for categorization
- Strict configuration validation

### **[tool.coverage]** - Code Coverage
```toml
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__pycache__/*"]
```
**Purpose**: Measures test coverage of your code  
**Output**: Generates coverage reports in multiple formats:
- Terminal summary
- HTML report (`htmlcov/index.html`)
- XML report (`coverage.xml`)

### **[tool.ruff]** - Modern Linting
```toml
[tool.ruff]
target-version = "py310"
select = ["E", "W", "F", "I", "B", "C4", "UP"]
```
**Purpose**: Fast, modern alternative to flake8 + isort + pyupgrade  
**Usage**:
```bash
ruff check src/              # Lint code
ruff format src/             # Format code (alternative to Black)
ruff check --fix src/        # Auto-fix issues
```
**Rules**:
- `E`, `W`: pycodestyle errors and warnings
- `F`: pyflakes (unused imports, variables)
- `I`: isort (import sorting)
- `B`: flake8-bugbear (common bugs)
- `C4`: flake8-comprehensions (list/dict improvements)
- `UP`: pyupgrade (modern Python syntax)

### **Configuration Consistency**

All tools are configured to work together:
- **Line Length**: 88 characters (Black, isort, ruff)
- **Python Version**: 3.10+ (mypy, ruff, Black targets)
- **Import Sorting**: Black-compatible profile
- **Coverage**: Integrated with pytest

### **Development Workflow Integration**

The configuration enables a complete development workflow:

1. **Code Formatting**:
   ```bash
   black src/ && isort src/     # Format and sort
   # OR
   ruff format src/             # Modern alternative
   ```

2. **Code Quality**:
   ```bash
   mypy src/                    # Type checking
   ruff check src/              # Linting
   ```

3. **Testing**:
   ```bash
   pytest --cov=src            # Tests with coverage
   ```

4. **All-in-One**:
   ```bash
   # Install dev tools
   uv pip install -e ".[dev,test]"
   
   # Run full quality check
   black src/ && isort src/ && mypy src/ && ruff check src/ && pytest --cov=src
   ```

### **Customization**

You can modify any section to fit your preferences:
- Change line length in `[tool.black]` and `[tool.ruff]`
- Add/remove linting rules in `[tool.ruff]`
- Adjust test markers in `[tool.pytest]`
- Modify dependency groups in `[project.optional-dependencies]`

## Contents
- **src/data/loaders.py** — sample and CSV loaders, train/valid/test splits.
- **src/features/pipelines.py** — leakage-safe `ColumnTransformer` builders and helpers (missingness indicators).
- **src/models/** — baselines (ridge/logistic), GBMs (LGBM/XGB), robust regressors, calibration helpers.
- **src/evaluation/** — metrics, plots (ROC/PR, calibration, residuals), CV utilities.
- **scripts/train.py** — CLI training with CV and early stopping (GBMs).
- **notebooks/02_train_evaluate.ipynb** — ready-to-run end-to-end demo (classification + regression).
- **config/example_config.json** — sample configuration for the CLI.
- **requirements-*.txt** — minimal vs full dependency sets.

## Notes
- The notebook defaults to datasets that do **not require internet** (`breast_cancer` for classification, synthetic for regression).
- GBM blocks auto-skip if LightGBM/XGBoost are not available.
- All preprocessing happens inside sklearn Pipelines to avoid leakage.
- Classification includes **probability calibration** (isotonic) after model selection when desired.

## New: Optuna, SHAP, and Time-Series
- **Optuna tuning**: `scripts/optuna_tune.py` with `config/optuna_config.json`. Returns tuned GBM params and trains a best pipeline.
- **SHAP explainers**: `src/explain/shap_utils.py` + `notebooks/04_optuna_shap_demo.ipynb` (works out of the box with LightGBM).
- **Time-series variant**: `src/time_series/*` + `notebooks/03_time_series_cv.ipynb` for `TimeSeriesSplit`, lag/rolling features, and RMSE comparison.

### Commands
```bash
# Tune a LightGBM classifier on breast_cancer with 20 trials
python scripts/optuna_tune.py --config config/optuna_config.json

# Run the time-series notebook
jupyter notebook notebooks/03_time_series_cv.ipynb

# SHAP demo (after tuning or with defaults)
jupyter notebook notebooks/04_optuna_shap_demo.ipynb
```

## Monotonic constraints, Tuning-in-main, Stats tests, and Conformal
- **Monotonic constraints**: map original features to {-1,0,1} in `config/example_config.json` under `monotonic`, and the training script will propagate to LightGBM/XGBoost via the `ColumnTransformer` using `make_monotone_vector_from_preprocessor`.

- **Optuna in main**: enable in config: 
```json
"tuning": {"enabled": true, "family": "lgbm", "n_trials": 20, "prefer_pr_auc": true}
```
- **Model comparison stats**: `src/evaluation/stats.py` provides `delong_roc_test` (binary ROC-AUC) and `paired_ttest` / `wilcoxon_signed` for per-fold metric vectors.
- **Conformal regression intervals**: see `notebooks/05_conformal_intervals.ipynb` (split-conformal).

### Monotonic config example
```json
"monotonic": {
  "f0": 1,   // prediction should increase with f0
  "f3": -1,  // prediction should decrease with f3
  "mean radius": 1  // works with named columns too
}
```

## New: Model Comparison & Risk-Controlled Classification
- **Model comparison (CV + stats)**: `notebooks/06_model_comparison_stats.ipynb` runs stratified CV, plots metric distributions, builds OOF predictions, and applies **DeLong** and **paired tests**.
- **Temperature scaling + selective conformal**: `src/calibration/temperature.py`, `src/calibration/conformal.py`, and `notebooks/07_classification_calibration_conformal.ipynb` for calibrated probabilities and **risk-controlled** (abstaining) classification.

### Notes
- The selective classifier guarantees that on the validation set the **error among auto-decisions** is ≤ α; test-time error should be similar if data are i.i.d.



### Demo config (breast_cancer) with Optuna + monotonic
Run:
```bash
python scripts/train.py --config config/demo_breast_cancer_monotone_optuna.json
```
Results will be appended to `results/compare.json` so you can diff runs automatically.


### Compare runs quickly
```bash
# Compare classification runs by ROC-AUC (default), grouped by task
python scripts/compare.py --path results/compare.json --task classification --by task --top 15

# Compare by config and use PR-AUC instead
python scripts/compare.py --path results/compare.json --task classification --by config --metric pr_auc --top 10

# For regression, compare by RMSE (lower is better)
python scripts/compare.py --path results/compare.json --task regression --metric rmse
```
