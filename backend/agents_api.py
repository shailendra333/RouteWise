"""
AI Agents API Endpoints
Flask routes for interacting with AI agents
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from ai_agents.orchestrator_agent import OrchestratorAgent
from ai_agents.route_optimizer_agent import RouteOptimizerAgent
from ai_agents.demand_predictor_agent import DemandPredictorAgent

logger = logging.getLogger(__name__)

# Create Blueprint
agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')

# Initialize orchestrator (singleton)
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = OrchestratorAgent()
    return orchestrator


@agents_bp.route('/health', methods=['GET'])
def agents_health():
    """Check health of AI agents system"""
    try:
        orch = get_orchestrator()
        summary = orch.get_agent_summary()

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'agents': summary
        }), 200

    except Exception as e:
        logger.error(f"Error checking agent health: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@agents_bp.route('/orchestrate', methods=['POST'])
def orchestrate_agents():
    """
    Orchestrate multiple agents to handle complex tasks

    Request body:
    {
        "current_routes": [...],
        "historical_orders": [...],
        "traffic_data": {...},
        "external_factors": {...}
    }
    """
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        orch = get_orchestrator()

        # Execute orchestration
        result = orch.execute_task(data)

        return jsonify({
            'success': True,
            'orchestration_result': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in orchestration: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/route-optimizer/execute', methods=['POST'])
def execute_route_optimizer():
    """
    Execute route optimizer agent

    Request body:
    {
        "current_routes": [...],
        "traffic_data": {...},
        "delivery_status": {...}
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get agent from orchestrator
        orch = get_orchestrator()
        agent = orch.agents.get('route_optimizer')

        if not agent:
            return jsonify({'error': 'Route optimizer agent not found'}), 404

        # Execute agent
        result = agent.execute_task(data)

        # Log action
        log_agent_action(
            agent.agent_id,
            agent.name,
            'route_optimization',
            result,
            result.get('success', False),
            result.get('execution_time', 0)
        )

        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error executing route optimizer: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/demand-predictor/execute', methods=['POST'])
def execute_demand_predictor():
    """
    Execute demand predictor agent

    Request body:
    {
        "historical_orders": [...],
        "current_capacity": {...},
        "external_factors": {...}
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get agent from orchestrator
        orch = get_orchestrator()
        agent = orch.agents.get('demand_predictor')

        if not agent:
            return jsonify({'error': 'Demand predictor agent not found'}), 404

        # Execute agent
        result = agent.execute_task(data)

        # Log action
        log_agent_action(
            agent.agent_id,
            agent.name,
            'demand_forecasting',
            result,
            result.get('success', False),
            result.get('execution_time', 0)
        )

        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error executing demand predictor: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/status', methods=['GET'])
def get_agents_status():
    """Get status of all agents"""
    try:
        orch = get_orchestrator()

        status = {
            'orchestrator': orch.get_status(),
            'agents': {}
        }

        for agent_name, agent in orch.agents.items():
            status['agents'][agent_name] = agent.get_status()

        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/agent/<agent_id>/metrics', methods=['GET'])
def get_agent_metrics(agent_id):
    """Get performance metrics for specific agent"""
    try:
        orch = get_orchestrator()

        # Find agent
        agent = None
        for agent_name, a in orch.agents.items():
            if a.agent_id == agent_id or agent_name == agent_id:
                agent = a
                break

        if not agent:
            return jsonify({'error': f'Agent {agent_id} not found'}), 404

        metrics = agent.performance_metrics
        status = agent.get_status()

        return jsonify({
            'success': True,
            'agent_id': agent.agent_id,
            'agent_name': agent.name,
            'metrics': metrics,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting agent metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/agent/<agent_id>/memory', methods=['GET'])
def get_agent_memory(agent_id):
    """Get memory/experiences of specific agent"""
    try:
        orch = get_orchestrator()

        # Find agent
        agent = None
        for agent_name, a in orch.agents.items():
            if a.agent_id == agent_id or agent_name == agent_id:
                agent = a
                break

        if not agent:
            return jsonify({'error': f'Agent {agent_id} not found'}), 404

        # Get recent experiences
        limit = request.args.get('limit', 10, type=int)
        recent_experiences = agent.memory.short_term[-limit:]

        return jsonify({
            'success': True,
            'agent_id': agent.agent_id,
            'agent_name': agent.name,
            'recent_experiences': recent_experiences,
            'memory_stats': {
                'short_term_size': len(agent.memory.short_term),
                'long_term_patterns': len(agent.memory.long_term)
            },
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting agent memory: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/simulate', methods=['POST'])
def simulate_scenario():
    """
    Simulate a logistics scenario with AI agents

    Request body:
    {
        "scenario": "high_demand" | "traffic_congestion" | "emergency",
        "parameters": {...}
    }
    """
    try:
        data = request.get_json()

        if not data or 'scenario' not in data:
            return jsonify({'error': 'Scenario type required'}), 400

        scenario = data['scenario']
        parameters = data.get('parameters', {})

        # Create simulation environment
        environment = create_simulation_environment(scenario, parameters)

        # Execute orchestrator
        orch = get_orchestrator()
        result = orch.execute_task(environment)

        return jsonify({
            'success': True,
            'scenario': scenario,
            'simulation_result': result,
            'insights': generate_simulation_insights(result),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in simulation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_simulation_environment(scenario: str, parameters: dict) -> dict:
    """Create simulated environment based on scenario"""
    base_env = {
        'current_routes': [],
        'historical_orders': [],
        'traffic_data': {},
        'external_factors': {},
        'current_capacity': {
            'vehicles': parameters.get('vehicles', 10),
            'drivers': parameters.get('drivers', 10),
            'deliveries_per_vehicle': 30
        }
    }

    if scenario == 'high_demand':
        # Simulate high demand scenario
        base_env['historical_orders'] = [{'id': i} for i in range(500)]
        base_env['pending_orders'] = [{'id': i} for i in range(100)]

    elif scenario == 'traffic_congestion':
        # Simulate traffic congestion
        base_env['current_routes'] = [
            {
                'route_id': i,
                'deliveries': [{'id': j} for j in range(10)],
                'efficiency': 0.6
            }
            for i in range(5)
        ]
        base_env['traffic_data'] = {'congestion_level': 'high'}

    elif scenario == 'emergency':
        # Simulate emergency orders
        base_env['emergency_orders'] = [
            {'id': i, 'priority': 'urgent'} for i in range(10)
        ]

    return base_env


def generate_simulation_insights(result: dict) -> dict:
    """Generate insights from simulation results"""
    insights = {
        'execution_time': result.get('execution_time', 0),
        'agents_activated': len(result.get('result', {}).get('agent_results', {})),
        'recommendations': []
    }

    # Analyze agent results
    agent_results = result.get('result', {}).get('agent_results', {})

    for agent_name, agent_result in agent_results.items():
        if agent_result.get('success'):
            improvements = agent_result.get('result', {}).get('improvements', {})
            if improvements:
                insights['recommendations'].append({
                    'agent': agent_name,
                    'impact': improvements
                })

    return insights


def log_agent_action(agent_id: str, agent_name: str, action: str,
                     result: dict, success: bool, execution_time: float):
    """Log agent action to database"""
    import sqlite3
    try:
        conn = sqlite3.connect('smart_logistics.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO agent_logs 
            (agent_id, agent_name, action, result, success, execution_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (agent_id, agent_name, action, str(result), success, execution_time))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log agent action: {str(e)}")


@agents_bp.route('/activity', methods=['GET'])
def get_agent_activity():
    """Get recent agent activity logs"""
    try:
        import sqlite3
        limit = request.args.get('limit', 50, type=int)

        conn = sqlite3.connect('smart_logistics.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT agent_id, agent_name, action, result, success, 
                   execution_time, timestamp
            FROM agent_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        logs = []
        for row in cursor.fetchall():
            logs.append({
                'agent_id': row[0],
                'agent_name': row[1],
                'action': row[2],
                'result': row[3],
                'success': bool(row[4]),
                'execution_time': row[5],
                'timestamp': row[6]
            })

        conn.close()

        return jsonify({
            'success': True,
            'count': len(logs),
            'logs': logs,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting agent activity: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/statistics', methods=['GET'])
def get_agent_statistics():
    """Get agent performance statistics"""
    try:
        import sqlite3

        conn = sqlite3.connect('smart_logistics.db')
        cursor = conn.cursor()

        # Total actions per agent
        cursor.execute('''
            SELECT agent_name, 
                   COUNT(*) as total_actions,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_actions,
                   AVG(execution_time) as avg_execution_time
            FROM agent_logs
            GROUP BY agent_name
        ''')

        stats = {}
        for row in cursor.fetchall():
            agent_name = row[0]
            stats[agent_name] = {
                'total_actions': row[1],
                'successful_actions': row[2],
                'success_rate': round(row[2] / row[1] * 100, 2) if row[1] > 0 else 0,
                'avg_execution_time': round(row[3], 2) if row[3] else 0
            }

        # Actions over time (last 24 hours by hour)
        cursor.execute('''
            SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                   COUNT(*) as action_count
            FROM agent_logs
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY hour
            ORDER BY hour
        ''')

        timeline = []
        for row in cursor.fetchall():
            timeline.append({
                'hour': row[0],
                'count': row[1]
            })

        conn.close()

        return jsonify({
            'success': True,
            'statistics': stats,
            'timeline': timeline,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting agent statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Export blueprint
__all__ = ['agents_bp']

