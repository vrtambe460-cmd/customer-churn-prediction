"""Recommendation Agent - Generates retention recommendations based on predictions."""

from typing import Any, Dict, List
from .base_agent import BaseAgent


class RecommendationAgent(BaseAgent):
    """Agent responsible for generating customer retention recommendations."""

    def __init__(self):
        super().__init__(name="RecommendationAgent")
        self.churn_factors = {
            'Contract': {
                'Month-to-month': 3.2,
                'One year': 1.0,
                'Two year': 0.5
            },
            'InternetService': {
                'Fiber optic': 1.8,
                'DSL': 1.0,
                'No': 0.3
            },
            'OnlineSecurity': {
                'No': 1.5,
                'Yes': 0.7
            },
            'TechSupport': {
                'No': 1.4,
                'Yes': 0.6
            },
            'PaymentMethod': {
                'Electronic check': 1.6,
                'Mailed check': 1.0,
                'Bank transfer': 0.8,
                'Credit card': 0.8
            }
        }

    def initialize(self) -> None:
        """Initialize recommendation engine."""
        self.log("Initializing Recommendation Agent...")
        self.is_initialized = True
        self.log("Recommendation Agent ready.")

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on prediction results."""
        self.log("Generating recommendations...")

        predictions = data.get('predictions')
        probabilities = data.get('probabilities')
        feature_columns = data.get('feature_columns')
        customer_data = data.get('customer_data')
        metrics = data.get('metrics')
        best_model_name = data.get('best_model_name')

        recommendations = self._generate_recommendations(
            predictions, probabilities, feature_columns, customer_data
        )

        report = self._generate_report(
            predictions, probabilities, recommendations,
            metrics, best_model_name, customer_data
        )

        self.log("Recommendations generated.")

        return {
            'recommendations': recommendations,
            'report': report
        }

    def _generate_recommendations(
        self,
        predictions,
        probabilities,
        feature_columns,
        customer_data
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations for each customer."""
        recommendations = []

        if hasattr(predictions, '__len__'):
            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                customer_recs = self._get_customer_recommendations(
                    prob, customer_data.iloc[i] if customer_data is not None else None,
                    feature_columns
                )
                recommendations.append({
                    'customer_index': i,
                    'will_churn': bool(pred),
                    'churn_probability': float(prob),
                    'risk_level': self._get_risk_level(prob),
                    'retention_actions': customer_recs
                })
        else:
            customer_recs = self._get_customer_recommendations(
                probabilities,
                customer_data.iloc[0] if customer_data is not None else None,
                feature_columns
            )
            recommendations.append({
                'customer_index': 0,
                'will_churn': bool(predictions),
                'churn_probability': float(probabilities),
                'risk_level': self._get_risk_level(probabilities),
                'retention_actions': customer_recs
            })

        return recommendations

    def _get_risk_level(self, probability: float) -> str:
        """Determine risk level based on churn probability."""
        if probability >= 0.7:
            return "HIGH"
        elif probability >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_customer_recommendations(self, probability, customer_info, feature_columns) -> List[str]:
        """Get specific recommendations for a customer."""
        recommendations = []

        if probability >= 0.5:
            recommendations.append("URGENT: Customer has high churn risk - immediate attention needed")

        recommendations.append("Schedule a personalized follow-up call within 48 hours")
        recommendations.append("Review account for potential billing issues or service gaps")

        if probability >= 0.3:
            recommendations.append("Offer loyalty discount or promotional rate")
            recommendations.append("Consider bundling additional services at reduced price")
            recommendations.append("Provide priority customer support access")

        if probability >= 0.5:
            recommendations.append("Assign dedicated account manager for personalized service")
            recommendations.append("Send satisfaction survey to identify pain points")

        return recommendations

    def _generate_report(
        self,
        predictions,
        probabilities,
        recommendations,
        metrics,
        best_model_name,
        customer_data
    ) -> str:
        """Generate a comprehensive report."""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("       CUSTOMER CHURN PREDICTION REPORT")
        report_lines.append("=" * 60)
        report_lines.append("")

        if metrics and best_model_name:
            report_lines.append(f"Model Used: {best_model_name.replace('_', ' ').title()}")
            report_lines.append(f"Model Accuracy: {metrics[best_model_name]['accuracy']:.2%}")
            report_lines.append(f"Precision: {metrics[best_model_name]['precision']:.2%}")
            report_lines.append(f"Recall: {metrics[best_model_name]['recall']:.2%}")
            report_lines.append(f"F1 Score: {metrics[best_model_name]['f1']:.2%}")
            report_lines.append("")

        report_lines.append("-" * 60)
        report_lines.append("       CUSTOMER ANALYSIS")
        report_lines.append("-" * 60)
        report_lines.append("")

        for rec in recommendations[:5]:
            report_lines.append(f"Customer #{rec['customer_index'] + 1}")
            report_lines.append(f"  Churn Probability: {rec['churn_probability']:.1%}")
            report_lines.append(f"  Risk Level: {rec['risk_level']}")
            report_lines.append(f"  Will Churn: {'Yes' if rec['will_churn'] else 'No'}")
            report_lines.append("")
            report_lines.append("  Recommended Actions:")
            for i, action in enumerate(rec['retention_actions'], 1):
                report_lines.append(f"    {i}. {action}")
            report_lines.append("")
            report_lines.append("-" * 60)
            report_lines.append("")

        report_lines.append("=" * 60)
        report_lines.append("       SUMMARY")
        report_lines.append("=" * 60)

        high_risk = sum(1 for r in recommendations if r['risk_level'] == 'HIGH')
        medium_risk = sum(1 for r in recommendations if r['risk_level'] == 'MEDIUM')
        low_risk = sum(1 for r in recommendations if r['risk_level'] == 'LOW')

        report_lines.append(f"Total Customers Analyzed: {len(recommendations)}")
        report_lines.append(f"High Risk: {high_risk}")
        report_lines.append(f"Medium Risk: {medium_risk}")
        report_lines.append(f"Low Risk: {low_risk}")
        report_lines.append("")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)
