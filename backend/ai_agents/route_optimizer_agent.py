"""
Route Optimizer Agent
Autonomous agent for real-time route optimization and dynamic routing decisions
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RouteOptimizerAgent(BaseAgent):
    """
    Intelligent agent that continuously monitors and optimizes delivery routes
    Uses real-time traffic, weather, and delivery status for dynamic decisions
    """

    def __init__(self):
        super().__init__(
            agent_id="route_optimizer_001",
            name="Route Optimizer Agent",
            capabilities=[
                "route_optimization",
                "dynamic_rerouting",
                "traffic_analysis",
                "delivery_scheduling"
            ]
        )

        self.optimization_threshold = 0.15  # 15% improvement threshold
        self.traffic_weight = 0.4
        self.distance_weight = 0.3
        self.time_weight = 0.3

    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive current delivery situation

        Environment data:
        - current_routes: Active delivery routes
        - traffic_data: Real-time traffic information
        - delivery_status: Status of ongoing deliveries
        - weather_conditions: Current weather
        """
        perception = {
            'timestamp': datetime.now().isoformat(),
            'active_deliveries': [],
            'traffic_issues': [],
            'optimization_opportunities': [],
            'priority_deliveries': []
        }

        # Extract active routes
        current_routes = environment.get('current_routes', [])
        perception['active_deliveries'] = current_routes

        # Analyze traffic conditions
        traffic_data = environment.get('traffic_data', {})
        for route_id, route in enumerate(current_routes):
            traffic_score = self._analyze_traffic(route, traffic_data)
            if traffic_score > 0.7:  # High traffic
                perception['traffic_issues'].append({
                    'route_id': route_id,
                    'severity': traffic_score,
                    'affected_segments': self._identify_congested_segments(route, traffic_data)
                })

        # Identify optimization opportunities
        for route_id, route in enumerate(current_routes):
            potential_improvement = self._calculate_potential_improvement(route)
            if potential_improvement > self.optimization_threshold:
                perception['optimization_opportunities'].append({
                    'route_id': route_id,
                    'improvement_potential': potential_improvement,
                    'reason': 'inefficient_sequence'
                })

        # Identify priority deliveries
        for route in current_routes:
            for delivery in route.get('deliveries', []):
                if self._is_priority_delivery(delivery):
                    perception['priority_deliveries'].append(delivery)

        logger.info(f"Perceived {len(perception['optimization_opportunities'])} optimization opportunities")

        return perception

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide on route optimization actions based on perception
        """
        decision = {
            'timestamp': datetime.now().isoformat(),
            'actions': [],
            'confidence': 0.0,
            'reasoning': []
        }

        # Priority 1: Handle traffic issues
        if perception['traffic_issues']:
            for issue in perception['traffic_issues']:
                action = self._decide_rerouting(issue, perception)
                decision['actions'].append(action)
                decision['reasoning'].append(
                    f"Reroute route {issue['route_id']} due to traffic severity {issue['severity']:.2f}"
                )

        # Priority 2: Optimize inefficient routes
        if perception['optimization_opportunities']:
            for opportunity in perception['optimization_opportunities']:
                if opportunity['improvement_potential'] > 0.2:  # 20%+ improvement
                    action = self._decide_optimization(opportunity, perception)
                    decision['actions'].append(action)
                    decision['reasoning'].append(
                        f"Optimize route {opportunity['route_id']} - potential improvement: "
                        f"{opportunity['improvement_potential']*100:.1f}%"
                    )

        # Priority 3: Prioritize urgent deliveries
        if perception['priority_deliveries']:
            action = self._decide_priority_handling(perception['priority_deliveries'])
            decision['actions'].append(action)
            decision['reasoning'].append(
                f"Resequence {len(perception['priority_deliveries'])} priority deliveries"
            )

        # Calculate overall confidence
        if decision['actions']:
            decision['confidence'] = self._calculate_decision_confidence(perception, decision)

        return decision

    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute route optimization actions
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'executed_actions': [],
            'improvements': {},
            'success': True
        }

        total_improvement = 0
        successful_actions = 0

        for action in decision['actions']:
            try:
                if action['type'] == 'reroute':
                    result = self._execute_reroute(action)
                elif action['type'] == 'optimize':
                    result = self._execute_optimization(action)
                elif action['type'] == 'prioritize':
                    result = self._execute_prioritization(action)
                else:
                    continue

                results['executed_actions'].append({
                    'action': action,
                    'result': result,
                    'success': result['success']
                })

                if result['success']:
                    successful_actions += 1
                    total_improvement += result.get('improvement', 0)

            except Exception as e:
                logger.error(f"Error executing action: {str(e)}")
                results['executed_actions'].append({
                    'action': action,
                    'error': str(e),
                    'success': False
                })

        # Calculate overall improvements
        if successful_actions > 0:
            results['improvements'] = {
                'average_improvement': total_improvement / successful_actions,
                'total_routes_optimized': successful_actions,
                'estimated_time_saved': total_improvement * 30,  # minutes
                'estimated_cost_saved': total_improvement * 50   # dollars
            }

        results['success'] = successful_actions > 0

        return results

    def _analyze_traffic(self, route: Dict, traffic_data: Dict) -> float:
        """Analyze traffic conditions for a route (0-1 score)"""
        if not traffic_data:
            return 0.0

        # Simulate traffic analysis (in real system, use real traffic API)
        congestion_score = np.random.random() * 0.5  # 0-0.5 baseline

        # Check time of day
        hour = datetime.now().hour
        if 7 <= hour <= 9 or 16 <= hour <= 19:  # Rush hours
            congestion_score += 0.3

        return min(congestion_score, 1.0)

    def _identify_congested_segments(self, route: Dict, traffic_data: Dict) -> List[str]:
        """Identify specific congested segments in route"""
        segments = []
        deliveries = route.get('deliveries', [])

        for i in range(len(deliveries) - 1):
            segment_id = f"seg_{i}_{i+1}"
            if np.random.random() > 0.7:  # Simulate congestion detection
                segments.append(segment_id)

        return segments

    def _calculate_potential_improvement(self, route: Dict) -> float:
        """Calculate potential improvement for a route"""
        deliveries = route.get('deliveries', [])
        if len(deliveries) < 3:
            return 0.0

        # Simulate improvement potential (in real system, use actual route analysis)
        current_efficiency = route.get('efficiency', 0.7)
        optimal_efficiency = 0.95

        return max(0, optimal_efficiency - current_efficiency)

    def _is_priority_delivery(self, delivery: Dict) -> bool:
        """Check if delivery is high priority"""
        priority = delivery.get('priority', 'normal')
        time_window = delivery.get('time_window_end')

        if priority == 'urgent':
            return True

        if time_window:
            # Check if approaching time window
            try:
                window_end = datetime.fromisoformat(time_window)
                time_remaining = (window_end - datetime.now()).total_seconds() / 3600
                return time_remaining < 2  # Less than 2 hours
            except:
                pass

        return False

    def _decide_rerouting(self, issue: Dict, perception: Dict) -> Dict[str, Any]:
        """Decide on rerouting action"""
        return {
            'type': 'reroute',
            'route_id': issue['route_id'],
            'severity': issue['severity'],
            'alternative_path': 'calculate_alternative',
            'estimated_time_saved': issue['severity'] * 20  # minutes
        }

    def _decide_optimization(self, opportunity: Dict, perception: Dict) -> Dict[str, Any]:
        """Decide on optimization action"""
        return {
            'type': 'optimize',
            'route_id': opportunity['route_id'],
            'improvement_potential': opportunity['improvement_potential'],
            'optimization_method': 'genetic_algorithm'
        }

    def _decide_priority_handling(self, priority_deliveries: List[Dict]) -> Dict[str, Any]:
        """Decide on priority delivery handling"""
        return {
            'type': 'prioritize',
            'deliveries': priority_deliveries,
            'resequence': True
        }

    def _calculate_decision_confidence(self, perception: Dict, decision: Dict) -> float:
        """Calculate confidence in decision"""
        base_confidence = 0.7

        # Increase confidence with more data
        if perception['traffic_issues']:
            base_confidence += 0.1
        if perception['optimization_opportunities']:
            base_confidence += 0.1

        # Check past performance
        if self.performance_metrics['success_rate'] > 0.8:
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    def _execute_reroute(self, action: Dict) -> Dict[str, Any]:
        """Execute rerouting action"""
        logger.info(f"Executing reroute for route {action['route_id']}")

        # In real system, integrate with routing algorithm
        # Here we simulate the action
        improvement = action['severity'] * 0.2  # 20% improvement per severity unit

        return {
            'success': True,
            'route_id': action['route_id'],
            'improvement': improvement,
            'new_eta': (datetime.now() + timedelta(minutes=30)).isoformat(),
            'distance_change': -action['severity'] * 5  # km reduction
        }

    def _execute_optimization(self, action: Dict) -> Dict[str, Any]:
        """Execute route optimization"""
        logger.info(f"Executing optimization for route {action['route_id']}")

        # In real system, call genetic_algorithm.py or OR-Tools
        improvement = action['improvement_potential']

        return {
            'success': True,
            'route_id': action['route_id'],
            'improvement': improvement,
            'method': action['optimization_method'],
            'distance_saved': improvement * 10,  # km
            'time_saved': improvement * 15  # minutes
        }

    def _execute_prioritization(self, action: Dict) -> Dict[str, Any]:
        """Execute priority delivery handling"""
        logger.info(f"Executing prioritization for {len(action['deliveries'])} deliveries")

        return {
            'success': True,
            'deliveries_prioritized': len(action['deliveries']),
            'improvement': 0.1,  # 10% improvement in on-time delivery
            'resequenced_routes': len(action['deliveries']) // 3
        }

