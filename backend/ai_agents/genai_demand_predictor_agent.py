"""
GenAI Demand Predictor Agent
Uses Azure OpenAI for intelligent demand forecasting and analysis
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import numpy as np

from .base_agent import BaseAgent
from .azure_openai_service import get_azure_openai_service

logger = logging.getLogger(__name__)


class GenAIDemandPredictorAgent(BaseAgent):
    """
    GenAI-powered demand predictor that uses Azure OpenAI for forecasting
    Provides contextual demand analysis with natural language insights
    """

    def __init__(self):
        super().__init__(
            agent_id="genai_demand_predictor_001",
            name="GenAI Demand Predictor Agent",
            capabilities=[
                "genai_demand_forecasting",
                "contextual_pattern_analysis",
                "anomaly_explanation",
                "natural_language_insights"
            ]
        )

        self.azure_service = get_azure_openai_service()
        self.forecast_days = 7

    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GenAI to perceive demand patterns and contextual factors
        """
        logger.info(f"{self.name} perceiving demand patterns with GenAI...")

        historical_orders = environment.get('historical_orders', [])
        current_capacity = environment.get('current_capacity', {})
        external_factors = environment.get('external_factors', {})

        # Calculate basic statistics
        if historical_orders:
            recent_orders = historical_orders[-30:]  # Last 30 days
            avg_orders = np.mean([order.get('orders', 0) for order in recent_orders if isinstance(order, dict)])
            trend = self._calculate_trend(recent_orders)
        else:
            avg_orders = 100
            trend = "stable"

        # Prepare data for GenAI analysis
        situation_data = {
            "timestamp": datetime.now().isoformat(),
            "historical_summary": {
                "total_days": len(historical_orders),
                "recent_30_day_average": float(avg_orders),
                "detected_trend": trend
            },
            "current_capacity": current_capacity,
            "external_factors": external_factors
        }

        # Use GenAI to analyze patterns
        genai_analysis = self.azure_service.analyze_situation(
            situation_data,
            agent_role="demand_predictor"
        )

        perception = {
            'timestamp': datetime.now().isoformat(),
            'historical_summary': situation_data['historical_summary'],
            'genai_analysis': genai_analysis,
            'detected_patterns': [],
            'anomalies': [],
            'external_factors': external_factors
        }

        # Extract insights from GenAI
        analysis_text = genai_analysis.get('analysis', '')
        if 'spike' in analysis_text.lower() or 'increase' in analysis_text.lower():
            perception['detected_patterns'].append({
                'type': 'upward_trend',
                'description': 'GenAI detected potential demand increase'
            })

        if 'anomaly' in analysis_text.lower() or 'unusual' in analysis_text.lower():
            perception['anomalies'].append({
                'type': 'pattern_deviation',
                'description': genai_analysis.get('analysis', '')
            })

        logger.info(f"GenAI perception: {genai_analysis.get('priority_level')} priority")

        return perception

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GenAI to make intelligent forecasting decisions
        """
        logger.info(f"{self.name} making forecast decision with GenAI...")

        genai_analysis = perception.get('genai_analysis', {})
        historical_summary = perception.get('historical_summary', {})

        # Ask GenAI for specific forecast recommendations
        messages = [
            {
                "role": "system",
                "content": "You are an expert demand forecasting agent. Provide accurate predictions with clear reasoning."
            },
            {
                "role": "user",
                "content": f"""
Based on this demand data, provide a 7-day forecast:

Historical Summary:
{json.dumps(historical_summary, indent=2)}

Current Analysis:
{json.dumps(genai_analysis, indent=2)}

Return JSON with:
{{
    "forecast_method": "trend_based|seasonal|ml_augmented",
    "daily_predictions": [
        {{"day": 1, "predicted_orders": X, "confidence": 0.0-1.0}},
        ...7 days
    ],
    "key_insights": ["insight1", "insight2", "insight3"],
    "recommendations": ["action1", "action2"],
    "potential_risks": ["risk1", "risk2"],
    "confidence_overall": 0.0-1.0
}}

Base predictions on the 30-day average of {historical_summary.get('recent_30_day_average', 100)} orders/day.
Consider the detected trend: {historical_summary.get('detected_trend', 'stable')}.
"""
            }
        ]

        decision_response = self.azure_service.chat_completion(
            messages,
            temperature=0.5,
            max_tokens=1200,
            json_mode=True
        )

        try:
            genai_forecast = json.loads(decision_response)
        except json.JSONDecodeError:
            # Fallback forecast
            base_orders = historical_summary.get('recent_30_day_average', 100)
            genai_forecast = {
                "forecast_method": "trend_based",
                "daily_predictions": [
                    {"day": i+1, "predicted_orders": int(base_orders * (1 + i*0.02)), "confidence": 0.75}
                    for i in range(7)
                ],
                "key_insights": [decision_response],
                "confidence_overall": 0.7
            }

        # Generate natural language summary
        forecast_summary = self.azure_service.generate_explanation(
            context="Demand forecast for next 7 days",
            decision=genai_forecast
        )

        decision = {
            'timestamp': datetime.now().isoformat(),
            'genai_forecast': genai_forecast,
            'forecast_method': genai_forecast.get('forecast_method', 'trend_based'),
            'daily_predictions': genai_forecast.get('daily_predictions', []),
            'natural_summary': forecast_summary,
            'key_insights': genai_forecast.get('key_insights', []),
            'recommendations': genai_forecast.get('recommendations', []),
            'risks': genai_forecast.get('potential_risks', []),
            'confidence': genai_forecast.get('confidence_overall', 0.7)
        }

        logger.info(f"GenAI forecast generated with {decision['confidence']:.2f} confidence")

        return decision

    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and store GenAI forecasts
        """
        logger.info(f"{self.name} generating GenAI forecasts...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'forecasts_generated': len(decision.get('daily_predictions', [])),
            'success': True,
            'natural_summary': decision.get('natural_summary', ''),
            'genai_powered': True
        }

        try:
            # Store forecasts
            forecasts = []
            base_date = datetime.now()

            for pred in decision.get('daily_predictions', []):
                forecast_date = base_date + timedelta(days=pred.get('day', 1))
                forecasts.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'predicted_demand': pred.get('predicted_orders', 100),
                    'confidence': pred.get('confidence', 0.7),
                    'genai_generated': True
                })

            results['forecasts'] = forecasts
            results['key_insights'] = decision.get('key_insights', [])
            results['recommendations'] = decision.get('recommendations', [])
            results['potential_risks'] = decision.get('risks', [])
            results['model_type'] = decision.get('forecast_method', 'genai_hybrid')
            results['overall_confidence'] = decision.get('confidence', 0.7)

            logger.info(f"Generated {len(forecasts)} GenAI forecasts")

        except Exception as e:
            logger.error(f"Error generating forecasts: {str(e)}")
            results['success'] = False
            results['error'] = str(e)

        return results

    def _calculate_trend(self, recent_data: List[Dict]) -> str:
        """Calculate basic trend from recent data"""
        if len(recent_data) < 7:
            return "insufficient_data"

        first_half = [d.get('orders', 0) for d in recent_data[:len(recent_data)//2] if isinstance(d, dict)]
        second_half = [d.get('orders', 0) for d in recent_data[len(recent_data)//2:] if isinstance(d, dict)]

        if not first_half or not second_half:
            return "stable"

        avg_first = np.mean(first_half)
        avg_second = np.mean(second_half)

        change_percent = ((avg_second - avg_first) / avg_first) * 100

        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"

    def explain_forecast_naturally(self, forecast: Dict[str, Any]) -> str:
        """
        Generate detailed natural language explanation of the forecast
        """
        messages = [
            {
                "role": "system",
                "content": "You are explaining a demand forecast to a logistics manager. "
                          "Be specific about numbers, dates, and business implications."
            },
            {
                "role": "user",
                "content": f"""
Explain this 7-day demand forecast in a brief, actionable way:

{json.dumps(forecast, indent=2)}

Include:
1. Overall forecast trend
2. Key dates/events to watch
3. Recommended actions
4. Confidence level

Keep it under 4 sentences.
"""
            }
        ]

        return self.azure_service.chat_completion(messages, temperature=0.4, max_tokens=300)

    def get_status(self) -> Dict[str, Any]:
        """Enhanced status with GenAI capabilities"""
        status = super().get_status()
        status['genai_powered'] = True
        status['genai_model'] = 'Azure OpenAI GPT-4'
        status['special_capabilities'] = [
            'Contextual demand forecasting',
            'Natural language insights',
            'Anomaly explanation',
            'Business recommendation generation'
        ]
        return status

