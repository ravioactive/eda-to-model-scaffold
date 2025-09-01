"""Model explainability utilities."""

try:
    from .shap_utils import *
    __all__ = ["shap_utils"]
except ImportError:
    __all__ = []
