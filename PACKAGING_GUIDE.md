# Complete Packaging Guide: Poetry, Building & Artifactory

## Overview

This guide covers how to make your EDA-to-Model Scaffold compatible with Poetry and package it for distribution via PyPI or private artifactories.

## (a) Making it Compatible with Poetry

### Current Status
✅ **Already Compatible**: `[project]` metadata, optional dependencies, tool configurations  
❌ **Needs Changes**: Build system, package structure, script locations

### Changes Made

1. **Package Structure** - Added `__init__.py` files:
   ```
   src/eda_to_model_scaffold/
   ├── __init__.py              # Main package
   ├── data/__init__.py         # Data loading
   ├── features/__init__.py     # Feature engineering  
   ├── models/__init__.py       # ML models
   ├── evaluation/__init__.py   # Evaluation metrics
   ├── calibration/__init__.py  # Model calibration
   ├── explain/__init__.py      # SHAP explainability
   ├── tuning/__init__.py       # Optuna tuning
   ├── time_series/__init__.py  # Time series utils
   └── scripts/__init__.py      # CLI scripts
   ```

2. **Poetry Configuration** - Created `pyproject-poetry.toml`:
   - Uses `poetry-core` build backend
   - Converts optional dependencies to Poetry extras
   - Moves scripts inside package structure
   - Adds Poetry-specific source configuration

### Poetry Commands

```bash
# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Use Poetry version
mv pyproject-poetry.toml pyproject.toml

# Install dependencies
poetry install                    # Core dependencies only
poetry install --extras full     # With ML stack
poetry install --extras dev      # With development tools
poetry install --extras all      # Everything

# Development workflow
poetry shell                      # Activate environment
poetry add numpy                  # Add new dependency
poetry remove numpy               # Remove dependency
poetry update                     # Update all dependencies
```

## (b) Building and Packaging

### Method 1: Using Current Setup (setuptools + build)

```bash
# Install build tools
uv pip install build twine

# Build the package
python -m build

# This creates:
# dist/eda_to_model_scaffold-0.1.0-py3-none-any.whl
# dist/eda_to_model_scaffold-0.1.0.tar.gz
```

### Method 2: Using Poetry

```bash
# Build with Poetry
poetry build

# This creates the same wheel and source distributions
# in dist/ directory
```

### Method 3: Using UV (Modern approach)

```bash
# Build with UV
uv build

# Fast, modern alternative to python -m build
```

### Build Configuration Options

Add to your `pyproject.toml` for custom builds:

```toml
[tool.setuptools.package-data]
"eda_to_model_scaffold" = ["config/*.json", "notebooks/*.ipynb"]

[tool.setuptools.exclude-package-data]
"*" = ["tests/*", "*.pyc", "__pycache__"]
```

## (c) Publishing to Artifactory

### Step 1: Configure Artifactory Access

1. **Create `.pypirc` in home directory**:
   ```ini
   [distutils]
   index-servers = artifactory
   
   [artifactory]
   repository = https://your-artifactory.com/artifactory/api/pypi/your-repo/
   username = your-username
   password = your-password
   ```

2. **Or use environment variables**:
   ```bash
   export TWINE_REPOSITORY_URL=https://your-artifactory.com/artifactory/api/pypi/your-repo/
   export TWINE_USERNAME=your-username
   export TWINE_PASSWORD=your-password
   ```

### Step 2: Upload to Artifactory

```bash
# Method 1: Using twine
twine upload --repository artifactory dist/*

# Method 2: Using Poetry
poetry config repositories.artifactory https://your-artifactory.com/artifactory/api/pypi/your-repo/
poetry config http-basic.artifactory your-username your-password
poetry publish --repository artifactory

# Method 3: Direct upload
curl -u username:password -X PUT \
  "https://your-artifactory.com/artifactory/your-repo/eda-to-model-scaffold/0.1.0/eda_to_model_scaffold-0.1.0-py3-none-any.whl" \
  -T dist/eda_to_model_scaffold-0.1.0-py3-none-any.whl
```

### Step 3: Install from Artifactory

```bash
# Install from your artifactory
pip install eda-to-model-scaffold --index-url https://your-artifactory.com/artifactory/api/pypi/your-repo/simple

# Or with UV
uv pip install eda-to-model-scaffold --index-url https://your-artifactory.com/artifactory/api/pypi/your-repo/simple

# Or with Poetry
poetry source add artifactory https://your-artifactory.com/artifactory/api/pypi/your-repo/simple
poetry add eda-to-model-scaffold
```

## (d) Making it Pip Installable

### Essential Requirements

✅ **Already Done**:
- Proper `pyproject.toml` with metadata
- Package structure with `__init__.py` files
- Entry points for CLI scripts
- Dependency specifications

### Additional Optimizations

1. **Version Management**:
   ```python
   # In src/eda_to_model_scaffold/__init__.py
   __version__ = "0.1.0"
   
   # In pyproject.toml - use dynamic versioning
   [project]
   dynamic = ["version"]
   
   [tool.setuptools.dynamic]
   version = {attr = "eda_to_model_scaffold.__version__"}
   ```

2. **Long Description from README**:
   ```toml
   [project]
   readme = {file = "README.md", content-type = "text/markdown"}
   ```

3. **Proper Classifiers**:
   ```toml
   classifiers = [
       "Development Status :: 4 - Beta",
       "Intended Audience :: Developers",
       "Intended Audience :: Science/Research",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
       "Programming Language :: Python :: 3",
       "Programming Language :: Python :: 3.10",
       "Programming Language :: Python :: 3.11",
       "Programming Language :: Python :: 3.12",
       "Topic :: Scientific/Engineering :: Artificial Intelligence",
   ]
   ```

### Testing Installation

```bash
# Test local installation
pip install -e .
eda-train --help  # Test CLI scripts work

# Test wheel installation
pip install dist/eda_to_model_scaffold-0.1.0-py3-none-any.whl

# Test from source distribution
pip install dist/eda_to_model_scaffold-0.1.0.tar.gz

# Test import
python -c "import eda_to_model_scaffold; print(eda_to_model_scaffold.__version__)"
```

## Complete Workflow Examples

### Scenario 1: Poetry + Private Artifactory

```bash
# 1. Setup Poetry project
mv pyproject-poetry.toml pyproject.toml
poetry install --extras all

# 2. Build package
poetry build

# 3. Configure artifactory
poetry config repositories.company https://artifactory.company.com/api/pypi/ml-packages/
poetry config http-basic.company $USERNAME $PASSWORD

# 4. Publish
poetry publish --repository company

# 5. Install elsewhere
poetry source add company https://artifactory.company.com/api/pypi/ml-packages/simple
poetry add eda-to-model-scaffold
```

### Scenario 2: UV + Public PyPI

```bash
# 1. Build with UV
uv build

# 2. Upload to PyPI
twine upload dist/*

# 3. Install anywhere
uv pip install eda-to-model-scaffold
```

### Scenario 3: Setuptools + Corporate Artifactory

```bash
# 1. Keep current pyproject.toml
# 2. Build package
python -m build

# 3. Upload to corporate artifactory
twine upload --repository-url https://corp-artifactory.com/api/pypi/packages/ dist/*

# 4. Install with index URL
pip install eda-to-model-scaffold --index-url https://corp-artifactory.com/api/pypi/packages/simple
```

## Artifactory-Specific Settings

### JFrog Artifactory Configuration

```toml
# Add to pyproject.toml for Poetry
[[tool.poetry.source]]
name = "artifactory"
url = "https://your-company.jfrog.io/artifactory/api/pypi/pypi-local/simple"
priority = "supplemental"
```

### Nexus Repository Configuration

```bash
# For Nexus repositories
export TWINE_REPOSITORY_URL=https://nexus.company.com/repository/pypi-hosted/
export TWINE_USERNAME=your-username
export TWINE_PASSWORD=your-password

twine upload dist/*
```

### Azure Artifacts Configuration

```bash
# For Azure DevOps Artifacts
pip install keyring artifacts-keyring
twine upload --repository-url https://pkgs.dev.azure.com/your-org/_packaging/your-feed/pypi/upload/ dist/*
```

## Security Best Practices

1. **Use API Tokens**: Prefer tokens over passwords
2. **Environment Variables**: Store credentials in environment, not files
3. **Keyring Integration**: Use system keyring for credential storage
4. **CI/CD Secrets**: Store publishing credentials in CI/CD secret management

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all `__init__.py` files exist
2. **Missing Dependencies**: Check optional dependencies are properly declared
3. **Script Errors**: Verify script entry points match actual function locations
4. **Build Failures**: Check `MANIFEST.in` includes all necessary files

### Validation Commands

```bash
# Check package structure
python -c "import eda_to_model_scaffold; print(dir(eda_to_model_scaffold))"

# Validate metadata
python -m build --check

# Test CLI scripts
eda-train --help
eda-optuna --help
eda-compare --help

# Check dependencies
pip check
```

This guide provides complete coverage for making your project Poetry-compatible, building packages, and publishing to any artifactory that supports PyPI protocol.