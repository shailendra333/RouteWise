"""
Advanced Learning API Endpoints - Phase 2 & 3
REST API for multi-objective optimization, seasonal patterns, and predictive intelligence
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from .advanced_learning_engine import AdvancedLearningEngine

logger = logging.getLogger(__name__)

# Create blueprint
advanced_learning_bp = Blueprint('advanced_learning', __name__, url_prefix='/api/advanced-learning')

# Global instance
_advanced_engine = None


def get_advanced_engine():
    """Get or create advanced learning engine"""
    global _advanced_engine

    if _advanced_engine is None:
        try:
            _advanced_engine = AdvancedLearningEngine()
            logger.info("Advanced Learning Engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Advanced Learning Engine: {str(e)}")

    return _advanced_engine


# ============================================================================
# PHASE 2: MULTI-OBJECTIVE OPTIMIZATION
# ============================================================================

@advanced_learning_bp.route('/multi-objective/optimize', methods=['POST'])
def multi_objective_optimize():
    """
    Optimize for multiple objectives simultaneously

    Body:
    {
        "decision_type": "reroute",
        "constraints": {...}
    }
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        data = request.json or {}
        decision_type = data.get('decision_type', 'optimize')
        constraints = data.get('constraints')

        result = engine.optimize_multi_objective(decision_type, constraints)

        return jsonify({
            'success': True,
            'results': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in multi-objective optimization: {str(e)}")
        return jsonify({'error': str(e)}), 500


@advanced_learning_bp.route('/multi-objective/pareto', methods=['GET'])
def get_pareto_optimal():
    """
    Get Pareto-optimal solutions for a decision type

    Query params:
    - decision_type: Type of decision
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        decision_type = request.args.get('decision_type', 'optimize')

        result = engine.optimize_multi_objective(decision_type)
        pareto = result.get('pareto_optimal', [])

        return jsonify({
            'success': True,
            'pareto_optimal_solutions': pareto,
            'count': len(pareto),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting Pareto optimal: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PHASE 2: SEASONAL PATTERN DETECTION
# ============================================================================

@advanced_learning_bp.route('/seasonal/detect', methods=['GET'])
def detect_seasonal_patterns():
    """
    Detect seasonal patterns in routing decisions

    Query params:
    - decision_type: Optional filter
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        decision_type = request.args.get('decision_type')

        result = engine.detect_seasonal_patterns(decision_type)

        return jsonify({
            'success': True,
            'seasonal_patterns': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error detecting seasonal patterns: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PHASE 2: GEOGRAPHIC CLUSTERING
# ============================================================================

@advanced_learning_bp.route('/geographic/clusters', methods=['GET'])
def get_geographic_clusters():
    """
    Get geographic clusters of routing patterns

    Query params:
    - decision_type: Optional filter
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        decision_type = request.args.get('decision_type')

        result = engine.cluster_geographic_patterns(decision_type)

        return jsonify({
            'success': True,
            'geographic_clusters': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting geographic clusters: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PHASE 2: CROSS-AGENT PATTERN SHARING
# ============================================================================

@advanced_learning_bp.route('/patterns/share', methods=['POST'])
def share_patterns():
    """
    Share patterns between agents

    Body:
    {
        "source_agent_id": "genai_route_optimizer_001",
        "target_agent_id": "traditional_route_optimizer_001",
        "pattern_types": ["reroute", "optimize"]  // optional
    }
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        data = request.json or {}
        source_agent = data.get('source_agent_id')
        target_agent = data.get('target_agent_id')
        pattern_types = data.get('pattern_types')

        if not source_agent or not target_agent:
            return jsonify({'error': 'source_agent_id and target_agent_id required'}), 400

        result = engine.share_patterns_between_agents(
            source_agent,
            target_agent,
            pattern_types
        )

        return jsonify({
            'success': True,
            'sharing_result': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error sharing patterns: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PHASE 3: PROACTIVE RECOMMENDATIONS
# ============================================================================

@advanced_learning_bp.route('/recommendations/proactive', methods=['POST'])
def get_proactive_recommendations():
    """
    Get proactive pattern recommendations for a situation

    Body:
    {
        "current_situation": {
            "traffic_level": "high",
            "hour": 17,
            "day_of_week": "Friday",
            "weather": "clear"
        },
        "top_k": 3
    }
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        data = request.json or {}
        situation = data.get('current_situation', {})
        top_k = data.get('top_k', 3)

        recommendations = engine.recommend_patterns_for_situation(situation, top_k)

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PHASE 3: WHAT-IF SIMULATION
# ============================================================================

@advanced_learning_bp.route('/whatif/simulate', methods=['POST'])
def simulate_whatif():
    """
    Simulate outcomes of a hypothetical decision

    Body:
    {
        "scenario": {
            "decision_type": "reroute",
            "traffic_level": "high",
            "num_routes": 10
        },
        "pattern_id": 42  // optional specific pattern
    }
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        data = request.json or {}
        scenario = data.get('scenario', {})
        pattern_id = data.get('pattern_id')

        result = engine.simulate_what_if_scenario(scenario, pattern_id)

        return jsonify({
            'success': True,
            'simulation': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in what-if simulation: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PHASE 3: AUTOMATIC PARAMETER TUNING
# ============================================================================

@advanced_learning_bp.route('/parameters/auto-tune', methods=['POST'])
def auto_tune_parameters():
    """
    Automatically tune learning parameters

    Body:
    {
        "target_metric": "quality"  // or "accuracy", "improvement"
    }
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        data = request.json or {}
        target_metric = data.get('target_metric', 'quality')

        result = engine.auto_tune_parameters(target_metric)

        return jsonify({
            'success': True,
            'tuning_result': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in auto-tuning: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PHASE 3: FEDERATED LEARNING
# ============================================================================

@advanced_learning_bp.route('/federated/aggregate', methods=['POST'])
def aggregate_federated():
    """
    Aggregate patterns from external systems

    Body:
    {
        "external_patterns": [
            {
                "pattern_type": "reroute",
                "conditions": {...},
                "confidence": 0.85,
                "observations": 20,
                "avg_improvement": 15.5
            }
        ]
    }
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        data = request.json or {}
        external_patterns = data.get('external_patterns', [])

        if not external_patterns:
            return jsonify({'error': 'external_patterns required'}), 400

        result = engine.aggregate_federated_patterns(external_patterns)

        return jsonify({
            'success': True,
            'aggregation_result': result,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in federated aggregation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@advanced_learning_bp.route('/federated/export', methods=['GET'])
def export_federated():
    """
    Export patterns for federated sharing

    Query params:
    - min_confidence: Minimum confidence threshold (default: 0.7)
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        min_confidence = request.args.get('min_confidence', 0.7, type=float)

        patterns = engine.export_patterns_for_federation(min_confidence)

        return jsonify({
            'success': True,
            'exported_patterns': patterns,
            'count': len(patterns),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error exporting patterns: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# DASHBOARD & OVERVIEW
# ============================================================================

@advanced_learning_bp.route('/overview', methods=['GET'])
def get_advanced_overview():
    """
    Get overview of all advanced learning features
    """
    try:
        engine = get_advanced_engine()
        if not engine:
            return jsonify({'error': 'Advanced learning engine not available'}), 503

        # Get basic stats
        conn = engine._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM learned_patterns')
        total_patterns = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM route_decisions WHERE outcome_measured = 1')
        total_decisions = cursor.fetchone()[0]

        conn.close()

        overview = {
            'phase_2_features': {
                'multi_objective_optimization': 'Available',
                'seasonal_pattern_detection': 'Available',
                'geographic_clustering': 'Available',
                'cross_agent_sharing': 'Available'
            },
            'phase_3_features': {
                'proactive_recommendations': 'Available',
                'whatif_simulation': 'Available',
                'auto_parameter_tuning': 'Available',
                'federated_learning': 'Available'
            },
            'statistics': {
                'total_patterns': total_patterns,
                'total_decisions_analyzed': total_decisions,
                'engine_status': 'operational'
            },
            'capabilities': [
                'Multi-objective optimization (time + cost + satisfaction)',
                'Seasonal and temporal pattern detection',
                'Geographic clustering of routing patterns',
                'Cross-agent pattern knowledge sharing',
                'Proactive pattern recommendations',
                'What-if scenario simulation',
                'Automatic parameter tuning',
                'Federated learning across systems'
            ]
        }

        return jsonify({
            'success': True,
            'overview': overview,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting overview: {str(e)}")
        return jsonify({'error': str(e)}), 500

