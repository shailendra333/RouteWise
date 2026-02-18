"""
Demand Predictor Agent
Autonomous agent for proactive demand forecasting and resource planning
"""

import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DemandPredictorAgent(BaseAgent):
    """
    Intelligent agent that continuously forecasts demand and recommends
    resource allocation and capacity planning
    """

    def __init__(self):
        super().__init__(
            agent_id="demand_predictor_001",
            name="Demand Predictor Agent",
            capabilities=[
                "demand_forecasting",
                "capacity_planning",
                "resource_allocation",
                "anomaly_detection"
            ]
        )

        self.forecast_horizon = 7  # days
        self.confidence_threshold = 0.85
        self.anomaly_threshold = 2.5  # standard deviations

    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive demand patterns and market conditions

        Environment data:
        - historical_orders: Past order data
        - current_capacity: Available resources
        - external_factors: Weather, events, holidays
        - market_trends: Industry trends
        """
        perception = {
            'timestamp': datetime.now().isoformat(),
            'demand_patterns': {},
            'capacity_status': {},
            'anomalies': [],
            'trends': []
        }

        # Analyze historical patterns
        historical_orders = environment.get('historical_orders', [])
        perception['demand_patterns'] = self._analyze_demand_patterns(historical_orders)

        # Assess current capacity
        current_capacity = environment.get('current_capacity', {})
        perception['capacity_status'] = self._assess_capacity(
            current_capacity,
            perception['demand_patterns']
        )

        # Detect anomalies
        perception['anomalies'] = self._detect_anomalies(historical_orders)

        # Identify trends
        perception['trends'] = self._identify_trends(historical_orders)

        # Consider external factors
        external_factors = environment.get('external_factors', {})
        perception['external_impact'] = self._analyze_external_factors(external_factors)

        logger.info(f"Perceived {len(perception['trends'])} demand trends and "
                   f"{len(perception['anomalies'])} anomalies")

        return perception

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide on demand-related actions and recommendations
        """
        decision = {
            'timestamp': datetime.now().isoformat(),
            'forecasts': [],
            'recommendations': [],
            'alerts': [],
            'confidence': 0.0
        }

        # Generate demand forecasts
        demand_patterns = perception['demand_patterns']
        decision['forecasts'] = self._generate_forecasts(
            demand_patterns,
            perception.get('trends', []),
            perception.get('external_impact', {})
        )

        # Generate capacity recommendations
        capacity_status = perception['capacity_status']
        if capacity_status.get('utilization', 0) > 0.85:
            decision['recommendations'].append({
                'type': 'capacity_increase',
                'reason': 'high_utilization',
                'current': capacity_status.get('utilization'),
                'recommended_increase': 0.15,
                'priority': 'high'
            })

        # Generate alerts for anomalies
        for anomaly in perception['anomalies']:
            decision['alerts'].append({
                'type': 'demand_anomaly',
                'severity': anomaly['severity'],
                'description': anomaly['description'],
                'recommended_action': self._recommend_anomaly_action(anomaly)
            })

        # Resource allocation recommendations
        decision['recommendations'].extend(
            self._recommend_resource_allocation(decision['forecasts'], capacity_status)
        )

        # Calculate confidence
        decision['confidence'] = self._calculate_forecast_confidence(
            perception,
            decision['forecasts']
        )

        return decision

    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute demand forecasting actions
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'forecasts_generated': len(decision['forecasts']),
            'recommendations_sent': [],
            'alerts_issued': [],
            'success': True
        }

        # Store forecasts
        for forecast in decision['forecasts']:
            self._store_forecast(forecast)

        results['forecasts_generated'] = len(decision['forecasts'])

        # Process recommendations
        for recommendation in decision['recommendations']:
            action_result = self._execute_recommendation(recommendation)
            results['recommendations_sent'].append(action_result)

        # Issue alerts
        for alert in decision['alerts']:
            alert_result = self._issue_alert(alert)
            results['alerts_issued'].append(alert_result)

        # Calculate impact
        results['estimated_impact'] = self._calculate_impact(decision)

        return results

    def _analyze_demand_patterns(self, historical_orders: List[Dict]) -> Dict[str, Any]:
        """Analyze historical demand patterns"""
        if not historical_orders:
            return {
                'daily_average': 0,
                'weekly_trend': 'stable',
                'seasonality': None
            }

        # Simulate demand analysis (in real system, use actual data analysis)
        total_orders = len(historical_orders)
        days_span = 30  # Assume 30 days of data

        patterns = {
            'daily_average': total_orders / days_span if days_span > 0 else 0,
            'weekly_trend': self._calculate_trend(historical_orders),
            'peak_days': self._identify_peak_days(historical_orders),
            'seasonal_factors': self._extract_seasonal_factors(historical_orders),
            'growth_rate': self._calculate_growth_rate(historical_orders)
        }

        return patterns

    def _assess_capacity(self, current_capacity: Dict, demand_patterns: Dict) -> Dict[str, Any]:
        """Assess current capacity vs demand"""
        vehicles = current_capacity.get('vehicles', 10)
        drivers = current_capacity.get('drivers', 10)
        daily_capacity = vehicles * current_capacity.get('deliveries_per_vehicle', 30)

        daily_demand = demand_patterns.get('daily_average', 0)
        utilization = daily_demand / daily_capacity if daily_capacity > 0 else 0

        return {
            'total_capacity': daily_capacity,
            'current_demand': daily_demand,
            'utilization': min(utilization, 1.0),
            'spare_capacity': max(0, daily_capacity - daily_demand),
            'status': self._get_capacity_status(utilization)
        }

    def _get_capacity_status(self, utilization: float) -> str:
        """Determine capacity status"""
        if utilization < 0.5:
            return 'underutilized'
        elif utilization < 0.8:
            return 'optimal'
        elif utilization < 0.95:
            return 'high'
        else:
            return 'critical'

    def _detect_anomalies(self, historical_orders: List[Dict]) -> List[Dict]:
        """Detect demand anomalies"""
        anomalies = []

        if not historical_orders:
            return anomalies

        # Simulate anomaly detection (in real system, use statistical methods)
        # Check recent data for unusual patterns
        recent_orders = historical_orders[-7:] if len(historical_orders) >= 7 else historical_orders

        if len(recent_orders) > 0:
            recent_avg = len(recent_orders) / 7
            historical_avg = len(historical_orders) / 30

            if recent_avg > historical_avg * 1.5:
                anomalies.append({
                    'type': 'demand_spike',
                    'severity': 'high',
                    'description': f'Recent demand 50% above average',
                    'value': recent_avg,
                    'expected': historical_avg
                })
            elif recent_avg < historical_avg * 0.5:
                anomalies.append({
                    'type': 'demand_drop',
                    'severity': 'medium',
                    'description': f'Recent demand 50% below average',
                    'value': recent_avg,
                    'expected': historical_avg
                })

        return anomalies

    def _identify_trends(self, historical_orders: List[Dict]) -> List[Dict]:
        """Identify demand trends"""
        trends = []

        if len(historical_orders) < 14:
            return trends

        # Simulate trend analysis
        recent_period = historical_orders[-7:]
        previous_period = historical_orders[-14:-7]

        recent_avg = len(recent_period) / 7
        previous_avg = len(previous_period) / 7

        change = (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0

        if abs(change) > 0.1:  # 10% change
            trends.append({
                'type': 'demand_trend',
                'direction': 'increasing' if change > 0 else 'decreasing',
                'magnitude': abs(change),
                'confidence': 0.8,
                'timeframe': 'weekly'
            })

        return trends

    def _analyze_external_factors(self, external_factors: Dict) -> Dict[str, Any]:
        """Analyze external factors impact"""
        impact = {
            'weather': 'neutral',
            'events': [],
            'holidays': [],
            'overall_impact': 0.0
        }

        # Weather impact
        weather = external_factors.get('weather', {})
        if weather.get('condition') in ['rain', 'snow', 'storm']:
            impact['weather'] = 'negative'
            impact['overall_impact'] -= 0.1

        # Events impact
        events = external_factors.get('events', [])
        impact['events'] = events
        if events:
            impact['overall_impact'] += 0.15 * len(events)

        # Holidays impact
        holidays = external_factors.get('holidays', [])
        impact['holidays'] = holidays
        if holidays:
            impact['overall_impact'] += 0.2 * len(holidays)

        return impact

    def _generate_forecasts(self, patterns: Dict, trends: List[Dict],
                           external: Dict) -> List[Dict]:
        """Generate demand forecasts"""
        forecasts = []
        base_demand = patterns.get('daily_average', 100)

        for day in range(self.forecast_horizon):
            forecast_date = datetime.now() + timedelta(days=day+1)

            # Apply trend
            trend_factor = 1.0
            for trend in trends:
                if trend['direction'] == 'increasing':
                    trend_factor += trend['magnitude'] / 7
                else:
                    trend_factor -= trend['magnitude'] / 7

            # Apply external factors
            external_factor = 1.0 + external.get('overall_impact', 0)

            # Apply seasonality (day of week effect)
            weekday_factor = self._get_weekday_factor(forecast_date.weekday())

            # Calculate forecast
            predicted_demand = base_demand * trend_factor * external_factor * weekday_factor

            # Add confidence interval
            std_dev = predicted_demand * 0.15  # 15% standard deviation

            forecasts.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_demand': round(predicted_demand, 2),
                'confidence_lower': round(predicted_demand - 1.96 * std_dev, 2),
                'confidence_upper': round(predicted_demand + 1.96 * std_dev, 2),
                'confidence_level': 0.95,
                'factors': {
                    'trend': trend_factor,
                    'external': external_factor,
                    'seasonality': weekday_factor
                }
            })

        return forecasts

    def _get_weekday_factor(self, weekday: int) -> float:
        """Get demand factor for day of week (0=Monday, 6=Sunday)"""
        weekday_factors = {
            0: 1.0,   # Monday
            1: 1.05,  # Tuesday
            2: 1.1,   # Wednesday
            3: 1.05,  # Thursday
            4: 1.15,  # Friday
            5: 0.8,   # Saturday
            6: 0.6    # Sunday
        }
        return weekday_factors.get(weekday, 1.0)

    def _calculate_trend(self, orders: List[Dict]) -> str:
        """Calculate overall trend"""
        if len(orders) < 7:
            return 'stable'

        recent = len(orders[-7:])
        previous = len(orders[-14:-7]) if len(orders) >= 14 else recent

        if recent > previous * 1.1:
            return 'increasing'
        elif recent < previous * 0.9:
            return 'decreasing'
        return 'stable'

    def _identify_peak_days(self, orders: List[Dict]) -> List[int]:
        """Identify peak demand days of week"""
        # Simulate peak day identification
        return [2, 4]  # Wednesday and Friday

    def _extract_seasonal_factors(self, orders: List[Dict]) -> Dict:
        """Extract seasonal factors"""
        return {
            'has_seasonality': True,
            'period': 'weekly',
            'strength': 0.3
        }

    def _calculate_growth_rate(self, orders: List[Dict]) -> float:
        """Calculate demand growth rate"""
        if len(orders) < 14:
            return 0.0

        recent_avg = len(orders[-7:]) / 7
        previous_avg = len(orders[-14:-7]) / 7

        return (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0.0

    def _recommend_anomaly_action(self, anomaly: Dict) -> str:
        """Recommend action for anomaly"""
        if anomaly['type'] == 'demand_spike':
            return 'Increase capacity and alert operations team'
        elif anomaly['type'] == 'demand_drop':
            return 'Investigate cause and consider promotional activities'
        return 'Monitor closely'

    def _recommend_resource_allocation(self, forecasts: List[Dict],
                                      capacity: Dict) -> List[Dict]:
        """Recommend resource allocation"""
        recommendations = []

        for forecast in forecasts[:3]:  # Next 3 days
            predicted = forecast['predicted_demand']
            current_capacity = capacity.get('total_capacity', 300)

            if predicted > current_capacity * 0.9:
                recommendations.append({
                    'type': 'resource_allocation',
                    'date': forecast['date'],
                    'action': 'increase_vehicles',
                    'current_capacity': current_capacity,
                    'predicted_demand': predicted,
                    'recommended_vehicles': int(predicted / 30) + 1,
                    'priority': 'high'
                })

        return recommendations

    def _calculate_forecast_confidence(self, perception: Dict,
                                       forecasts: List[Dict]) -> float:
        """Calculate overall forecast confidence"""
        base_confidence = 0.85

        # Reduce confidence if anomalies present
        anomalies = len(perception.get('anomalies', []))
        base_confidence -= anomalies * 0.05

        # Increase confidence with stable trends
        trends = perception.get('trends', [])
        if trends and all(t['confidence'] > 0.8 for t in trends):
            base_confidence += 0.05

        return max(0.5, min(base_confidence, 0.95))

    def _store_forecast(self, forecast: Dict):
        """Store forecast for future validation"""
        self.memory.store_experience({
            'type': 'forecast',
            'data': forecast,
            'timestamp': datetime.now().isoformat()
        })

    def _execute_recommendation(self, recommendation: Dict) -> Dict[str, Any]:
        """Execute recommendation"""
        logger.info(f"Executing recommendation: {recommendation['type']}")

        return {
            'recommendation': recommendation,
            'status': 'sent_to_operations',
            'success': True
        }

    def _issue_alert(self, alert: Dict) -> Dict[str, Any]:
        """Issue alert to stakeholders"""
        logger.warning(f"Issuing alert: {alert['type']} - {alert['description']}")

        return {
            'alert': alert,
            'recipients': ['operations', 'management'],
            'status': 'issued',
            'success': True
        }

    def _calculate_impact(self, decision: Dict) -> Dict[str, Any]:
        """Calculate estimated impact of actions"""
        return {
            'improved_planning': True,
            'estimated_cost_savings': len(decision['recommendations']) * 500,
            'estimated_efficiency_gain': 0.12,
            'risk_mitigation': len(decision['alerts'])
        }

