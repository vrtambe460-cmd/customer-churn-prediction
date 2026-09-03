"""Churn Model - Model management and persistence."""

import joblib
import pandas as pd
from typing import Any, Dict, Optional
from sklearn.base import BaseEstimator


class ChurnModel:
    """Manages churn prediction models."""

    def __init__(self):
        self.model: Optional[BaseEstimator] = None
        self.model_name: str = ""
        self.metrics: Dict[str, float] = {}
        self.feature_columns: list = []

    def save(self, filepath: str) -> None:
        """Save model to disk."""
        model_data = {
            'model': self.model,
            'model_name': self.model_name,
            'metrics': self.metrics,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")

    def load(self, filepath: str) -> None:
        """Load model from disk."""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.model_name = model_data['model_name']
        self.metrics = model_data['metrics']
        self.feature_columns = model_data['feature_columns']
        print(f"Model loaded from {filepath}")

    def predict(self, X: pd.DataFrame) -> Dict[str, Any]:
        """Make predictions on input data."""
        if self.model is None:
            raise ValueError("No model loaded. Call load() first.")

        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]

        return {
            'predictions': predictions,
            'probabilities': probabilities
        }

    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'model_name': self.model_name,
            'metrics': self.metrics,
            'feature_columns': self.feature_columns,
            'is_loaded': self.model is not None
        }
