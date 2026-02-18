"""
Self-Learning Engine for Route Optimizer
Tracks decisions, measures outcomes, identifies patterns, and enables continuous improvement
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)


class LearningEngine:
    """
    Core learning engine that enables the route optimizer to learn from experience
    """

    def __init__(self, database_path: str = 'smart_logistics.db'):
        self.database_path = database_path
        self.min_observations = 3  # Minimum observations to form a pattern
        self.pattern_confidence_threshold = 0.6

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.database_path)

    def record_decision(
        self,
        agent_id: str,
        decision_type: str,
        decision_data: Dict[str, Any]
    ) -> int:
        """
        Record a routing decision for learning

        Returns:
            decision_id for tracking outcomes
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO route_decisions (
                    agent_id, decision_type, num_active_routes,
                    traffic_conditions, weather_conditions,
                    genai_reasoning, confidence_score,
                    predicted_time_saving, predicted_cost_saving,
                    routes_affected
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_id,
                decision_type,
                decision_data.get('num_active_routes', 0),
                json.dumps(decision_data.get('traffic_conditions', {})),
                json.dumps(decision_data.get('weather_conditions', {})),
                decision_data.get('genai_reasoning', ''),
                decision_data.get('confidence_score', 0.5),
                decision_data.get('predicted_time_saving', 0),
                decision_data.get('predicted_cost_saving', 0.0),
                json.dumps(decision_data.get('routes_affected', []))
            ))

            decision_id = cursor.lastrowid
            conn.commit()

            logger.info(f"✅ Recorded decision {decision_id} for learning")
            return decision_id

        except Exception as e:
            logger.error(f"Error recording decision: {str(e)}")
            conn.rollback()
            return -1
        finally:
            conn.close()

    def record_outcome(
        self,
        decision_id: int,
        outcome_data: Dict[str, Any]
    ) -> bool:
        """
        Record the actual outcome of a routing decision
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO route_outcomes (
                    decision_id, actual_time_saving, actual_cost_saving,
                    delivery_success_rate, customer_satisfaction,
                    issues_encountered, data_quality
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision_id,
                outcome_data.get('actual_time_saving', 0),
                outcome_data.get('actual_cost_saving', 0.0),
                outcome_data.get('delivery_success_rate', 1.0),
                outcome_data.get('customer_satisfaction', 4.0),
                json.dumps(outcome_data.get('issues_encountered', [])),
                outcome_data.get('data_quality', 1.0)
            ))

            # Mark decision as having outcome measured
            cursor.execute('''
                UPDATE route_decisions 
                SET outcome_measured = 1
                WHERE decision_id = ?
            ''', (decision_id,))

            conn.commit()

            # Calculate decision quality score
            self._calculate_decision_quality(decision_id)

            # Trigger pattern learning
            self._process_learning(decision_id)

            logger.info(f"✅ Recorded outcome for decision {decision_id}")
            return True

        except Exception as e:
            logger.error(f"Error recording outcome: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def _calculate_decision_quality(self, decision_id: int):
        """
        Calculate quality score for a decision based on predicted vs actual
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT 
                    d.predicted_time_saving,
                    d.predicted_cost_saving,
                    d.confidence_score,
                    o.actual_time_saving,
                    o.actual_cost_saving,
                    o.delivery_success_rate,
                    o.customer_satisfaction
                FROM route_decisions d
                JOIN route_outcomes o ON d.decision_id = o.decision_id
                WHERE d.decision_id = ?
            ''', (decision_id,))

            row = cursor.fetchone()
            if not row:
                return

            pred_time, pred_cost, confidence, act_time, act_cost, success_rate, satisfaction = row

            # Calculate accuracy scores (0-1)
            time_accuracy = 1.0 - min(abs(pred_time - act_time) / max(abs(pred_time) + 1, 1), 1.0)
            cost_accuracy = 1.0 - min(abs(pred_cost - act_cost) / max(abs(pred_cost) + 1, 1), 1.0)

            # Overall quality score
            quality_score = (
                0.3 * time_accuracy +
                0.3 * cost_accuracy +
                0.2 * success_rate +
                0.2 * (satisfaction / 5.0)
            )

            cursor.execute('''
                UPDATE route_decisions 
                SET decision_quality_score = ?
                WHERE decision_id = ?
            ''', (quality_score, decision_id))

            conn.commit()
            logger.info(f"📊 Decision {decision_id} quality score: {quality_score:.2f}")

        except Exception as e:
            logger.error(f"Error calculating quality: {str(e)}")
        finally:
            conn.close()

    def _process_learning(self, decision_id: int):
        """
        Process a decision outcome for pattern learning
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get decision and outcome data
            cursor.execute('''
                SELECT 
                    d.decision_type,
                    d.traffic_conditions,
                    d.weather_conditions,
                    d.confidence_score,
                    d.decision_quality_score,
                    o.actual_time_saving,
                    o.actual_cost_saving
                FROM route_decisions d
                JOIN route_outcomes o ON d.decision_id = o.decision_id
                WHERE d.decision_id = ?
            ''', (decision_id,))

            row = cursor.fetchone()
            if not row:
                return

            decision_type, traffic_json, weather_json, confidence, quality, time_saving, cost_saving = row

            # Parse conditions
            traffic_conditions = json.loads(traffic_json) if traffic_json else {}
            weather_conditions = json.loads(weather_json) if weather_json else {}

            # Create pattern signature
            pattern_signature = self._create_pattern_signature(
                decision_type, traffic_conditions, weather_conditions
            )

            # Check if pattern exists
            cursor.execute('''
                SELECT pattern_id, times_observed, success_count, failure_count, avg_improvement
                FROM learned_patterns
                WHERE pattern_type = ? AND conditions = ?
            ''', (decision_type, json.dumps(pattern_signature)))

            existing_pattern = cursor.fetchone()

            is_success = quality >= 0.7  # Success threshold
            improvement = max(time_saving, 0)

            if existing_pattern:
                # Update existing pattern
                pattern_id, times_obs, success_cnt, failure_cnt, avg_imp = existing_pattern

                new_times = times_obs + 1
                new_success = success_cnt + (1 if is_success else 0)
                new_failure = failure_cnt + (0 if is_success else 1)
                new_avg_imp = (avg_imp * times_obs + improvement) / new_times
                new_confidence = new_success / new_times

                cursor.execute('''
                    UPDATE learned_patterns
                    SET times_observed = ?,
                        success_count = ?,
                        failure_count = ?,
                        avg_improvement = ?,
                        confidence = ?,
                        last_updated = ?,
                        last_successful_use = ?
                    WHERE pattern_id = ?
                ''', (
                    new_times, new_success, new_failure, new_avg_imp, new_confidence,
                    datetime.now().isoformat(),
                    datetime.now().isoformat() if is_success else existing_pattern[4],
                    pattern_id
                ))

                logger.info(f"📚 Updated pattern {pattern_id}: {new_success}/{new_times} success rate")

            else:
                # Create new pattern
                cursor.execute('''
                    INSERT INTO learned_patterns (
                        pattern_type, conditions, recommended_action,
                        confidence, times_observed, success_count,
                        failure_count, avg_improvement
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    decision_type,
                    json.dumps(pattern_signature),
                    decision_type,  # Recommended action is the decision type
                    1.0 if is_success else 0.0,
                    1,
                    1 if is_success else 0,
                    0 if is_success else 1,
                    improvement
                ))

                pattern_id = cursor.lastrowid
                logger.info(f"🆕 Created new pattern {pattern_id} for {decision_type}")

            # Mark decision as learning processed
            cursor.execute('''
                UPDATE route_decisions
                SET learning_processed = 1
                WHERE decision_id = ?
            ''', (decision_id,))

            conn.commit()

        except Exception as e:
            logger.error(f"Error processing learning: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def _create_pattern_signature(
        self,
        decision_type: str,
        traffic_conditions: Dict,
        weather_conditions: Dict
    ) -> Dict:
        """
        Create a pattern signature for matching similar situations
        """
        signature = {
            'decision_type': decision_type
        }

        # Simplify traffic conditions to categories
        if traffic_conditions:
            avg_traffic = np.mean([v for v in traffic_conditions.values() if isinstance(v, (int, float))])
            if avg_traffic > 0.7:
                signature['traffic_level'] = 'high'
            elif avg_traffic > 0.4:
                signature['traffic_level'] = 'medium'
            else:
                signature['traffic_level'] = 'low'

        # Simplify weather conditions
        if weather_conditions:
            if 'condition' in weather_conditions:
                signature['weather'] = weather_conditions['condition']
            elif 'rain' in str(weather_conditions).lower():
                signature['weather'] = 'rain'
            else:
                signature['weather'] = 'clear'

        return signature

    def query_learned_patterns(
        self,
        decision_type: str,
        traffic_conditions: Dict = None,
        weather_conditions: Dict = None
    ) -> List[Dict[str, Any]]:
        """
        Query learned patterns for similar situations
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get all patterns of this type
            cursor.execute('''
                SELECT 
                    pattern_id, pattern_type, conditions, recommended_action,
                    confidence, times_observed, success_count, failure_count,
                    avg_improvement, last_successful_use
                FROM learned_patterns
                WHERE pattern_type = ? AND confidence >= ?
                ORDER BY confidence DESC, times_observed DESC
                LIMIT 10
            ''', (decision_type, self.pattern_confidence_threshold))

            patterns = []
            for row in cursor.fetchall():
                pattern = {
                    'pattern_id': row[0],
                    'pattern_type': row[1],
                    'conditions': json.loads(row[2]),
                    'recommended_action': row[3],
                    'confidence': row[4],
                    'times_observed': row[5],
                    'success_count': row[6],
                    'failure_count': row[7],
                    'avg_improvement': row[8],
                    'last_successful_use': row[9]
                }
                patterns.append(pattern)

            logger.info(f"🔍 Found {len(patterns)} learned patterns for {decision_type}")
            return patterns

        except Exception as e:
            logger.error(f"Error querying patterns: {str(e)}")
            return []
        finally:
            conn.close()

    def get_learning_statistics(self) -> Dict[str, Any]:
        """
        Get overall learning statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            stats = {}

            # Total decisions
            cursor.execute('SELECT COUNT(*) FROM route_decisions')
            stats['total_decisions'] = cursor.fetchone()[0]

            # Decisions with outcomes
            cursor.execute('SELECT COUNT(*) FROM route_decisions WHERE outcome_measured = 1')
            stats['decisions_with_outcomes'] = cursor.fetchone()[0]

            # Average quality score
            cursor.execute('''
                SELECT AVG(decision_quality_score) 
                FROM route_decisions 
                WHERE decision_quality_score IS NOT NULL
            ''')
            result = cursor.fetchone()[0]
            stats['avg_decision_quality'] = round(result, 3) if result else 0.0

            # Prediction accuracy (within 20% of actual)
            cursor.execute('''
                SELECT COUNT(*) FROM route_decisions d
                JOIN route_outcomes o ON d.decision_id = o.decision_id
                WHERE ABS(d.predicted_time_saving - o.actual_time_saving) <= ABS(d.predicted_time_saving * 0.2)
            ''')
            accurate_predictions = cursor.fetchone()[0]
            stats['prediction_accuracy'] = (
                round(accurate_predictions / max(stats['decisions_with_outcomes'], 1), 3)
            )

            # Total patterns learned
            cursor.execute('SELECT COUNT(*) FROM learned_patterns')
            stats['total_patterns'] = cursor.fetchone()[0]

            # High confidence patterns
            cursor.execute('SELECT COUNT(*) FROM learned_patterns WHERE confidence >= 0.8')
            stats['high_confidence_patterns'] = cursor.fetchone()[0]

            # Average improvement from decisions
            cursor.execute('SELECT AVG(actual_time_saving) FROM route_outcomes')
            result = cursor.fetchone()[0]
            stats['avg_time_savings'] = round(result, 2) if result else 0.0

            cursor.execute('SELECT AVG(actual_cost_saving) FROM route_outcomes')
            result = cursor.fetchone()[0]
            stats['avg_cost_savings'] = round(result, 2) if result else 0.0

            # Recent performance (last 7 days)
            cursor.execute('''
                SELECT AVG(decision_quality_score)
                FROM route_decisions
                WHERE timestamp >= datetime('now', '-7 days')
                AND decision_quality_score IS NOT NULL
            ''')
            result = cursor.fetchone()[0]
            stats['recent_quality_score'] = round(result, 3) if result else 0.0

            # Calculate improvement trend
            if stats['decisions_with_outcomes'] >= 10:
                # Compare first 5 vs last 5 decisions
                cursor.execute('''
                    SELECT AVG(decision_quality_score) FROM (
                        SELECT decision_quality_score 
                        FROM route_decisions 
                        WHERE decision_quality_score IS NOT NULL
                        ORDER BY decision_id ASC
                        LIMIT 5
                    )
                ''')
                early_quality = cursor.fetchone()[0] or 0.5

                cursor.execute('''
                    SELECT AVG(decision_quality_score) FROM (
                        SELECT decision_quality_score 
                        FROM route_decisions 
                        WHERE decision_quality_score IS NOT NULL
                        ORDER BY decision_id DESC
                        LIMIT 5
                    )
                ''')
                recent_quality = cursor.fetchone()[0] or 0.5

                stats['quality_improvement'] = round((recent_quality - early_quality) * 100, 1)
            else:
                stats['quality_improvement'] = 0.0

            logger.info(f"📊 Learning statistics: {stats['total_patterns']} patterns, "
                       f"{stats['prediction_accuracy']*100:.1f}% accuracy")

            return stats

        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
        finally:
            conn.close()

    def update_weekly_metrics(self):
        """
        Calculate and store weekly learning metrics
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            week_start = datetime.now() - timedelta(days=7)
            week_start_str = week_start.strftime('%Y-%m-%d')

            # Get metrics for the past week
            cursor.execute('''
                SELECT 
                    AVG(d.decision_quality_score) as avg_quality,
                    COUNT(*) as total_decisions,
                    SUM(CASE WHEN d.decision_quality_score >= 0.7 THEN 1 ELSE 0 END) as successful
                FROM route_decisions d
                WHERE d.timestamp >= ?
                AND d.decision_quality_score IS NOT NULL
            ''', (week_start_str,))

            row = cursor.fetchone()
            if row and row[1] > 0:
                avg_quality, total_dec, successful = row
                success_rate = successful / total_dec

                # Get patterns stats
                cursor.execute('''
                    SELECT COUNT(*) FROM learned_patterns
                    WHERE created_at >= ?
                ''', (week_start_str,))
                patterns_discovered = cursor.fetchone()[0]

                cursor.execute('''
                    SELECT COUNT(*) FROM learned_patterns
                    WHERE last_updated >= ? AND created_at < ?
                ''', (week_start_str, week_start_str))
                patterns_refined = cursor.fetchone()[0]

                # Get savings
                cursor.execute('''
                    SELECT AVG(o.actual_time_saving), AVG(o.actual_cost_saving)
                    FROM route_outcomes o
                    WHERE o.measured_at >= ?
                ''', (week_start_str,))
                savings_row = cursor.fetchone()
                avg_time = savings_row[0] or 0.0
                avg_cost = savings_row[1] or 0.0

                # Insert metrics
                cursor.execute('''
                    INSERT INTO learning_metrics (
                        week_start_date, avg_prediction_accuracy,
                        decision_success_rate, avg_time_savings,
                        avg_cost_savings, patterns_discovered,
                        patterns_refined, confidence_trend
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    week_start_str,
                    avg_quality,
                    success_rate,
                    avg_time,
                    avg_cost,
                    patterns_discovered,
                    patterns_refined,
                    avg_quality - 0.7  # Trend relative to baseline
                ))

                conn.commit()
                logger.info(f"📈 Updated weekly metrics for {week_start_str}")

        except Exception as e:
            logger.error(f"Error updating weekly metrics: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def get_pattern_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get human-readable insights from learned patterns
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT 
                    pattern_type, conditions, confidence,
                    times_observed, success_count, avg_improvement,
                    last_successful_use
                FROM learned_patterns
                WHERE confidence >= ?
                ORDER BY confidence DESC, times_observed DESC
                LIMIT ?
            ''', (self.pattern_confidence_threshold, limit))

            insights = []
            for row in cursor.fetchall():
                pattern_type, conditions_json, confidence, times_obs, success_cnt, avg_imp, last_use = row
                conditions = json.loads(conditions_json)

                insight = {
                    'pattern_type': pattern_type,
                    'conditions': conditions,
                    'confidence': round(confidence, 2),
                    'observations': times_obs,
                    'success_rate': round(success_cnt / times_obs, 2),
                    'avg_improvement_minutes': round(avg_imp, 1),
                    'last_used': last_use,
                    'description': self._generate_pattern_description(pattern_type, conditions, confidence, times_obs, avg_imp)
                }
                insights.append(insight)

            return insights

        except Exception as e:
            logger.error(f"Error getting insights: {str(e)}")
            return []
        finally:
            conn.close()

    def _generate_pattern_description(
        self,
        pattern_type: str,
        conditions: Dict,
        confidence: float,
        times_observed: int,
        avg_improvement: float
    ) -> str:
        """
        Generate human-readable description of a learned pattern
        """
        desc_parts = []

        # Pattern type
        if pattern_type == 'reroute':
            desc_parts.append("Rerouting")
        elif pattern_type == 'optimize':
            desc_parts.append("Route optimization")
        elif pattern_type == 'prioritize':
            desc_parts.append("Priority handling")

        # Conditions
        condition_strs = []
        if 'traffic_level' in conditions:
            condition_strs.append(f"during {conditions['traffic_level']} traffic")
        if 'weather' in conditions:
            condition_strs.append(f"in {conditions['weather']} weather")

        if condition_strs:
            desc_parts.append(" ".join(condition_strs))

        # Performance
        desc_parts.append(f"saves avg {avg_improvement:.0f} minutes")
        desc_parts.append(f"({int(confidence * 100)}% confidence from {times_observed} observations)")

        return " ".join(desc_parts)

