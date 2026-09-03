"""Customer Churn Prediction System - Main Entry Point

This system uses a multi-agent architecture to predict customer churn
and generate retention recommendations.

Agents:
- DataPrepAgent: Handles data loading, cleaning, and preprocessing
- PredictionAgent: Trains ML models and makes predictions
- RecommendationAgent: Generates retention recommendations
"""

import os
import sys
import pandas as pd
from typing import Dict, Any

from agents import DataPrepAgent, PredictionAgent, RecommendationAgent
from utils.helpers import load_data, print_header, print_separator


class ChurnPredictionOrchestrator:
    """Main orchestrator that coordinates all agents."""

    def __init__(self):
        self.data_prep_agent = DataPrepAgent()
        self.prediction_agent = PredictionAgent()
        self.recommendation_agent = RecommendationAgent()

    def initialize(self) -> None:
        """Initialize all agents."""
        print_header("INITIALIZING SYSTEM")
        self.data_prep_agent.initialize()
        self.prediction_agent.initialize()
        self.recommendation_agent.initialize()
        print("All agents initialized successfully!\n")

    def run(self, data_path: str) -> Dict[str, Any]:
        """Run the complete churn prediction pipeline."""
        print_header("LOADING DATA")
        df = load_data(data_path)
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}\n")

        print_header("DATA PREPARATION")
        prep_result = self.data_prep_agent.execute({
            'dataframe': df,
            'fit_scaler': True
        })

        print_header("MODEL TRAINING & PREDICTION")
        pred_result = self.prediction_agent.execute({
            'dataframe': prep_result['dataframe']
        })

        predictions, probabilities = self.prediction_agent.predict(pred_result['X_test'])

        print_header("GENERATING RECOMMENDATIONS")
        rec_result = self.recommendation_agent.execute({
            'predictions': predictions,
            'probabilities': probabilities,
            'feature_columns': prep_result['feature_columns'],
            'customer_data': pred_result['X_test'],
            'metrics': pred_result['metrics'],
            'best_model_name': pred_result['best_model_name']
        })

        return {
            'prepared_data': prep_result,
            'predictions': pred_result,
            'recommendations': rec_result
        }

    def predict_single_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict churn for a single customer."""
        df = pd.DataFrame([customer_data])

        prep_result = self.data_prep_agent.execute({
            'dataframe': df,
            'fit_scaler': False
        })

        predictions, probabilities = self.prediction_agent.predict(prep_result['dataframe'])

        return {
            'prediction': bool(predictions[0]),
            'churn_probability': float(probabilities[0]),
            'risk_level': self.recommendation_agent._get_risk_level(probabilities[0])
        }


def main():
    """Main function to run the churn prediction system."""
    orchestrator = ChurnPredictionOrchestrator()
    orchestrator.initialize()

    data_path = os.path.join('data', 'telco_churn.csv')

    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        print("Please place 'telco_churn.csv' in the 'data' directory.")
        return

    results = orchestrator.run(data_path)

    print_header("RESULTS SUMMARY")
    print(f"Best Model: {results['predictions']['best_model_name']}")
    print(f"Model Accuracy: {results['predictions']['metrics'][results['predictions']['best_model_name']]['accuracy']:.2%}")
    print("\n" + results['recommendations']['report'])

    print_header("MODEL COMPARISON")
    for model_name, metrics in results['predictions']['metrics'].items():
        print(f"{model_name}:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1']:.4f}")
        print()


if __name__ == "__main__":
    main()
