"""
GenAI Agents API
REST API endpoints for GenAI-powered autonomous agents
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import os
import threading

from .genai_route_optimizer_agent import GenAIRouteOptimizerAgent
from .genai_demand_predictor_agent import GenAIDemandPredictorAgent
from .genai_orchestrator import GenAIOrchestrator
from . import trace_bus

logger = logging.getLogger(__name__)

# Create blueprint
genai_agents_bp = Blueprint('genai_agents', __name__, url_prefix='/api/genai-agents')

# Check if GenAI is enabled
GENAI_ENABLED = os.getenv('ENABLE_GENAI_AGENTS', 'true').lower() == 'true'

# Global instances (lazy loaded)
_genai_route_optimizer = None
_genai_demand_predictor = None
_genai_orchestrator = None


def get_genai_route_optimizer():
    """Get or create GenAI route optimizer"""
    global _genai_route_optimizer

    if _genai_route_optimizer is None and GENAI_ENABLED:
        try:
            _genai_route_optimizer = GenAIRouteOptimizerAgent()
            logger.info("GenAI Route Optimizer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI Route Optimizer: {str(e)}")

    return _genai_route_optimizer


def get_genai_demand_predictor():
    """Get or create GenAI demand predictor"""
    global _genai_demand_predictor

    if _genai_demand_predictor is None and GENAI_ENABLED:
        try:
            _genai_demand_predictor = GenAIDemandPredictorAgent()
            logger.info("GenAI Demand Predictor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI Demand Predictor: {str(e)}")

    return _genai_demand_predictor


def get_genai_orchestrator():
    """Get or create GenAI orchestrator"""
    global _genai_orchestrator

    if _genai_orchestrator is None and GENAI_ENABLED:
        try:
            route_optimizer = get_genai_route_optimizer()
            demand_predictor = get_genai_demand_predictor()

            _genai_orchestrator = GenAIOrchestrator()

            if route_optimizer:
                _genai_orchestrator.register_agent('genai_route_optimizer', route_optimizer)
            if demand_predictor:
                _genai_orchestrator.register_agent('genai_demand_predictor', demand_predictor)

            logger.info("GenAI Orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI Orchestrator: {str(e)}")

    return _genai_orchestrator


@genai_agents_bp.route('/health', methods=['GET'])
def health_check():
    """Check GenAI agents system health"""

    if not GENAI_ENABLED:
        return jsonify({
            'status': 'disabled',
            'message': 'GenAI agents are disabled. Set ENABLE_GENAI_AGENTS=true in .env'
        }), 200

    try:
        # Try to initialize agents
        route_optimizer = get_genai_route_optimizer()
        demand_predictor = get_genai_demand_predictor()
        orchestrator = get_genai_orchestrator()

        agents_status = {}

        if route_optimizer:
            agents_status['route_optimizer'] = 'healthy'
        if demand_predictor:
            agents_status['demand_predictor'] = 'healthy'
        if orchestrator:
            agents_status['orchestrator'] = 'healthy'

        return jsonify({
            'status': 'healthy',
            'genai_enabled': True,
            'agents': agents_status,
            'model': 'Azure OpenAI GPT-4',
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Check Azure OpenAI credentials in .env file'
        }), 500


@genai_agents_bp.route('/status', methods=['GET'])
def get_status():
    """Get status of all GenAI agents"""

    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents are disabled'}), 400

    try:
        route_optimizer = get_genai_route_optimizer()
        demand_predictor = get_genai_demand_predictor()
        orchestrator = get_genai_orchestrator()

        agents_status = {}

        if route_optimizer:
            agents_status['genai_route_optimizer'] = route_optimizer.get_status()
        if demand_predictor:
            agents_status['genai_demand_predictor'] = demand_predictor.get_status()
        if orchestrator:
            agents_status['genai_orchestrator'] = orchestrator.get_status()

        return jsonify({
            'success': True,
            'status': {
                'system_status': 'operational',
                'genai_powered': True,
                'agents': agents_status
            },
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting GenAI agents status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _summarize_for_trace(obj, max_len: int = 220) -> str:
    """Produce a short human-readable summary of a value for the trace console"""
    try:
        text = str(obj)
        return text if len(text) <= max_len else text[:max_len] + '…'
    except Exception:
        return '<unavailable>'


def _run_genai_agent_traced(agent, environment: dict, run_id: str, explain_method_name: str):
    """
    Execute a GenAI agent's Perceive -> Decide -> Act -> Learn lifecycle in a
    background thread, emitting a trace event after each phase (including the
    real GPT-4 generated text) so the frontend can poll and render a live
    "agent thinking" stream. Since this agent calls Azure OpenAI, phases take
    real network latency — that's intentional and makes the demo feel authentic.
    """
    try:
        trace_bus.emit(run_id, 'perceive', f"{agent.name} is perceiving the environment (calling Azure OpenAI)…")
        perception = agent.perceive(environment)
        genai_analysis = perception.get('genai_analysis', {})
        trace_bus.emit(
            run_id, 'perceive', 'GPT-4 situation analysis received',
            _summarize_for_trace(genai_analysis.get('analysis') or perception)
        )

        trace_bus.emit(run_id, 'decide', f"{agent.name} is asking GPT-4 to decide on the best actions…")
        decision = agent.decide(perception)
        trace_bus.emit(
            run_id, 'decide', 'GPT-4 decision received',
            _summarize_for_trace(decision.get('natural_summary') or decision)
        )

        trace_bus.emit(run_id, 'act', f"{agent.name} is executing the recommended actions…")
        result = agent.act(decision)
        trace_bus.emit(run_id, 'act', 'Actions executed', _summarize_for_trace(result))

        trace_bus.emit(run_id, 'learn', f"{agent.name} is updating memory & confidence from this outcome…")
        experience = {
            'perception': perception,
            'decision': decision,
            'result': result,
            'success': result.get('success', False),
            'timestamp': datetime.now().isoformat()
        }
        agent.learn(experience)
        trace_bus.emit(run_id, 'learn', 'Learning complete — experience stored, metrics updated')

        # Extra GenAI-only step: ask GPT-4 to explain the decision in plain English
        explanation = ''
        try:
            if explain_method_name == 'explain_decision_naturally':
                explanation = agent.explain_decision_naturally(decision, result)
            elif explain_method_name == 'explain_forecast_naturally':
                explanation = agent.explain_forecast_naturally(result)
        except Exception as ex:
            explanation = f'(explanation unavailable: {ex})'

        if explanation:
            trace_bus.emit(run_id, 'explain', 'GPT-4 natural-language explanation', explanation)

        final_result = {
            'success': True,
            'agent_id': agent.agent_id,
            'agent_name': agent.name,
            'result': result,
            'natural_explanation': explanation,
            'timestamp': datetime.now().isoformat()
        }
        trace_bus.complete(run_id, final_result)

    except Exception as e:
        logger.error(f"Traced GenAI agent run {run_id} failed: {str(e)}")
        trace_bus.fail(run_id, str(e))


@genai_agents_bp.route('/route-optimizer/execute-traced', methods=['POST'])
def execute_genai_route_optimizer_traced():
    """
    Start a traced (streamable) execution of the GenAI route optimizer.
    Since this agent calls Azure OpenAI, the Perceive/Decide phases will
    take real network time — poll GET /api/trace/<run_id> to watch the
    live GPT-4 reasoning stream in as it's produced.
    """
    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents are disabled'}), 400

    try:
        data = request.get_json() or {}
        agent = get_genai_route_optimizer()

        if not agent:
            return jsonify({'error': 'GenAI Route optimizer not available'}), 404

        run_id = trace_bus.start_run(agent.agent_id, agent.name, 'genai_route_optimization')
        thread = threading.Thread(
            target=_run_genai_agent_traced,
            args=(agent, data, run_id, 'explain_decision_naturally'),
            daemon=True
        )
        thread.start()

        return jsonify({'success': True, 'run_id': run_id}), 202

    except Exception as e:
        logger.error(f"Error starting traced GenAI route optimizer: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@genai_agents_bp.route('/demand-predictor/execute-traced', methods=['POST'])
def execute_genai_demand_predictor_traced():
    """
    Start a traced (streamable) execution of the GenAI demand predictor.
    Poll GET /api/trace/<run_id> to watch the live GPT-4 reasoning stream.
    """
    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents are disabled'}), 400

    try:
        data = request.get_json() or {}
        agent = get_genai_demand_predictor()

        if not agent:
            return jsonify({'error': 'GenAI Demand predictor not available'}), 404

        run_id = trace_bus.start_run(agent.agent_id, agent.name, 'genai_demand_forecasting')
        thread = threading.Thread(
            target=_run_genai_agent_traced,
            args=(agent, data, run_id, 'explain_forecast_naturally'),
            daemon=True
        )
        thread.start()

        return jsonify({'success': True, 'run_id': run_id}), 202

    except Exception as e:
        logger.error(f"Error starting traced GenAI demand predictor: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@genai_agents_bp.route('/route-optimizer/execute', methods=['POST'])
def execute_genai_route_optimizer():
    """Execute GenAI route optimizer"""

    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents are disabled'}), 400

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        agent = get_genai_route_optimizer()

        if not agent:
            return jsonify({'error': 'GenAI Route optimizer not available'}), 404

        # Execute agent
        result = agent.execute_task(data)

        # Generate natural explanation
        if result.get('success') and result.get('result'):
            explanation = agent.explain_decision_naturally(
                result.get('result', {}),
                result.get('result', {})
            )
            result['natural_explanation'] = explanation

        return jsonify({
            'success': True,
            'result': result,
            'genai_powered': True,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error executing GenAI route optimizer: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_agents_bp.route('/demand-predictor/execute', methods=['POST'])
def execute_genai_demand_predictor():
    """Execute GenAI demand predictor"""

    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents are disabled'}), 400

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        agent = get_genai_demand_predictor()

        if not agent:
            return jsonify({'error': 'GenAI Demand predictor not available'}), 404

        # Execute agent
        result = agent.execute_task(data)

        # Generate natural forecast explanation
        if result.get('success') and result.get('result'):
            forecast_data = result.get('result', {})
            explanation = agent.explain_forecast_naturally(forecast_data)
            result['forecast_explanation'] = explanation

        return jsonify({
            'success': True,
            'result': result,
            'genai_powered': True,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error executing GenAI demand predictor: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_agents_bp.route('/orchestrate', methods=['POST'])
def orchestrate_genai_agents():
    """Orchestrate multiple GenAI agents for complex scenarios"""

    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents are disabled'}), 400

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        orchestrator = get_genai_orchestrator()

        if not orchestrator:
            return jsonify({'error': 'GenAI Orchestrator not available'}), 404

        # Execute orchestration
        result = orchestrator.execute_task(data)

        return jsonify({
            'success': True,
            'result': result,
            'genai_powered': True,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error orchestrating GenAI agents: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_agents_bp.route('/chat', methods=['POST'])
def chat_with_agents():
    """Natural language chat interface with GenAI agents"""

    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents are disabled'}), 400

    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message']
        conversation_history = data.get('history', [])

        orchestrator = get_genai_orchestrator()

        if not orchestrator:
            return jsonify({'error': 'GenAI Orchestrator not available'}), 404

        # Get response
        response = orchestrator.chat_interface(user_message, conversation_history)

        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in chat interface: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_agents_bp.route('/report', methods=['POST'])
def generate_genai_report():
    """Generate a report using GenAI"""

    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents are disabled'}), 400

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        report_type = data.get('report_type', 'executive')
        agent_activities = data.get('activities', [])

        orchestrator = get_genai_orchestrator()

        if not orchestrator:
            return jsonify({'error': 'GenAI Orchestrator not available'}), 404

        # Generate report
        report = orchestrator.generate_system_report(agent_activities, report_type)

        return jsonify({
            'success': True,
            'report': report,
            'report_type': report_type,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@genai_agents_bp.route('/compare', methods=['GET'])
def compare_agents():
    """
    Compare traditional vs GenAI agents capabilities
    """

    comparison = {
        'traditional_agents': {
            'type': 'Rule-based',
            'decision_making': 'Algorithmic logic',
            'explanation': 'Technical logs',
            'adaptability': 'Fixed rules',
            'interaction': 'API only',
            'strengths': [
                'Fast and predictable',
                'No external API dependency',
                'Lower cost',
                'Proven algorithms'
            ]
        },
        'genai_agents': {
            'type': 'AI-powered (Azure OpenAI)',
            'decision_making': 'Natural language reasoning',
            'explanation': 'Human-readable explanations',
            'adaptability': 'Context-aware',
            'interaction': 'Conversational + API',
            'strengths': [
                'Natural language explanations',
                'Context-aware decisions',
                'Novel situation handling',
                'Conversational interface',
                'Report generation',
                'Root cause analysis'
            ]
        },
        'comparison_matrix': {
            'speed': {
                'traditional': 'Very Fast (<100ms)',
                'genai': 'Fast (1-3 seconds)'
            },
            'cost': {
                'traditional': 'Very Low (compute only)',
                'genai': 'Moderate (API calls)'
            },
            'explainability': {
                'traditional': 'Technical',
                'genai': 'Natural language'
            },
            'adaptability': {
                'traditional': 'Fixed rules',
                'genai': 'Context-aware'
            },
            'user_experience': {
                'traditional': 'Technical expertise needed',
                'genai': 'Conversational, accessible'
            }
        },
        'recommendation': 'Use both! Traditional for speed-critical operations, GenAI for complex decisions and user interaction.'
    }

    return jsonify(comparison), 200


# ============================================================================
# Self-Learning API Endpoints
# ============================================================================

@genai_agents_bp.route('/route-optimizer/record-outcome', methods=['POST'])
def record_route_outcome():
    """
    Record the actual outcome of a routing decision for learning

    Body:
    {
        "actual_time_saving": 15,  // minutes
        "actual_cost_saving": 25.50,  // dollars
        "delivery_success_rate": 0.95,  // 0-1
        "customer_satisfaction": 4.2,  // 0-5
        "issues_encountered": ["minor_delay_zone_a"]
    }
    """
    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents disabled'}), 503

    try:
        optimizer = get_genai_route_optimizer()
        if not optimizer:
            return jsonify({'error': 'Route optimizer not available'}), 503

        outcome_data = request.json

        # Validate required fields
        if 'actual_time_saving' not in outcome_data:
            outcome_data['actual_time_saving'] = 0
        if 'actual_cost_saving' not in outcome_data:
            outcome_data['actual_cost_saving'] = 0.0
        if 'delivery_success_rate' not in outcome_data:
            outcome_data['delivery_success_rate'] = 1.0
        if 'customer_satisfaction' not in outcome_data:
            outcome_data['customer_satisfaction'] = 4.0
        if 'issues_encountered' not in outcome_data:
            outcome_data['issues_encountered'] = []

        success = optimizer.record_outcome(outcome_data)

        if success:
            return jsonify({
                'success': True,
                'message': 'Outcome recorded for learning',
                'learning_status': 'processing'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No active decision to record outcome for'
            }), 400

    except Exception as e:
        logger.error(f"Error recording outcome: {str(e)}")
        return jsonify({'error': str(e)}), 500


@genai_agents_bp.route('/route-optimizer/learning-insights', methods=['GET'])
def get_learning_insights():
    """
    Get insights from the self-learning system

    Returns statistics, patterns, and learning progress
    """
    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents disabled'}), 503

    try:
        optimizer = get_genai_route_optimizer()
        if not optimizer:
            return jsonify({'error': 'Route optimizer not available'}), 503

        insights = optimizer.get_learning_insights()

        return jsonify({
            'success': True,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning insights: {str(e)}")
        return jsonify({'error': str(e)}), 500


@genai_agents_bp.route('/learning/statistics', methods=['GET'])
def get_learning_statistics():
    """
    Get detailed learning statistics for the route optimizer
    """
    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents disabled'}), 503

    try:
        optimizer = get_genai_route_optimizer()
        if not optimizer:
            return jsonify({'error': 'Route optimizer not available'}), 503

        stats = optimizer.learning_engine.get_learning_statistics()

        return jsonify({
            'success': True,
            'statistics': stats,
            'learning_enabled': True,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@genai_agents_bp.route('/learning/patterns', methods=['GET'])
def get_learned_patterns():
    """
    Get learned patterns with human-readable descriptions

    Query params:
    - limit: Number of patterns to return (default: 10)
    """
    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents disabled'}), 503

    try:
        optimizer = get_genai_route_optimizer()
        if not optimizer:
            return jsonify({'error': 'Route optimizer not available'}), 503

        limit = request.args.get('limit', 10, type=int)
        patterns = optimizer.learning_engine.get_pattern_insights(limit=limit)

        return jsonify({
            'success': True,
            'patterns': patterns,
            'count': len(patterns),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting patterns: {str(e)}")
        return jsonify({'error': str(e)}), 500


@genai_agents_bp.route('/learning/simulate-outcome', methods=['POST'])
def simulate_learning_outcome():
    """
    Simulate a learning outcome for demonstration purposes

    Body:
    {
        "scenario": "high_traffic_reroute",  // Optional scenario type
        "success": true  // Whether the simulated outcome was successful
    }
    """
    if not GENAI_ENABLED:
        return jsonify({'error': 'GenAI agents disabled'}), 503

    try:
        optimizer = get_genai_route_optimizer()
        if not optimizer:
            return jsonify({'error': 'Route optimizer not available'}), 503

        data = request.json or {}
        is_success = data.get('success', True)

        # Create simulated outcome
        import random

        if is_success:
            outcome_data = {
                'actual_time_saving': random.randint(10, 20),
                'actual_cost_saving': round(random.uniform(15.0, 35.0), 2),
                'delivery_success_rate': random.uniform(0.9, 1.0),
                'customer_satisfaction': random.uniform(4.0, 5.0),
                'issues_encountered': []
            }
        else:
            outcome_data = {
                'actual_time_saving': random.randint(-5, 5),
                'actual_cost_saving': round(random.uniform(-10.0, 5.0), 2),
                'delivery_success_rate': random.uniform(0.7, 0.9),
                'customer_satisfaction': random.uniform(3.0, 4.0),
                'issues_encountered': ['traffic_worse_than_expected']
            }

        success = optimizer.record_outcome(outcome_data)

        return jsonify({
            'success': True,
            'message': 'Simulated outcome recorded',
            'outcome': outcome_data,
            'learning_triggered': success
        }), 200

    except Exception as e:
        logger.error(f"Error simulating outcome: {str(e)}")
        return jsonify({'error': str(e)}), 500

