"""Prediction Agent - Handles ML model training and prediction."""

import numpy as np
import pandas as pd
from typing import Any, Dict, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import joblib
import os
from .base_agent import BaseAgent


class PredictionAgent(BaseAgent):
    """Agent responsible for model training and making predictions."""

    def __init__(self):
        super().__init__(name="PredictionAgent")
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.metrics = {}

    def initialize(self) -> None:
        """Initialize prediction components."""
        self.log("Initializing Prediction Agent...")
        self.models = {
            'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
                eval_metric='logloss',
                use_label_encoder=False
            )
        }
        self.is_initialized = True
        self.log("Prediction Agent ready.")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute training or prediction based on input."""
        self.log("Starting prediction pipeline...")

        df = data.get('dataframe')
        if df is None:
            raise ValueError("No dataframe provided")

        X = df.drop('Churn', axis=1)
        y = df['Churn']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.log("Training models...")
        self._train_models(X_train, y_train)

        self.log("Evaluating models...")
        self.metrics = self._evaluate_models(X_test, y_test)

        self.best_model_name = max(self.metrics, key=lambda k: self.metrics[k]['accuracy'])
        self.best_model = self.models[self.best_model_name]

        self.log(f"Best model: {self.best_model_name} (Accuracy: {self.metrics[self.best_model_name]['accuracy']:.4f})")

        return {
            'best_model': self.best_model,
            'best_model_name': self.best_model_name,
            'metrics': self.metrics,
            'models': self.models,
            'X_test': X_test,
            'y_test': y_test
        }

    def _train_models(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train all models."""
        for name, model in self.models.items():
            self.log(f"Training {name}...")
            model.fit(X_train, y_train)

    def _evaluate_models(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Dict]:
        """Evaluate all models and return metrics."""
        metrics = {}

        for name, model in self.models.items():
            y_pred = model.predict(X_test)

            metrics[name] = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1': f1_score(y_test, y_pred, zero_division=0)
            }

            self.log(f"{name}: Accuracy={metrics[name]['accuracy']:.4f}")

        return metrics

    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions on new data."""
        if self.best_model is None:
            raise ValueError("No model trained yet. Call execute() first.")

        predictions = self.best_model.predict(X)
        probabilities = self.best_model.predict_proba(X)[:, 1]

        return predictions, probabilities

    def save_model(self, filepath: str) -> None:
        """Save the best model to disk."""
        model_data = {
            'model': self.best_model,
            'model_name': self.best_model_name,
            'metrics': self.metrics
        }
        joblib.dump(model_data, filepath)
        self.log(f"Model saved to {filepath}")

    def load_model(self, filepath: str) -> None:
        """Load a model from disk."""
        model_data = joblib.load(filepath)
        self.best_model = model_data['model']
        self.best_model_name = model_data['model_name']
        self.metrics = model_data['metrics']
        self.log(f"Model loaded from {filepath}")
