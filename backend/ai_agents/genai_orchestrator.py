"""
GenAI Orchestrator Agent
Uses Azure OpenAI to intelligently coordinate multiple agents
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from .base_agent import BaseAgent
from .azure_openai_service import get_azure_openai_service

logger = logging.getLogger(__name__)


class GenAIOrchestrator(BaseAgent):
    """
    GenAI-powered orchestrator that intelligently coordinates multiple agents
    Uses natural language reasoning for complex multi-agent scenarios
    """

    def __init__(self, agents: Dict[str, BaseAgent] = None):
        super().__init__(
            agent_id="genai_orchestrator_001",
            name="GenAI Orchestrator Agent",
            capabilities=[
                "genai_multi_agent_coordination",
                "intelligent_task_delegation",
                "context_aware_orchestration",
                "natural_language_strategy"
            ]
        )

        self.agents = agents or {}
        self.azure_service = get_azure_openai_service()

    def register_agent(self, agent_key: str, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent_key] = agent
        logger.info(f"Registered agent: {agent.name}")

    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GenAI to perceive system-wide state and agent capabilities
        """
        logger.info(f"{self.name} perceiving system state with GenAI...")

        # Gather information from all agents
        agent_statuses = {}
        for key, agent in self.agents.items():
            agent_statuses[key] = {
                'name': agent.name,
                'status': agent.status,
                'capabilities': agent.capabilities,
                'metrics': agent.performance_metrics
            }

        situation_data = {
            "timestamp": datetime.now().isoformat(),
            "scenario": environment.get('scenario', 'general_operation'),
            "available_agents": agent_statuses,
            "system_state": environment.get('system_state', {}),
            "parameters": environment.get('parameters', {})
        }

        # Use GenAI to analyze the orchestration situation
        genai_analysis = self.azure_service.analyze_situation(
            situation_data,
            agent_role="orchestrator"
        )

        perception = {
            'timestamp': datetime.now().isoformat(),
            'scenario': environment.get('scenario', 'general_operation'),
            'available_agents': agent_statuses,
            'genai_analysis': genai_analysis,
            'system_health': self._assess_system_health(agent_statuses)
        }

        logger.info(f"System health: {perception['system_health']['overall_status']}")

        return perception

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use GenAI to create intelligent orchestration strategy
        """
        logger.info(f"{self.name} creating orchestration strategy with GenAI...")

        genai_analysis = perception.get('genai_analysis', {})
        scenario = perception.get('scenario', 'general_operation')
        available_agents = perception.get('available_agents', {})

        # Ask GenAI for orchestration strategy
        messages = [
            {
                "role": "system",
                "content": "You are a master orchestrator coordinating AI agents in a logistics system. "
                          "Create efficient, strategic coordination plans."
            },
            {
                "role": "user",
                "content": f"""
Create an orchestration strategy for this scenario:

Scenario: {scenario}

Available Agents:
{json.dumps(available_agents, indent=2)}

Initial Analysis:
{json.dumps(genai_analysis, indent=2)}

Return JSON with:
{{
    "strategy_name": "Brief strategy name",
    "agents_to_activate": ["agent_key1", "agent_key2"],
    "execution_order": ["agent_key", "agent_key", "parallel:[agent1,agent2]"],
    "coordination_approach": "sequential|parallel|hybrid",
    "reasoning": "Why this strategy is optimal",
    "expected_outcome": "What we expect to achieve",
    "success_metrics": ["metric1", "metric2"],
    "contingency_plan": "What to do if primary strategy fails",
    "confidence": 0.0-1.0
}}
"""
            }
        ]

        decision_response = self.azure_service.chat_completion(
            messages,
            temperature=0.5,
            max_tokens=1000,
            json_mode=True
        )

        try:
            genai_strategy = json.loads(decision_response)
        except json.JSONDecodeError:
            genai_strategy = {
                "strategy_name": "default_strategy",
                "agents_to_activate": list(available_agents.keys()),
                "execution_order": list(available_agents.keys()),
                "reasoning": decision_response,
                "confidence": 0.6
            }

        # Generate natural language strategy explanation
        strategy_explanation = self.azure_service.generate_explanation(
            context=f"Multi-agent orchestration for {scenario}",
            decision=genai_strategy
        )

        decision = {
            'timestamp': datetime.now().isoformat(),
            'genai_strategy': genai_strategy,
            'strategy_name': genai_strategy.get('strategy_name', 'adaptive_coordination'),
            'agents_to_activate': genai_strategy.get('agents_to_activate', []),
            'execution_order': genai_strategy.get('execution_order', []),
            'coordination_approach': genai_strategy.get('coordination_approach', 'sequential'),
            'reasoning': genai_strategy.get('reasoning', ''),
            'natural_explanation': strategy_explanation,
            'expected_outcome': genai_strategy.get('expected_outcome', ''),
            'confidence': genai_strategy.get('confidence', 0.7),
            'contingency_plan': genai_strategy.get('contingency_plan', '')
        }

        logger.info(f"Strategy: {decision['strategy_name']} (confidence: {decision['confidence']})")

        return decision

    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the GenAI orchestration strategy
        """
        logger.info(f"{self.name} executing GenAI orchestration strategy...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'strategy_executed': decision.get('strategy_name', 'unknown'),
            'agent_results': {},
            'success': True,
            'natural_explanation': decision.get('natural_explanation', ''),
            'genai_powered': True
        }

        try:
            agents_to_activate = decision.get('agents_to_activate', [])
            execution_order = decision.get('execution_order', agents_to_activate)

            # Execute agents according to GenAI strategy
            for step in execution_order:
                if isinstance(step, str) and step.startswith('parallel:'):
                    # Parallel execution
                    parallel_agents = step.replace('parallel:', '').strip('[]').split(',')
                    parallel_results = {}

                    for agent_key in parallel_agents:
                        agent_key = agent_key.strip()
                        if agent_key in self.agents:
                            # Simulate parallel execution
                            parallel_results[agent_key] = {
                                'status': 'executed',
                                'mode': 'parallel'
                            }

                    results['agent_results']['parallel_batch'] = parallel_results

                else:
                    # Sequential execution
                    agent_key = step
                    if agent_key in self.agents:
                        results['agent_results'][agent_key] = {
                            'status': 'executed',
                            'mode': 'sequential',
                            'agent_name': self.agents[agent_key].name
                        }

            results['agents_activated'] = len(results['agent_results'])
            results['coordination_approach'] = decision.get('coordination_approach', 'adaptive')
            results['expected_outcome'] = decision.get('expected_outcome', '')
            results['genai_reasoning'] = decision.get('reasoning', '')

            logger.info(f"Orchestration complete: {results['agents_activated']} agents activated")

        except Exception as e:
            logger.error(f"Orchestration error: {str(e)}")
            results['success'] = False
            results['error'] = str(e)

        return results

    def _assess_system_health(self, agent_statuses: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall system health"""
        total_agents = len(agent_statuses)
        active_agents = sum(1 for agent in agent_statuses.values() if agent.get('status') == 'active')
        error_agents = sum(1 for agent in agent_statuses.values() if agent.get('status') == 'error')

        if error_agents > 0:
            overall_status = 'degraded'
        elif active_agents > total_agents * 0.5:
            overall_status = 'busy'
        else:
            overall_status = 'healthy'

        return {
            'overall_status': overall_status,
            'total_agents': total_agents,
            'active_agents': active_agents,
            'error_agents': error_agents
        }

    def generate_system_report(self,
                              agent_activities: List[Dict[str, Any]],
                              report_type: str = "executive") -> str:
        """
        Generate a comprehensive system report using GenAI
        """
        logger.info(f"Generating {report_type} report with GenAI...")

        report_data = {
            "report_date": datetime.now().strftime('%Y-%m-%d'),
            "total_activities": len(agent_activities),
            "agent_activities": agent_activities,
            "system_metrics": {
                "total_agents": len(self.agents),
                "active_agents": sum(1 for a in self.agents.values() if a.status != 'idle')
            }
        }

        return self.azure_service.generate_report(report_data, report_type)

    def chat_interface(self,
                      user_message: str,
                      conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Natural language interface to query and control the system
        """
        logger.info(f"Processing user message: {user_message[:50]}...")

        # Build context about current system state
        context = {
            "agents": {key: agent.get_status() for key, agent in self.agents.items()},
            "orchestrator_metrics": self.performance_metrics
        }

        return self.azure_service.chat_with_context(
            user_message,
            context,
            conversation_history
        )

    def get_status(self) -> Dict[str, Any]:
        """Enhanced status with GenAI capabilities"""
        status = super().get_status()
        status['genai_powered'] = True
        status['genai_model'] = 'Azure OpenAI GPT-4'
        status['managed_agents'] = len(self.agents)
        status['special_capabilities'] = [
            'Natural language orchestration',
            'Intelligent task delegation',
            'Context-aware strategy creation',
            'Conversational system control',
            'Automated report generation'
        ]
        return status

