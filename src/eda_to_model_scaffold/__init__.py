"""EDA to Model Selection Scaffold.

A comprehensive toolkit for EDA-driven model selection with interpretability-first pipelines
for tabular machine learning tasks.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core modules
from . import data
from . import features  
from . import models
from . import evaluation

# Optional modules (import only if dependencies available)
try:
    from . import explain
except (ImportError, SyntaxError):
    explain = None

try:
    from . import tuning
except (ImportError, SyntaxError):
    tuning = None

try:
    from . import calibration
except (ImportError, SyntaxError):
    calibration = None

try:
    from . import time_series
except (ImportError, SyntaxError):
    time_series = None

__all__ = [
    "data",
    "features", 
    "models",
    "evaluation",
    "explain",
    "tuning", 
    "calibration",
    "time_series",
]
