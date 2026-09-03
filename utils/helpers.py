"""Utility functions for the churn prediction project."""

import pandas as pd
import joblib
import os
from typing import Any, Optional


def load_data(filepath: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    df = pd.read_csv(filepath)
    print(f"Data loaded successfully. Shape: {df.shape}")
    return df


def save_model(model: Any, filepath: str) -> None:
    """Save a model to disk using joblib."""
    joblib.dump(model, filepath)
    print(f"Model saved to {filepath}")


def load_model(filepath: str) -> Any:
    """Load a model from disk."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file not found: {filepath}")

    model = joblib.load(filepath)
    print(f"Model loaded from {filepath}")
    return model


def get_data_summary(df: pd.DataFrame) -> dict:
    """Get a summary of the dataframe."""
    summary = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_stats': df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
    }
    return summary


def print_separator(char: str = "=", length: int = 60) -> None:
    """Print a separator line."""
    print(char * length)


def print_header(title: str) -> None:
    """Print a formatted header."""
    print_separator()
    print(f"  {title}")
    print_separator()
