# Artifactory Workflow Setup Guide

This guide takes you from a raw Python project to a fully configured repository ready for artifactory packaging and publishing. After completing this setup, you'll be ready to use the [ARTIFACTORY_WORKFLOW.md](./ARTIFACTORY_WORKFLOW.md) guide seamlessly.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Assessment](#project-assessment)
- [Step 1: Environment Setup](#step-1-environment-setup)
- [Step 2: Project Structure Setup](#step-2-project-structure-setup)
- [Step 3: Package Configuration](#step-3-package-configuration)
- [Step 4: Development Tools Setup](#step-4-development-tools-setup)
- [Step 5: Build System Configuration](#step-5-build-system-configuration)
- [Step 6: Version Control Setup](#step-6-version-control-setup)
- [Step 7: Testing and Validation](#step-7-testing-and-validation)
- [Step 8: Documentation Setup](#step-8-documentation-setup)
- [Verification Checklist](#verification-checklist)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)

## Prerequisites

### What You Need
- A Python project with source code (any structure)
- Python 3.10 or higher installed
- Git installed
- Basic command line knowledge
- Access to your target artifactory system

### What You'll Get
- Professional Python package structure
- Modern build system (UV + setuptools)
- Comprehensive configuration files
- Ready-to-use packaging workflow
- Complete development environment

## Project Assessment

Before starting, let's assess your current project structure:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Check current structure
find . -name "*.py" | head -10
ls -la

# Check if you have any existing configuration
ls -la *.toml *.cfg *.ini requirements*.txt setup.py setup.cfg 2>/dev/null || echo "No existing config files found"
```

### Common Starting Scenarios

#### Scenario A: Flat Python Files
```
your_project/
├── main.py
├── utils.py
├── models.py
└── data_loader.py
```

#### Scenario B: Basic Directory Structure
```
your_project/
├── src/
│   ├── module1.py
│   └── module2.py
├── tests/
│   └── test_basic.py
└── requirements.txt
```

#### Scenario C: Existing Package (needs modernization)
```
your_project/
├── setup.py
├── your_package/
│   ├── __init__.py
│   └── core.py
└── README.md
```

## Step 1: Environment Setup

### 1.1 Install UV Package Manager

```bash
# Install UV (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell or source profile
source ~/.bashrc  # or ~/.zshrc

# Verify installation
uv --version
```

### 1.2 Create Project Virtual Environment

```bash
# Navigate to your project root
cd /path/to/your/project

# Create virtual environment with UV
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Verify activation
which python
python --version
```

### 1.3 Install Essential Tools

```bash
# Install build and packaging tools
uv pip install build twine wheel setuptools

# Install development tools
uv pip install black isort mypy pytest pytest-cov

# Install optional but recommended tools
uv pip install ruff bandit safety
```

## Step 2: Project Structure Setup

### 2.1 Assess Current Structure and Plan Migration

```bash
# Create a backup of your current project
cp -r . ../backup_$(basename $(pwd))_$(date +%Y%m%d)

# Analyze current Python files
find . -name "*.py" -not -path "./.venv/*" | sort
```

### 2.2 Create Modern Package Structure

#### For Scenario A (Flat Files):
```bash
# Create src-layout structure
mkdir -p src/your_package_name
mkdir -p tests
mkdir -p config
mkdir -p notebooks
mkdir -p scripts

# Move Python files to package directory
mv *.py src/your_package_name/

# Create __init__.py files
touch src/your_package_name/__init__.py
```

#### For Scenario B (Basic Structure):
```bash
# Reorganize to src-layout if not already
if [ ! -d "src" ]; then
    mkdir -p src/your_package_name
    mv your_existing_modules/* src/your_package_name/
fi

# Ensure proper __init__.py files exist
find src -type d -exec touch {}/__init__.py \;
```

#### For Scenario C (Existing Package):
```bash
# Modernize to src-layout
mkdir -p src
mv your_package src/

# Remove old setup.py if it exists
mv setup.py setup.py.backup 2>/dev/null || true
```

### 2.3 Create Package Module Structure

```bash
# Define your package name (replace 'your_package_name' with actual name)
PACKAGE_NAME="your_package_name"

# Create comprehensive package structure
mkdir -p src/$PACKAGE_NAME/{data,features,models,evaluation,utils}
mkdir -p src/$PACKAGE_NAME/scripts

# Create __init__.py files for all modules
find src/$PACKAGE_NAME -type d -exec touch {}/__init__.py \;
```

### 2.4 Organize Existing Code by Functionality

```bash
# Example organization (adapt to your code)
# Move data-related code
find src/$PACKAGE_NAME -name "*data*" -o -name "*load*" | head -5
# mv data_related_files src/$PACKAGE_NAME/data/

# Move model-related code  
find src/$PACKAGE_NAME -name "*model*" -o -name "*train*" | head -5
# mv model_related_files src/$PACKAGE_NAME/models/

# Move utility functions
find src/$PACKAGE_NAME -name "*util*" -o -name "*helper*" | head -5
# mv utility_files src/$PACKAGE_NAME/utils/
```

## Step 3: Package Configuration

### 3.1 Create pyproject.toml

```bash
# Create modern package configuration
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package-name"
version = "0.1.0"
description = "Your package description"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
maintainers = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = [
    "machine-learning",
    "data-science",
    # Add relevant keywords
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.10"

# Core dependencies (analyze your imports and add here)
dependencies = [
    "numpy>=1.23",
    "pandas>=2.0",
    # Add your actual dependencies
]

# Optional dependencies for different use cases
[project.optional-dependencies]
# ML stack
ml = [
    "scikit-learn>=1.3",
    "xgboost>=2.0",
    "lightgbm>=4.0",
    # Add ML-specific dependencies
]

# Development dependencies
dev = [
    "jupyter>=1.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

# Testing dependencies
test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-xdist>=3.0.0",
]

# All dependencies combined
all = [
    "your-package-name[ml,dev,test]"
]

[project.urls]
Homepage = "https://github.com/yourusername/your-package-name"
Repository = "https://github.com/yourusername/your-package-name"
Documentation = "https://github.com/yourusername/your-package-name#readme"
"Bug Tracker" = "https://github.com/yourusername/your-package-name/issues"

# CLI scripts (if your package has command-line tools)
[project.scripts]
# your-tool = "your_package_name.scripts.main:main"

[tool.setuptools.packages.find]
where = ["src"]
include = ["*"]

[tool.setuptools.package-dir]
"" = "src"

# Development tool configurations
[tool.black]
line-length = 88
target-version = ["py310", "py311", "py312"]
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["your_package_name"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]
testpaths = ["tests"]

[tool.ruff]
target-version = "py310"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501"]
EOF
```

### 3.2 Customize Configuration for Your Project

```bash
# Get your actual package name from directory structure
ACTUAL_PACKAGE=$(find src -maxdepth 1 -type d | grep -v __pycache__ | tail -1 | xargs basename)
echo "Detected package name: $ACTUAL_PACKAGE"

# Update pyproject.toml with actual package name
sed -i.bak "s/your-package-name/$ACTUAL_PACKAGE/g" pyproject.toml
sed -i.bak "s/your_package_name/$ACTUAL_PACKAGE/g" pyproject.toml

# Update with your actual information
read -p "Enter your name: " YOUR_NAME
read -p "Enter your email: " YOUR_EMAIL
read -p "Enter package description: " DESCRIPTION

sed -i.bak "s/Your Name/$YOUR_NAME/g" pyproject.toml
sed -i.bak "s/your.email@example.com/$YOUR_EMAIL/g" pyproject.toml
sed -i.bak "s/Your package description/$DESCRIPTION/g" pyproject.toml
```

### 3.3 Analyze and Add Dependencies

```bash
# Analyze your code for imports
echo "Analyzing imports in your code..."
find src -name "*.py" -exec grep -h "^import\|^from" {} \; | sort | uniq | head -20

# Create requirements files for reference
echo "Creating requirements files..."
cat > requirements-min.txt << 'EOF'
# Minimal dependencies
numpy>=1.23
pandas>=2.0
EOF

cat > requirements-full.txt << 'EOF'
# Full dependencies (copy from your analysis)
numpy>=1.23
pandas>=2.0
scikit-learn>=1.3
matplotlib>=3.7
# Add other dependencies found in your code
EOF
```

## Step 4: Development Tools Setup

### 4.1 Create Package __init__.py Files

```bash
# Create main package __init__.py
cat > src/$ACTUAL_PACKAGE/__init__.py << EOF
"""$ACTUAL_PACKAGE - Your package description."""

__version__ = "0.1.0"
__author__ = "$YOUR_NAME"
__email__ = "$YOUR_EMAIL"

# Import main modules (customize based on your structure)
try:
    from . import utils
except ImportError:
    pass

try:
    from . import models
except ImportError:
    pass

try:
    from . import data
except ImportError:
    pass

__all__ = ["utils", "models", "data"]
EOF

# Create module __init__.py files
for module in data features models evaluation utils scripts; do
    if [ -d "src/$ACTUAL_PACKAGE/$module" ]; then
        cat > src/$ACTUAL_PACKAGE/$module/__init__.py << EOF
"""$module module for $ACTUAL_PACKAGE."""

# Import main functions/classes from this module
# from .main_file import main_function, MainClass

__all__ = []  # Add your public API here
EOF
    fi
done
```

### 4.2 Create Development Configuration Files

```bash
# Create .gitignore
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# MyPy
.mypy_cache/

# Jupyter
.ipynb_checkpoints

# Data and models (customize based on your needs)
data/
models/
*.pkl
*.joblib
*.h5

# Logs and outputs
logs/
outputs/
results/

# Credentials
.env
.env.local
secrets.json
.pypirc
EOF

# Create MANIFEST.in for package distribution
cat > MANIFEST.in << 'EOF'
include README.md
include LICENSE
include pyproject.toml
include requirements*.txt
recursive-include config *.json *.yaml *.yml
recursive-include notebooks *.ipynb
global-exclude *.pyc
global-exclude *.pyo
global-exclude __pycache__
global-exclude .git*
global-exclude .DS_Store
EOF
```

### 4.3 Setup Testing Framework

```bash
# Create tests directory structure
mkdir -p tests
touch tests/__init__.py

# Create basic test file
cat > tests/test_basic.py << EOF
"""Basic tests for $ACTUAL_PACKAGE."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import $ACTUAL_PACKAGE
except ImportError as e:
    pytest.skip(f"Cannot import $ACTUAL_PACKAGE: {e}", allow_module_level=True)


def test_package_import():
    """Test that the package can be imported."""
    assert $ACTUAL_PACKAGE.__version__
    assert $ACTUAL_PACKAGE.__author__


def test_package_version():
    """Test that version is properly set."""
    assert isinstance($ACTUAL_PACKAGE.__version__, str)
    assert len($ACTUAL_PACKAGE.__version__.split('.')) >= 2


# Add more tests based on your package functionality
class TestBasicFunctionality:
    """Test basic package functionality."""
    
    def test_placeholder(self):
        """Placeholder test - replace with actual tests."""
        assert True
        
    # Add tests for your main functions/classes
    # def test_your_main_function(self):
    #     from $ACTUAL_PACKAGE.module import your_function
    #     result = your_function()
    #     assert result is not None
EOF

# Create pytest configuration
cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
EOF
```

## Step 5: Build System Configuration

### 5.1 Install Package in Development Mode

```bash
# Install your package in editable mode
uv pip install -e .

# Verify installation
python -c "import $ACTUAL_PACKAGE; print(f'Package {$ACTUAL_PACKAGE.__name__} v{$ACTUAL_PACKAGE.__version__} imported successfully')"
```

### 5.2 Install Dependencies

```bash
# Install development dependencies
uv pip install -e ".[dev,test]"

# If you have ML dependencies
uv pip install -e ".[ml]" 2>/dev/null || echo "ML dependencies not available, skipping"

# Verify key tools are available
black --version
isort --version
mypy --version
pytest --version
```

### 5.3 Create Build Scripts

```bash
# Create scripts directory
mkdir -p scripts

# Create build script
cat > scripts/build.sh << 'EOF'
#!/bin/bash
set -e

echo "🏗️  Building package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Format code
echo "📝 Formatting code..."
black src/ tests/
isort src/ tests/

# Type checking
echo "🔍 Type checking..."
mypy src/ || echo "⚠️  Type checking issues found"

# Run tests
echo "🧪 Running tests..."
pytest

# Build package
echo "📦 Building distribution..."
python -m build

# Validate package
echo "✅ Validating package..."
twine check dist/*

echo "🎉 Build completed successfully!"
ls -la dist/
EOF

chmod +x scripts/build.sh

# Create development setup script
cat > scripts/dev-setup.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    uv venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install package in development mode
uv pip install -e ".[dev,test]"

# Install additional development tools
uv pip install build twine

echo "✅ Development environment ready!"
echo "📝 Next steps:"
echo "   1. Activate environment: source .venv/bin/activate"
echo "   2. Run tests: pytest"
echo "   3. Build package: ./scripts/build.sh"
EOF

chmod +x scripts/dev-setup.sh
```

## Step 6: Version Control Setup

### 6.1 Initialize Git Repository (if not already done)

```bash
# Initialize git if not already a git repository
if [ ! -d ".git" ]; then
    git init
    echo "📁 Initialized git repository"
fi

# Add all files
git add .

# Create initial commit
git status
read -p "Create initial commit? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Initial package setup with modern Python packaging

- Added src-layout package structure
- Configured pyproject.toml with modern build system
- Added development tools (black, isort, mypy, pytest)
- Created comprehensive .gitignore
- Added build and development scripts
- Ready for artifactory workflow"
fi
```

### 6.2 Create Version Management

```bash
# Create version bumping configuration
cat > .bumpversion.cfg << EOF
[bumpversion]
current_version = 0.1.0
commit = True
tag = True

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file:src/$ACTUAL_PACKAGE/__init__.py]
search = __version__ = "{current_version}"
replace = __version__ = "{new_version}"
EOF

# Install bump2version for easy version management
uv pip install bump2version
```

## Step 7: Testing and Validation

### 7.1 Run Complete Test Suite

```bash
echo "🧪 Running complete validation..."

# Test package import
echo "Testing package import..."
python -c "
import sys
sys.path.insert(0, 'src')
import $ACTUAL_PACKAGE
print(f'✅ Package {$ACTUAL_PACKAGE.__name__} v{$ACTUAL_PACKAGE.__version__} imports successfully')
print(f'📍 Location: {$ACTUAL_PACKAGE.__file__}')
"

# Run code formatting
echo "🎨 Formatting code..."
black --check src/ tests/ || (echo "❌ Code formatting needed" && black src/ tests/)
isort --check-only src/ tests/ || (echo "❌ Import sorting needed" && isort src/ tests/)

# Run type checking
echo "🔍 Type checking..."
mypy src/ || echo "⚠️  Type checking issues found (non-blocking)"

# Run tests
echo "🧪 Running tests..."
pytest -v

# Test package building
echo "📦 Testing package build..."
python -m build

# Validate built package
echo "✅ Validating built package..."
twine check dist/*

echo "🎉 All validations passed!"
```

### 7.2 Test Installation from Built Package

```bash
# Test installation from wheel
echo "🔄 Testing installation from built package..."

# Create temporary environment for testing
uv venv test-env
source test-env/bin/activate

# Install from wheel
uv pip install dist/*.whl

# Test import in clean environment
python -c "
import $ACTUAL_PACKAGE
print(f'✅ Package {$ACTUAL_PACKAGE.__name__} v{$ACTUAL_PACKAGE.__version__} installed and imports successfully')
"

# Cleanup test environment
deactivate
rm -rf test-env/

# Reactivate original environment
source .venv/bin/activate

echo "✅ Package installation test passed!"
```

## Step 8: Documentation Setup

### 8.1 Create README.md

```bash
# Create comprehensive README
cat > README.md << EOF
# $ACTUAL_PACKAGE

$DESCRIPTION

## Installation

### From Source
\`\`\`bash
git clone <repository-url>
cd $ACTUAL_PACKAGE
uv venv && source .venv/bin/activate
uv pip install -e ".[all]"
\`\`\`

### From Package Repository
\`\`\`bash
# From PyPI (when published)
pip install $ACTUAL_PACKAGE

# From corporate artifactory
pip install $ACTUAL_PACKAGE --index-url https://your-artifactory.com/simple
\`\`\`

## Quick Start

\`\`\`python
import $ACTUAL_PACKAGE

# Add usage examples here
print(f"Using {$ACTUAL_PACKAGE.__name__} v{$ACTUAL_PACKAGE.__version__}")
\`\`\`

## Development

### Setup Development Environment
\`\`\`bash
./scripts/dev-setup.sh
source .venv/bin/activate
\`\`\`

### Run Tests
\`\`\`bash
pytest
\`\`\`

### Build Package
\`\`\`bash
./scripts/build.sh
\`\`\`

### Code Quality
\`\`\`bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/
\`\`\`

## Package Structure

\`\`\`
$ACTUAL_PACKAGE/
├── src/$ACTUAL_PACKAGE/          # Main package code
│   ├── data/                     # Data handling modules
│   ├── models/                   # Model implementations
│   ├── utils/                    # Utility functions
│   └── scripts/                  # Command-line scripts
├── tests/                        # Test suite
├── config/                       # Configuration files
├── notebooks/                    # Jupyter notebooks
└── scripts/                      # Build and development scripts
\`\`\`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: \`pytest\`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
EOF
```

### 8.2 Create LICENSE file

```bash
# Create MIT license (customize as needed)
cat > LICENSE << EOF
MIT License

Copyright (c) $(date +%Y) $YOUR_NAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### 8.3 Create CHANGELOG.md

```bash
cat > CHANGELOG.md << EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial package setup with modern Python packaging
- Comprehensive development environment configuration
- Automated build and testing scripts

## [0.1.0] - $(date +%Y-%m-%d)

### Added
- Initial release
- Core package functionality
- Development tools setup
- Documentation and examples

[Unreleased]: https://github.com/yourusername/$ACTUAL_PACKAGE/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/$ACTUAL_PACKAGE/releases/tag/v0.1.0
EOF
```

## Verification Checklist

Run this checklist to ensure everything is properly set up:

```bash
# Create verification script
cat > scripts/verify-setup.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying package setup..."

# Check files exist
echo "📁 Checking required files..."
files=("pyproject.toml" "README.md" "LICENSE" ".gitignore" "MANIFEST.in")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
    fi
done

# Check package structure
echo "📦 Checking package structure..."
if [ -d "src" ]; then
    echo "  ✅ src/ directory"
    if [ -f "src/*//__init__.py" ]; then
        echo "  ✅ Package __init__.py"
    else
        echo "  ❌ Package __init__.py (missing)"
    fi
else
    echo "  ❌ src/ directory (missing)"
fi

# Check virtual environment
echo "🐍 Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "  ✅ Virtual environment"
else
    echo "  ❌ Virtual environment (missing)"
fi

# Check package installation
echo "📋 Checking package installation..."
python -c "
try:
    import sys
    sys.path.insert(0, 'src')
    pkg_name = [d for d in __import__('os').listdir('src') if not d.startswith('.')][0]
    pkg = __import__(pkg_name)
    print(f'  ✅ Package {pkg.__name__} v{pkg.__version__} imports')
except Exception as e:
    print(f'  ❌ Package import failed: {e}')
"

# Check build capability
echo "🏗️  Checking build capability..."
if command -v python -m build &> /dev/null; then
    echo "  ✅ Build tools available"
else
    echo "  ❌ Build tools missing"
fi

# Check development tools
echo "🛠️  Checking development tools..."
tools=("black" "isort" "mypy" "pytest")
for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "  ✅ $tool"
    else
        echo "  ❌ $tool (missing)"
    fi
done

echo "🎯 Setup verification complete!"
echo "📖 Next step: Follow ARTIFACTORY_WORKFLOW.md for packaging and publishing"
EOF

chmod +x scripts/verify-setup.sh

# Run verification
./scripts/verify-setup.sh
```

## Troubleshooting Common Issues

### Issue 1: Import Errors

```bash
# Problem: Cannot import package
# Solution: Check package structure and __init__.py files

# Debug imports
python -c "
import sys
sys.path.insert(0, 'src')
print('Python path:', sys.path[:3])
print('Available packages in src:', __import__('os').listdir('src'))
"

# Fix: Ensure __init__.py files exist
find src -type d -exec touch {}/__init__.py \;
```

### Issue 2: Build Failures

```bash
# Problem: Build fails with missing files
# Solution: Check MANIFEST.in and file structure

# Debug build
python -m build --verbose

# Fix: Update MANIFEST.in to include missing files
echo "include missing_file.txt" >> MANIFEST.in
```

### Issue 3: Dependency Issues

```bash
# Problem: Dependencies not resolving
# Solution: Check and update pyproject.toml dependencies

# Analyze actual imports in your code
grep -r "^import\|^from" src/ | cut -d: -f2 | sort | uniq

# Update pyproject.toml with actual dependencies
```

### Issue 4: Test Failures

```bash
# Problem: Tests fail to run
# Solution: Check test configuration and imports

# Debug test discovery
pytest --collect-only

# Fix: Ensure proper test structure
mkdir -p tests
touch tests/__init__.py
```

## Ready for Artifactory Workflow

After completing this setup, your project will have:

✅ **Modern Package Structure** - src-layout with proper __init__.py files  
✅ **Build System Configuration** - pyproject.toml with all necessary settings  
✅ **Development Environment** - Virtual environment with all tools  
✅ **Quality Tools** - Black, isort, mypy, pytest configured  
✅ **Version Control** - Git repository with proper .gitignore  
✅ **Documentation** - README, LICENSE, CHANGELOG  
✅ **Build Scripts** - Automated build and validation  
✅ **Testing Framework** - Pytest with coverage reporting  

### Next Steps

1. **Customize the configuration** - Update package name, dependencies, and metadata
2. **Organize your code** - Move existing code into the proper module structure  
3. **Add tests** - Create tests for your main functionality
4. **Follow ARTIFACTORY_WORKFLOW.md** - Use the workflow guide for packaging and publishing

Your package is now ready for professional development and artifactory publishing! 🚀

---

## Quick Command Reference

```bash
# Setup (run once)
./scripts/dev-setup.sh

# Daily development
source .venv/bin/activate
pytest                    # Run tests
black src/ tests/        # Format code
./scripts/build.sh       # Build package

# Version management
bump2version patch       # 0.1.0 → 0.1.1
bump2version minor       # 0.1.0 → 0.2.0
bump2version major       # 0.1.0 → 1.0.0

# Ready for artifactory workflow
# Follow ARTIFACTORY_WORKFLOW.md
```
