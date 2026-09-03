"""Data Preparation Agent - Handles data loading, cleaning, and preprocessing."""

import pandas as pd
import numpy as np
from typing import Any, Dict
from sklearn.preprocessing import LabelEncoder, StandardScaler
from .base_agent import BaseAgent


class DataPrepAgent(BaseAgent):
    """Agent responsible for data preparation and preprocessing."""

    def __init__(self):
        super().__init__(name="DataPrepAgent")
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []

    def initialize(self) -> None:
        """Initialize data preparation components."""
        self.log("Initializing Data Preparation Agent...")
        self.is_initialized = True
        self.log("Data Preparation Agent ready.")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data preparation pipeline."""
        self.log("Starting data preparation...")

        df = data.get('dataframe')
        if df is None:
            raise ValueError("No dataframe provided in input data")

        df = self._clean_data(df)
        df = self._encode_features(df)
        df = self._scale_features(df, fit=data.get('fit_scaler', True))

        self.log(f"Data preparation complete. Shape: {df.shape}")

        return {
            'dataframe': df,
            'feature_columns': self.feature_columns,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler
        }

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the dataset by handling missing values and duplicates."""
        self.log("Cleaning data...")

        df = df.drop_duplicates()

        if 'Unnamed: 0' in df.columns:
            df = df.drop('Unnamed: 0', axis=1)

        if 'customerID' in df.columns:
            df = df.drop('customerID', axis=1)

        if 'Churn' in df.columns:
            churn_map = {'True': 1, 'False': 0, 'Yes': 1, 'No': 0}
            df['Churn'] = df['Churn'].map(churn_map)
            df['Churn'] = df['Churn'].fillna(0).astype(int)

        if 'TotalCharges' in df.columns:
            df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')

        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].fillna(df[col].median())

        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')

        return df

    def _encode_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features using LabelEncoder."""
        self.log("Encoding categorical features...")

        categorical_cols = df.select_dtypes(include=['object']).columns

        for col in categorical_cols:
            if col != 'Churn':
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le

        self.feature_columns = [col for col in df.columns if col != 'Churn']

        return df

    def _scale_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Scale numerical features using StandardScaler."""
        self.log("Scaling numerical features...")

        numerical_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
        cols_to_scale = [col for col in numerical_cols if col in df.columns]

        if cols_to_scale:
            if fit:
                df[cols_to_scale] = self.scaler.fit_transform(df[cols_to_scale])
            else:
                df[cols_to_scale] = self.scaler.transform(df[cols_to_scale])

        return df

    def prepare_single_customer(self, customer_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare a single customer's data for prediction."""
        df = pd.DataFrame([customer_data])

        for col, le in self.label_encoders.items():
            if col in df.columns and col != 'Churn':
                try:
                    df[col] = le.transform(df[col].astype(str))
                except ValueError:
                    df[col] = 0

        numerical_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
        cols_to_scale = [col for col in numerical_cols if col in df.columns]

        if cols_to_scale:
            df[cols_to_scale] = self.scaler.transform(df[cols_to_scale])

        return df[self.feature_columns]
