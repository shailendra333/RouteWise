"""
Base Agent Class for AI Agent System
Provides core functionality for all autonomous agents
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentMemory:
    """Memory system for agents to store and retrieve experiences"""

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.short_term = []  # Recent experiences
        self.long_term = {}   # Important patterns and learnings
        self.working_memory = {}  # Current task context

    def store_experience(self, experience: Dict[str, Any]):
        """Store an experience in short-term memory"""
        self.short_term.append({
            'timestamp': datetime.now().isoformat(),
            'data': experience
        })

        # Move to long-term if capacity exceeded
        if len(self.short_term) > self.capacity:
            self._consolidate_memory()

    def _consolidate_memory(self):
        """Move important patterns to long-term memory"""
        # Keep only recent 80% in short-term
        cutoff = int(self.capacity * 0.8)
        archived = self.short_term[:-cutoff]
        self.short_term = self.short_term[-cutoff:]

        # Analyze and store patterns in long-term
        for exp in archived:
            pattern_key = self._extract_pattern(exp)
            if pattern_key:
                if pattern_key not in self.long_term:
                    self.long_term[pattern_key] = []
                self.long_term[pattern_key].append(exp)

    def _extract_pattern(self, experience: Dict[str, Any]) -> Optional[str]:
        """Extract patterns from experiences"""
        data = experience.get('data', {})
        if 'action' in data and 'outcome' in data:
            return f"{data['action']}_{data.get('context', 'general')}"
        return None

    def recall(self, query: str) -> List[Dict]:
        """Retrieve relevant memories based on query"""
        results = []

        # Search short-term memory
        for exp in self.short_term:
            if query.lower() in str(exp).lower():
                results.append(exp)

        # Search long-term memory
        if query in self.long_term:
            results.extend(self.long_term[query])

        return results[:10]  # Return top 10 results


class BaseAgent(ABC):
    """
    Base class for all AI Agents in the logistics system
    Implements core agent functionality and lifecycle
    """

    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.status = "idle"
        self.memory = AgentMemory()
        self.performance_metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'average_execution_time': 0,
            'success_rate': 1.0
        }
        self.created_at = datetime.now()
        self.last_active = None

        logger.info(f"Agent {self.name} ({self.agent_id}) initialized with capabilities: {capabilities}")

    @abstractmethod
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive the environment and extract relevant information

        Args:
            environment: Current state of the environment

        Returns:
            Dict containing perceived information
        """
        pass

    @abstractmethod
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make decisions based on perception

        Args:
            perception: Information from perception phase

        Returns:
            Dict containing decision and action plan
        """
        pass

    @abstractmethod
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the decided action

        Args:
            decision: Decision from decide phase

        Returns:
            Dict containing action results
        """
        pass

    def learn(self, experience: Dict[str, Any]):
        """
        Learn from experience and update knowledge

        Args:
            experience: Experience data to learn from
        """
        self.memory.store_experience(experience)
        self._update_performance_metrics(experience)

        logger.info(f"Agent {self.name} learned from experience: {experience.get('outcome', 'unknown')}")

    def _update_performance_metrics(self, experience: Dict[str, Any]):
        """Update agent performance metrics"""
        if experience.get('success', False):
            self.performance_metrics['tasks_completed'] += 1
        else:
            self.performance_metrics['tasks_failed'] += 1

        total_tasks = (self.performance_metrics['tasks_completed'] +
                      self.performance_metrics['tasks_failed'])

        if total_tasks > 0:
            self.performance_metrics['success_rate'] = (
                self.performance_metrics['tasks_completed'] / total_tasks
            )

        # Update average execution time
        if 'execution_time' in experience:
            current_avg = self.performance_metrics['average_execution_time']
            new_time = experience['execution_time']
            self.performance_metrics['average_execution_time'] = (
                (current_avg * (total_tasks - 1) + new_time) / total_tasks
            )

    def execute_task(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete agent cycle: Perceive -> Decide -> Act -> Learn

        Args:
            environment: Current environment state

        Returns:
            Dict containing execution results
        """
        start_time = datetime.now()
        self.status = "active"
        self.last_active = start_time

        try:
            # Perceive
            logger.info(f"Agent {self.name} perceiving environment...")
            perception = self.perceive(environment)

            # Decide
            logger.info(f"Agent {self.name} making decision...")
            decision = self.decide(perception)

            # Act
            logger.info(f"Agent {self.name} executing action...")
            result = self.act(decision)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Learn
            experience = {
                'perception': perception,
                'decision': decision,
                'result': result,
                'success': result.get('success', False),
                'execution_time': execution_time,
                'timestamp': start_time.isoformat()
            }
            self.learn(experience)

            self.status = "idle"

            return {
                'success': True,
                'agent_id': self.agent_id,
                'agent_name': self.name,
                'result': result,
                'execution_time': execution_time,
                'timestamp': start_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Agent {self.name} encountered error: {str(e)}")
            self.status = "error"

            # Learn from failure
            self.learn({
                'success': False,
                'error': str(e),
                'timestamp': start_time.isoformat()
            })

            return {
                'success': False,
                'agent_id': self.agent_id,
                'agent_name': self.name,
                'error': str(e),
                'timestamp': start_time.isoformat()
            }

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status,
            'capabilities': self.capabilities,
            'metrics': self.performance_metrics,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'memory_size': {
                'short_term': len(self.memory.short_term),
                'long_term': len(self.memory.long_term)
            }
        }

    def communicate(self, target_agent: 'BaseAgent', message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Communicate with another agent

        Args:
            target_agent: Agent to communicate with
            message: Message to send

        Returns:
            Response from target agent
        """
        logger.info(f"Agent {self.name} communicating with {target_agent.name}")

        return {
            'from': self.agent_id,
            'to': target_agent.agent_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type"""
        return task_type in self.capabilities

    def reset(self):
        """Reset agent to initial state"""
        self.status = "idle"
        self.memory = AgentMemory()
        logger.info(f"Agent {self.name} has been reset")

