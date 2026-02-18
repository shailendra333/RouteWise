"""
GenAI Route Optimizer Agent with Self-Learning
Uses Azure OpenAI for intelligent route optimization decisions
Learns from historical decisions to continuously improve
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from .base_agent import BaseAgent
from .azure_openai_service import get_azure_openai_service
from .learning_engine import LearningEngine

logger = logging.getLogger(__name__)


class GenAIRouteOptimizerAgent(BaseAgent):
    """
    GenAI-powered route optimizer that uses Azure OpenAI for decision making
    Provides natural language reasoning and context-aware optimization
    """

    def __init__(self):
        super().__init__(
            agent_id="genai_route_optimizer_001",
            name="GenAI Route Optimizer Agent",
            capabilities=[
                "genai_route_optimization",
                "natural_language_explanation",
                "context_aware_rerouting",
                "intelligent_priority_handling",
                "self_learning"
            ]
        )

        self.azure_service = get_azure_openai_service()
        self.optimization_threshold = 0.15
        self.learning_engine = LearningEngine()
        self.current_decision_id = None  # Track current decision for outcome recording

    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GenAI to perceive and analyze the environment intelligently
        """
        logger.info(f"{self.name} perceiving environment with GenAI...")

        # Extract basic environment data
        current_routes = environment.get('current_routes', [])
        traffic_data = environment.get('traffic_data', {})
        delivery_status = environment.get('delivery_status', {})

        # Prepare situation data for GenAI analysis
        situation_data = {
            "timestamp": datetime.now().isoformat(),
            "num_active_routes": len(current_routes),
            "routes": current_routes,
            "traffic_conditions": traffic_data,
            "delivery_status": delivery_status
        }

        # Use GenAI to analyze the situation
        genai_analysis = self.azure_service.analyze_situation(
            situation_data,
            agent_role="route_optimizer"
        )

        # Build perception with GenAI insights
        perception = {
            'timestamp': datetime.now().isoformat(),
            'active_routes': current_routes,
            'genai_analysis': genai_analysis,
            'optimization_opportunities': [],
            'traffic_issues': [],
            'priority_deliveries': []
        }

        # Extract actionable insights from GenAI analysis
        recommended_actions = genai_analysis.get('recommended_actions', [])

        for action in recommended_actions:
            if 'reroute' in action.lower() or 'traffic' in action.lower():
                perception['traffic_issues'].append({
                    'description': action,
                    'priority': genai_analysis.get('priority_level', 'medium')
                })
            elif 'optimize' in action.lower():
                perception['optimization_opportunities'].append({
                    'description': action,
                    'confidence': genai_analysis.get('confidence', 0.7)
                })

        logger.info(f"GenAI perception complete. Priority: {genai_analysis.get('priority_level')}")

        return perception

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GenAI to make intelligent routing decisions with learning support
        """
        logger.info(f"{self.name} making decision with GenAI and learned patterns...")

        genai_analysis = perception.get('genai_analysis', {})

        # Query learned patterns for this situation
        decision_type = self._determine_decision_type(perception)
        learned_patterns = self.learning_engine.query_learned_patterns(
            decision_type=decision_type,
            traffic_conditions=perception.get('traffic_issues', {}),
            weather_conditions={}
        )

        # Prepare decision context for GenAI with learned patterns
        decision_context = {
            "current_situation": {
                "active_routes": len(perception.get('active_routes', [])),
                "traffic_issues": perception.get('traffic_issues', []),
                "optimization_opportunities": perception.get('optimization_opportunities', [])
            },
            "genai_initial_analysis": genai_analysis,
            "learned_patterns": [
                {
                    "description": p.get('conditions'),
                    "confidence": p.get('confidence'),
                    "success_rate": f"{p.get('success_count', 0)}/{p.get('times_observed', 1)}",
                    "avg_improvement": f"{p.get('avg_improvement', 0):.0f} minutes"
                }
                for p in learned_patterns[:3]  # Top 3 patterns
            ],
            "constraints": {
                "optimization_threshold": self.optimization_threshold,
                "must_maintain_priorities": True
            }
        }

        # Ask GenAI for specific action recommendations with learning context
        messages = [
            {
                "role": "system",
                "content": "You are an expert route optimization agent with self-learning capabilities. "
                          "Use both your reasoning and historical patterns to make optimal decisions."
            },
            {
                "role": "user",
                "content": f"""
Based on this analysis and learned patterns from past decisions, provide specific routing decisions:

{json.dumps(decision_context, indent=2)}

Consider:
1. Your learned patterns show what has worked well in similar situations
2. Higher confidence patterns are more reliable
3. Balance innovation with proven strategies

Return JSON with:
{{
    "primary_action": "reroute|optimize|prioritize|monitor",
    "specific_routes_to_change": [route IDs or "all"],
    "reasoning": "Clear explanation including reference to learned patterns if used",
    "expected_improvement": {{"time_minutes": X, "cost_dollars": Y}},
    "confidence": 0.0-1.0,
    "alternative_actions": ["backup plan 1", "backup plan 2"],
    "learning_applied": true/false
}}
"""
            }
        ]

        decision_response = self.azure_service.chat_completion(
            messages,
            temperature=0.4,
            max_tokens=800,
            json_mode=True
        )

        try:
            genai_decision = json.loads(decision_response)
        except json.JSONDecodeError:
            genai_decision = {
                "primary_action": "monitor",
                "reasoning": decision_response,
                "confidence": 0.5,
                "learning_applied": False
            }

        # Boost confidence if supported by learned patterns
        if learned_patterns:
            pattern_confidence = sum(p.get('confidence', 0) for p in learned_patterns[:3]) / len(learned_patterns[:3])
            original_confidence = genai_decision.get('confidence', 0.5)
            adjusted_confidence = min((original_confidence + pattern_confidence) / 2, 0.95)
            genai_decision['confidence'] = adjusted_confidence
            genai_decision['confidence_boost'] = round((adjusted_confidence - original_confidence) * 100, 1)
            logger.info(f"🎓 Confidence boosted by {genai_decision['confidence_boost']}% from learned patterns")

        # Generate natural language explanation
        explanation = self.azure_service.generate_explanation(
            context="Route optimization decision with self-learning",
            decision=genai_decision
        )

        decision = {
            'timestamp': datetime.now().isoformat(),
            'genai_decision': genai_decision,
            'action': genai_decision.get('primary_action', 'monitor'),
            'routes_affected': genai_decision.get('specific_routes_to_change', []),
            'reasoning': genai_decision.get('reasoning', ''),
            'natural_explanation': explanation,
            'confidence': genai_decision.get('confidence', 0.7),
            'expected_improvement': genai_decision.get('expected_improvement', {}),
            'alternative_actions': genai_decision.get('alternative_actions', []),
            'learning_applied': genai_decision.get('learning_applied', False),
            'learned_patterns_count': len(learned_patterns)
        }

        # Record this decision for learning
        decision_data = {
            'num_active_routes': len(perception.get('active_routes', [])),
            'traffic_conditions': {
                'issues_count': len(perception.get('traffic_issues', []))
            },
            'weather_conditions': {},
            'genai_reasoning': decision.get('reasoning', ''),
            'confidence_score': decision.get('confidence', 0.5),
            'predicted_time_saving': decision['expected_improvement'].get('time_minutes', 0),
            'predicted_cost_saving': decision['expected_improvement'].get('cost_dollars', 0.0),
            'routes_affected': decision.get('routes_affected', [])
        }

        self.current_decision_id = self.learning_engine.record_decision(
            agent_id=self.agent_id,
            decision_type=decision.get('action', 'monitor'),
            decision_data=decision_data
        )

        logger.info(f"GenAI decision: {decision['action']} (confidence: {decision['confidence']:.2%}) "
                   f"[Decision ID: {self.current_decision_id}]")

        return decision

    def _determine_decision_type(self, perception: Dict[str, Any]) -> str:
        """Determine the primary decision type from perception"""
        if perception.get('traffic_issues'):
            return 'reroute'
        elif perception.get('optimization_opportunities'):
            return 'optimize'
        elif perception.get('priority_deliveries'):
            return 'prioritize'
        else:
            return 'monitor'

    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the GenAI-recommended actions
        """
        logger.info(f"{self.name} executing GenAI decision...")

        action = decision.get('action', 'monitor')

        results = {
            'timestamp': datetime.now().isoformat(),
            'action_taken': action,
            'success': True,
            'natural_explanation': decision.get('natural_explanation', ''),
            'improvements': {},
            'genai_powered': True
        }

        try:
            if action == 'reroute':
                # Simulate rerouting with GenAI-recommended routes
                routes_affected = decision.get('routes_affected', [])
                results['routes_rerouted'] = len(routes_affected) if isinstance(routes_affected, list) else 1
                results['improvements'] = decision.get('expected_improvement', {})

            elif action == 'optimize':
                # Simulate optimization
                results['routes_optimized'] = len(decision.get('routes_affected', []))
                results['improvements'] = decision.get('expected_improvement', {})

            elif action == 'prioritize':
                # Simulate priority reordering
                results['deliveries_reordered'] = 10
                results['improvements'] = {'time_minutes': 15}

            else:  # monitor
                results['action_taken'] = 'monitoring'
                results['improvements'] = {'status': 'no action needed'}

            # Add GenAI reasoning to results
            results['genai_reasoning'] = decision.get('reasoning', '')
            results['confidence'] = decision.get('confidence', 0.7)

            logger.info(f"GenAI action executed successfully: {action}")

        except Exception as e:
            logger.error(f"Error executing GenAI action: {str(e)}")
            results['success'] = False
            results['error'] = str(e)

        return results

    def explain_decision_naturally(self, decision: Dict[str, Any], result: Dict[str, Any]) -> str:
        """
        Generate a comprehensive natural language explanation of what happened
        """
        explanation_context = {
            "decision": decision,
            "result": result,
            "agent_name": self.name
        }

        messages = [
            {
                "role": "system",
                "content": "You are explaining an AI agent's routing decision to a logistics manager. "
                          "Be clear, specific, and focus on business value."
            },
            {
                "role": "user",
                "content": f"""
Create a brief explanation (2-3 sentences) of what this agent did:

{json.dumps(explanation_context, indent=2)}

Focus on:
- What action was taken
- Why it was necessary
- The benefit achieved
"""
            }
        ]

        return self.azure_service.chat_completion(messages, temperature=0.3, max_tokens=200)

    def record_outcome(self, outcome_data: Dict[str, Any]) -> bool:
        """
        Record the actual outcome of the routing decision for learning

        Args:
            outcome_data: Dictionary containing:
                - actual_time_saving: int (minutes)
                - actual_cost_saving: float (dollars)
                - delivery_success_rate: float (0-1)
                - customer_satisfaction: float (0-5)
                - issues_encountered: list

        Returns:
            True if outcome recorded successfully
        """
        if self.current_decision_id and self.current_decision_id > 0:
            success = self.learning_engine.record_outcome(
                decision_id=self.current_decision_id,
                outcome_data=outcome_data
            )

            if success:
                logger.info(f"🧠 Learning from decision {self.current_decision_id}: "
                           f"{outcome_data.get('actual_time_saving', 0)} min saved")

            return success
        else:
            logger.warning("No current decision to record outcome for")
            return False

    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights from the learning engine about performance and patterns
        """
        stats = self.learning_engine.get_learning_statistics()
        patterns = self.learning_engine.get_pattern_insights(limit=5)

        return {
            'statistics': stats,
            'top_patterns': patterns,
            'learning_status': 'active' if stats.get('total_patterns', 0) > 0 else 'initializing'
        }

    def get_status(self) -> Dict[str, Any]:
        """Enhanced status with GenAI and self-learning capabilities"""
        status = super().get_status()
        status['genai_powered'] = True
        status['genai_model'] = 'Azure OpenAI GPT-4'
        status['self_learning_enabled'] = True

        # Add learning statistics
        learning_stats = self.learning_engine.get_learning_statistics()
        status['learning_stats'] = {
            'total_patterns': learning_stats.get('total_patterns', 0),
            'prediction_accuracy': f"{learning_stats.get('prediction_accuracy', 0) * 100:.1f}%",
            'avg_decision_quality': learning_stats.get('avg_decision_quality', 0),
            'quality_improvement': f"{learning_stats.get('quality_improvement', 0):+.1f}%"
        }

        status['special_capabilities'] = [
            'Natural language decision explanations',
            'Context-aware route analysis',
            'Intelligent priority handling',
            'Conversational interaction',
            'Self-learning from outcomes',
            'Pattern-based optimization'
        ]
        return status

