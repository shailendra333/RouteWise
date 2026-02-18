"""
Orchestrator Agent
Master agent that coordinates multiple specialized agents
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from .base_agent import BaseAgent
from .route_optimizer_agent import RouteOptimizerAgent
from .demand_predictor_agent import DemandPredictorAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Master agent that coordinates multiple specialized agents
    Manages agent collaboration and high-level decision making
    """

    def __init__(self):
        super().__init__(
            agent_id="orchestrator_001",
            name="Orchestrator Agent",
            capabilities=[
                "agent_coordination",
                "task_delegation",
                "conflict_resolution",
                "strategic_planning"
            ]
        )

        # Initialize specialized agents
        self.agents = {
            'route_optimizer': RouteOptimizerAgent(),
            'demand_predictor': DemandPredictorAgent()
        }

        self.task_queue = []
        self.active_tasks = {}

    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive overall system state
        """
        perception = {
            'timestamp': datetime.now().isoformat(),
            'system_status': {},
            'agent_status': {},
            'pending_tasks': [],
            'system_health': 'healthy'
        }

        # Get status of all agents
        for agent_name, agent in self.agents.items():
            perception['agent_status'][agent_name] = agent.get_status()

        # Analyze system state
        perception['system_status'] = self._analyze_system_state(environment)

        # Identify pending tasks
        perception['pending_tasks'] = self._identify_tasks(environment)

        # Assess system health
        perception['system_health'] = self._assess_system_health(perception)

        return perception

    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide on agent coordination and task delegation
        """
        decision = {
            'timestamp': datetime.now().isoformat(),
            'task_assignments': [],
            'agent_actions': {},
            'priorities': [],
            'coordination_plan': {}
        }

        # Assign tasks to appropriate agents
        for task in perception['pending_tasks']:
            assignment = self._assign_task_to_agent(task, perception['agent_status'])
            if assignment:
                decision['task_assignments'].append(assignment)

        # Determine priorities
        decision['priorities'] = self._prioritize_tasks(decision['task_assignments'])

        # Plan agent coordination
        decision['coordination_plan'] = self._plan_coordination(
            decision['task_assignments'],
            perception['agent_status']
        )

        return decision

    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute coordinated agent actions
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'executed_tasks': [],
            'agent_results': {},
            'coordination_outcome': {},
            'success': True
        }

        # Execute high-priority tasks first
        for task_assignment in decision['priorities']:
            agent_name = task_assignment['agent']
            task = task_assignment['task']

            if agent_name in self.agents:
                agent = self.agents[agent_name]

                try:
                    # Execute task through agent
                    agent_result = agent.execute_task(task['environment'])

                    results['agent_results'][agent_name] = agent_result
                    results['executed_tasks'].append({
                        'task': task,
                        'agent': agent_name,
                        'result': agent_result,
                        'success': agent_result.get('success', False)
                    })

                except Exception as e:
                    logger.error(f"Error executing task with {agent_name}: {str(e)}")
                    results['executed_tasks'].append({
                        'task': task,
                        'agent': agent_name,
                        'error': str(e),
                        'success': False
                    })

        # Analyze coordination outcome
        results['coordination_outcome'] = self._analyze_coordination_outcome(results)

        return results

    def _analyze_system_state(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall system state"""
        return {
            'active_routes': len(environment.get('current_routes', [])),
            'pending_orders': len(environment.get('pending_orders', [])),
            'available_vehicles': environment.get('available_vehicles', 0),
            'system_load': self._calculate_system_load(environment)
        }

    def _calculate_system_load(self, environment: Dict[str, Any]) -> float:
        """Calculate current system load"""
        active_routes = len(environment.get('current_routes', []))
        total_capacity = environment.get('total_capacity', 100)

        return min(active_routes / total_capacity, 1.0) if total_capacity > 0 else 0.0

    def _identify_tasks(self, environment: Dict[str, Any]) -> List[Dict]:
        """Identify tasks that need to be executed"""
        tasks = []

        # Check if route optimization needed
        if environment.get('current_routes'):
            tasks.append({
                'type': 'route_optimization',
                'priority': 'high',
                'environment': environment,
                'description': 'Optimize current routes'
            })

        # Check if demand forecasting needed
        if environment.get('historical_orders'):
            tasks.append({
                'type': 'demand_forecasting',
                'priority': 'medium',
                'environment': environment,
                'description': 'Generate demand forecasts'
            })

        # Check for emergency situations
        if environment.get('emergency_orders'):
            tasks.append({
                'type': 'emergency_routing',
                'priority': 'critical',
                'environment': environment,
                'description': 'Handle emergency orders'
            })

        return tasks

    def _assess_system_health(self, perception: Dict[str, Any]) -> str:
        """Assess overall system health"""
        agent_status = perception['agent_status']

        # Check if any agent has errors
        for agent_name, status in agent_status.items():
            if status['status'] == 'error':
                return 'degraded'

        # Check system load
        system_load = perception['system_status'].get('system_load', 0)
        if system_load > 0.9:
            return 'high_load'

        return 'healthy'

    def _assign_task_to_agent(self, task: Dict, agent_status: Dict) -> Dict[str, Any]:
        """Assign task to appropriate agent"""
        task_type = task['type']

        # Map task types to agents
        task_agent_map = {
            'route_optimization': 'route_optimizer',
            'emergency_routing': 'route_optimizer',
            'demand_forecasting': 'demand_predictor',
            'capacity_planning': 'demand_predictor'
        }

        agent_name = task_agent_map.get(task_type)

        if agent_name and agent_name in agent_status:
            agent_info = agent_status[agent_name]

            # Check if agent is available
            if agent_info['status'] in ['idle', 'active']:
                return {
                    'task': task,
                    'agent': agent_name,
                    'assigned_at': datetime.now().isoformat(),
                    'priority': task.get('priority', 'medium')
                }

        return None

    def _prioritize_tasks(self, task_assignments: List[Dict]) -> List[Dict]:
        """Prioritize task assignments"""
        priority_order = {
            'critical': 0,
            'high': 1,
            'medium': 2,
            'low': 3
        }

        return sorted(
            task_assignments,
            key=lambda x: priority_order.get(x.get('priority', 'medium'), 2)
        )

    def _plan_coordination(self, assignments: List[Dict],
                          agent_status: Dict) -> Dict[str, Any]:
        """Plan coordination between agents"""
        plan = {
            'parallel_tasks': [],
            'sequential_tasks': [],
            'dependencies': []
        }

        # Identify tasks that can run in parallel
        agent_workload = {}
        for assignment in assignments:
            agent = assignment['agent']
            if agent not in agent_workload:
                agent_workload[agent] = []
            agent_workload[agent].append(assignment)

        # Tasks for different agents can run in parallel
        for agent, tasks in agent_workload.items():
            if len(tasks) == 1:
                plan['parallel_tasks'].append(tasks[0])
            else:
                # Multiple tasks for same agent run sequentially
                plan['sequential_tasks'].extend(tasks)

        return plan

    def _analyze_coordination_outcome(self, results: Dict) -> Dict[str, Any]:
        """Analyze outcome of agent coordination"""
        total_tasks = len(results['executed_tasks'])
        successful_tasks = sum(
            1 for task in results['executed_tasks']
            if task.get('success', False)
        )

        return {
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0,
            'coordination_efficiency': self._calculate_coordination_efficiency(results),
            'recommendations': self._generate_coordination_recommendations(results)
        }

    def _calculate_coordination_efficiency(self, results: Dict) -> float:
        """Calculate coordination efficiency"""
        # Based on success rate and execution times
        success_rate = results['coordination_outcome'].get('success_rate', 0) if 'coordination_outcome' in results else 0

        # Simple efficiency metric
        return success_rate * 0.9  # 90% of success rate

    def _generate_coordination_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations for improving coordination"""
        recommendations = []

        failed_tasks = [
            task for task in results['executed_tasks']
            if not task.get('success', False)
        ]

        if failed_tasks:
            recommendations.append(
                f"Review {len(failed_tasks)} failed tasks and implement retry logic"
            )

        # Check agent performance
        for agent_name, agent_result in results['agent_results'].items():
            if not agent_result.get('success', False):
                recommendations.append(
                    f"Investigate issues with {agent_name} agent"
                )

        if not recommendations:
            recommendations.append("System operating optimally")

        return recommendations

    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of all agents"""
        summary = {
            'orchestrator': self.get_status(),
            'agents': {}
        }

        for agent_name, agent in self.agents.items():
            summary['agents'][agent_name] = agent.get_status()

        return summary

    def add_agent(self, agent_name: str, agent: BaseAgent):
        """Add a new agent to the system"""
        self.agents[agent_name] = agent
        logger.info(f"Added agent {agent_name} to orchestrator")

    def remove_agent(self, agent_name: str):
        """Remove an agent from the system"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Removed agent {agent_name} from orchestrator")

