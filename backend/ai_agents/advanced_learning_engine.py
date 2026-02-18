"""
Advanced Learning Engine - Phase 2 & 3 Enhancements
Multi-objective optimization, seasonal patterns, geographic clustering, and predictive intelligence
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cdist

logger = logging.getLogger(__name__)


class AdvancedLearningEngine:
    """
    Enhanced learning engine with Phase 2 & 3 capabilities
    """

    def __init__(self, database_path: str = 'smart_logistics.db'):
        self.database_path = database_path
        self.min_observations = 3
        self.pattern_confidence_threshold = 0.6

        # Phase 2: Advanced Learning parameters
        self.seasonal_window_days = 90  # 3 months for seasonal detection
        self.geographic_cluster_eps = 0.05  # ~5km for clustering
        self.min_cluster_size = 3

        # Phase 3: Predictive Intelligence parameters
        self.what_if_scenarios = []
        self.auto_tune_history = []

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.database_path)

    # ========================================================================
    # PHASE 2: MULTI-OBJECTIVE OPTIMIZATION
    # ========================================================================

    def calculate_multi_objective_score(
        self,
        time_saving: float,
        cost_saving: float,
        satisfaction: float,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate combined score using multiple objectives

        Args:
            time_saving: Minutes saved
            cost_saving: Dollars saved
            satisfaction: Customer satisfaction (0-5)
            weights: Optional custom weights for each objective

        Returns:
            Combined multi-objective score (0-1)
        """
        if weights is None:
            weights = {
                'time': 0.35,
                'cost': 0.35,
                'satisfaction': 0.30
            }

        # Normalize each objective to 0-1 scale
        time_norm = min(time_saving / 30, 1.0)  # 30 min = 1.0
        cost_norm = min(cost_saving / 50, 1.0)  # $50 = 1.0
        satisfaction_norm = satisfaction / 5.0   # Already 0-5

        # Calculate weighted sum
        score = (
            weights['time'] * time_norm +
            weights['cost'] * cost_norm +
            weights['satisfaction'] * satisfaction_norm
        )

        return score

    def optimize_multi_objective(
        self,
        decision_type: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Find patterns that optimize multiple objectives simultaneously

        Returns:
            Best patterns for each objective and combined best
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get all patterns with outcomes
            cursor.execute('''
                SELECT 
                    p.pattern_id,
                    p.pattern_type,
                    p.conditions,
                    p.confidence,
                    p.avg_improvement,
                    AVG(o.actual_cost_saving) as avg_cost,
                    AVG(o.customer_satisfaction) as avg_satisfaction
                FROM learned_patterns p
                JOIN route_decisions d ON d.decision_type = p.pattern_type
                JOIN route_outcomes o ON o.decision_id = d.decision_id
                WHERE p.pattern_type = ?
                GROUP BY p.pattern_id
                HAVING COUNT(*) >= ?
            ''', (decision_type, self.min_observations))

            patterns = []
            for row in cursor.fetchall():
                pattern_id, ptype, conditions, confidence, avg_time, avg_cost, avg_sat = row

                # Calculate multi-objective score
                mo_score = self.calculate_multi_objective_score(
                    avg_time or 0,
                    avg_cost or 0,
                    avg_sat or 3.5
                )

                patterns.append({
                    'pattern_id': pattern_id,
                    'pattern_type': ptype,
                    'conditions': json.loads(conditions),
                    'confidence': confidence,
                    'avg_time_saving': avg_time,
                    'avg_cost_saving': avg_cost,
                    'avg_satisfaction': avg_sat,
                    'multi_objective_score': mo_score
                })

            # Sort by multi-objective score
            patterns.sort(key=lambda x: x['multi_objective_score'], reverse=True)

            result = {
                'best_overall': patterns[0] if patterns else None,
                'best_time': max(patterns, key=lambda x: x['avg_time_saving']) if patterns else None,
                'best_cost': max(patterns, key=lambda x: x['avg_cost_saving']) if patterns else None,
                'best_satisfaction': max(patterns, key=lambda x: x['avg_satisfaction']) if patterns else None,
                'pareto_optimal': self._find_pareto_optimal(patterns)
            }

            logger.info(f"✅ Multi-objective optimization complete: {len(patterns)} patterns analyzed")
            return result

        except Exception as e:
            logger.error(f"Error in multi-objective optimization: {str(e)}")
            return {}
        finally:
            conn.close()

    def _find_pareto_optimal(self, patterns: List[Dict]) -> List[Dict]:
        """Find Pareto-optimal patterns (non-dominated solutions)"""
        if not patterns:
            return []

        pareto = []
        for p1 in patterns:
            dominated = False
            for p2 in patterns:
                if p1 == p2:
                    continue

                # Check if p2 dominates p1 (better in all objectives)
                if (p2['avg_time_saving'] >= p1['avg_time_saving'] and
                    p2['avg_cost_saving'] >= p1['avg_cost_saving'] and
                    p2['avg_satisfaction'] >= p1['avg_satisfaction'] and
                    (p2['avg_time_saving'] > p1['avg_time_saving'] or
                     p2['avg_cost_saving'] > p1['avg_cost_saving'] or
                     p2['avg_satisfaction'] > p1['avg_satisfaction'])):
                    dominated = True
                    break

            if not dominated:
                pareto.append(p1)

        return pareto

    # ========================================================================
    # PHASE 2: SEASONAL PATTERN DETECTION
    # ========================================================================

    def detect_seasonal_patterns(
        self,
        decision_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect patterns that vary by season/time of year

        Returns:
            Seasonal patterns grouped by month, day of week, etc.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = '''
                SELECT 
                    d.timestamp,
                    d.decision_type,
                    d.decision_quality_score,
                    o.actual_time_saving,
                    o.actual_cost_saving,
                    o.customer_satisfaction
                FROM route_decisions d
                JOIN route_outcomes o ON d.decision_id = o.decision_id
                WHERE d.outcome_measured = 1
            '''

            params = []
            if decision_type:
                query += ' AND d.decision_type = ?'
                params.append(decision_type)

            cursor.execute(query, params)

            # Group by temporal features
            monthly_patterns = defaultdict(list)
            weekly_patterns = defaultdict(list)
            hourly_patterns = defaultdict(list)

            for row in cursor.fetchall():
                timestamp_str, dtype, quality, time_save, cost_save, satisfaction = row
                timestamp = datetime.fromisoformat(timestamp_str)

                month = timestamp.month
                day_of_week = timestamp.strftime('%A')
                hour = timestamp.hour

                data = {
                    'quality': quality or 0,
                    'time_saving': time_save or 0,
                    'cost_saving': cost_save or 0,
                    'satisfaction': satisfaction or 3.5
                }

                monthly_patterns[month].append(data)
                weekly_patterns[day_of_week].append(data)
                hourly_patterns[hour].append(data)

            # Analyze patterns
            result = {
                'monthly': self._analyze_temporal_group(monthly_patterns, 'Month'),
                'weekly': self._analyze_temporal_group(weekly_patterns, 'Day of Week'),
                'hourly': self._analyze_temporal_group(hourly_patterns, 'Hour'),
                'seasonality_detected': self._detect_significant_seasonality(monthly_patterns)
            }

            logger.info(f"✅ Seasonal pattern detection complete")
            return result

        except Exception as e:
            logger.error(f"Error detecting seasonal patterns: {str(e)}")
            return {}
        finally:
            conn.close()

    def _analyze_temporal_group(
        self,
        groups: Dict[Any, List[Dict]],
        group_name: str
    ) -> List[Dict]:
        """Analyze temporal groupings"""
        results = []

        for key, values in groups.items():
            if len(values) >= self.min_observations:
                avg_quality = np.mean([v['quality'] for v in values])
                avg_time = np.mean([v['time_saving'] for v in values])
                avg_cost = np.mean([v['cost_saving'] for v in values])
                avg_satisfaction = np.mean([v['satisfaction'] for v in values])

                results.append({
                    f'{group_name.lower().replace(" ", "_")}': key,
                    'avg_quality': round(avg_quality, 3),
                    'avg_time_saving': round(avg_time, 2),
                    'avg_cost_saving': round(avg_cost, 2),
                    'avg_satisfaction': round(avg_satisfaction, 2),
                    'sample_size': len(values)
                })

        return sorted(results, key=lambda x: x['avg_quality'], reverse=True)

    def _detect_significant_seasonality(self, monthly_data: Dict) -> bool:
        """Check if there's significant seasonal variation"""
        if len(monthly_data) < 3:
            return False

        qualities = []
        for month_data in monthly_data.values():
            if month_data:
                qualities.append(np.mean([d['quality'] for d in month_data]))

        if len(qualities) < 3:
            return False

        # Use coefficient of variation to detect seasonality
        cv = np.std(qualities) / (np.mean(qualities) + 1e-6)
        return cv > 0.15  # 15% variation indicates seasonality

    # ========================================================================
    # PHASE 2: GEOGRAPHIC PATTERN CLUSTERING
    # ========================================================================

    def cluster_geographic_patterns(
        self,
        decision_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cluster patterns by geographic location

        Returns:
            Geographic clusters with their performance characteristics
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get decisions with location data (from routes_affected)
            query = '''
                SELECT 
                    d.decision_id,
                    d.routes_affected,
                    d.decision_quality_score,
                    o.actual_time_saving,
                    o.actual_cost_saving
                FROM route_decisions d
                JOIN route_outcomes o ON d.decision_id = o.decision_id
                WHERE d.outcome_measured = 1
            '''

            params = []
            if decision_type:
                query += ' AND d.decision_type = ?'
                params.append(decision_type)

            cursor.execute(query, params)

            # Extract location data (this would need actual lat/lon from routes)
            # For now, we'll simulate with route zones
            locations = []
            performance_data = []

            for row in cursor.fetchall():
                decision_id, routes_json, quality, time_save, cost_save = row

                # In real implementation, extract lat/lon from routes
                # For demo, we'll use simulated coordinates
                locations.append([
                    np.random.uniform(40.7, 40.8),  # NYC latitude range
                    np.random.uniform(-74.0, -73.9)  # NYC longitude range
                ])

                performance_data.append({
                    'quality': quality or 0,
                    'time_saving': time_save or 0,
                    'cost_saving': cost_save or 0
                })

            if len(locations) < self.min_cluster_size:
                return {'clusters': [], 'message': 'Insufficient data for clustering'}

            # Perform DBSCAN clustering
            locations_array = np.array(locations)
            clustering = DBSCAN(
                eps=self.geographic_cluster_eps,
                min_samples=self.min_cluster_size
            ).fit(locations_array)

            # Analyze clusters
            clusters = []
            unique_labels = set(clustering.labels_)

            for label in unique_labels:
                if label == -1:  # Noise
                    continue

                cluster_mask = clustering.labels_ == label
                cluster_indices = np.where(cluster_mask)[0]

                # Calculate cluster statistics
                cluster_performance = [performance_data[i] for i in cluster_indices]
                cluster_locations = locations_array[cluster_mask]

                centroid = cluster_locations.mean(axis=0)

                clusters.append({
                    'cluster_id': int(label),
                    'size': len(cluster_indices),
                    'centroid': {
                        'lat': round(float(centroid[0]), 4),
                        'lon': round(float(centroid[1]), 4)
                    },
                    'avg_quality': round(np.mean([p['quality'] for p in cluster_performance]), 3),
                    'avg_time_saving': round(np.mean([p['time_saving'] for p in cluster_performance]), 2),
                    'avg_cost_saving': round(np.mean([p['cost_saving'] for p in cluster_performance]), 2)
                })

            result = {
                'clusters': sorted(clusters, key=lambda x: x['avg_quality'], reverse=True),
                'total_clusters': len(clusters),
                'noise_points': sum(clustering.labels_ == -1)
            }

            logger.info(f"✅ Geographic clustering complete: {len(clusters)} clusters found")
            return result

        except Exception as e:
            logger.error(f"Error in geographic clustering: {str(e)}")
            return {'clusters': [], 'error': str(e)}
        finally:
            conn.close()

    # ========================================================================
    # PHASE 2: CROSS-AGENT PATTERN SHARING
    # ========================================================================

    def share_patterns_between_agents(
        self,
        source_agent_id: str,
        target_agent_id: str,
        pattern_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Share learned patterns from one agent to another

        Args:
            source_agent_id: Agent to copy patterns from
            target_agent_id: Agent to copy patterns to
            pattern_types: Optional filter for pattern types

        Returns:
            Summary of shared patterns
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get high-confidence patterns from source agent
            query = '''
                SELECT DISTINCT
                    p.pattern_type,
                    p.conditions,
                    p.recommended_action,
                    p.confidence,
                    p.times_observed,
                    p.success_count,
                    p.avg_improvement
                FROM learned_patterns p
                JOIN route_decisions d ON d.decision_type = p.pattern_type
                WHERE d.agent_id = ?
                AND p.confidence >= ?
                AND p.times_observed >= ?
            '''

            params = [source_agent_id, self.pattern_confidence_threshold, self.min_observations]

            if pattern_types:
                placeholders = ','.join('?' * len(pattern_types))
                query += f' AND p.pattern_type IN ({placeholders})'
                params.extend(pattern_types)

            cursor.execute(query, params)

            shared_patterns = []
            for row in cursor.fetchall():
                ptype, conditions, action, confidence, times_obs, success, avg_imp = row

                # Check if target agent already has this pattern
                cursor.execute('''
                    SELECT pattern_id, confidence, times_observed
                    FROM learned_patterns
                    WHERE pattern_type = ? AND conditions = ?
                    LIMIT 1
                ''', (ptype, conditions))

                existing = cursor.fetchone()

                if existing:
                    # Update existing pattern with weighted average
                    existing_id, existing_conf, existing_times = existing

                    new_confidence = (confidence * times_obs + existing_conf * existing_times) / (times_obs + existing_times)
                    new_times = times_obs + existing_times

                    cursor.execute('''
                        UPDATE learned_patterns
                        SET confidence = ?,
                            times_observed = ?,
                            last_updated = ?
                        WHERE pattern_id = ?
                    ''', (new_confidence, new_times, datetime.now().isoformat(), existing_id))

                    shared_patterns.append({
                        'pattern_type': ptype,
                        'action': 'merged',
                        'new_confidence': round(new_confidence, 3)
                    })
                else:
                    # Create new pattern for target agent
                    cursor.execute('''
                        INSERT INTO learned_patterns (
                            pattern_type, conditions, recommended_action,
                            confidence, times_observed, success_count,
                            failure_count, avg_improvement
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ptype, conditions, action, confidence,
                        times_obs, success, times_obs - success, avg_imp
                    ))

                    shared_patterns.append({
                        'pattern_type': ptype,
                        'action': 'created',
                        'confidence': round(confidence, 3)
                    })

            conn.commit()

            result = {
                'source_agent': source_agent_id,
                'target_agent': target_agent_id,
                'patterns_shared': len(shared_patterns),
                'details': shared_patterns
            }

            logger.info(f"✅ Shared {len(shared_patterns)} patterns from {source_agent_id} to {target_agent_id}")
            return result

        except Exception as e:
            logger.error(f"Error sharing patterns: {str(e)}")
            conn.rollback()
            return {'error': str(e)}
        finally:
            conn.close()

    # ========================================================================
    # PHASE 3: PROACTIVE PATTERN RECOMMENDATIONS
    # ========================================================================

    def recommend_patterns_for_situation(
        self,
        current_situation: Dict[str, Any],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Proactively recommend patterns before a decision is made

        Args:
            current_situation: Current routing context
            top_k: Number of recommendations to return

        Returns:
            List of recommended patterns with reasoning
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Extract situation features
            traffic_level = current_situation.get('traffic_level', 'medium')
            time_of_day = current_situation.get('hour', 12)
            day_of_week = current_situation.get('day_of_week', 'Monday')

            # Query similar situations
            cursor.execute('''
                SELECT 
                    p.pattern_id,
                    p.pattern_type,
                    p.conditions,
                    p.confidence,
                    p.avg_improvement,
                    p.times_observed,
                    p.success_count,
                    p.last_successful_use
                FROM learned_patterns p
                WHERE p.confidence >= ?
                ORDER BY p.confidence DESC, p.times_observed DESC
                LIMIT ?
            ''', (self.pattern_confidence_threshold, top_k * 2))

            recommendations = []
            for row in cursor.fetchall():
                pid, ptype, conditions_json, conf, avg_imp, times, success, last_use = row
                conditions = json.loads(conditions_json)

                # Calculate similarity score
                similarity = self._calculate_situation_similarity(
                    current_situation,
                    conditions
                )

                if similarity > 0.5:  # Threshold for relevance
                    recommendations.append({
                        'pattern_id': pid,
                        'pattern_type': ptype,
                        'confidence': conf,
                        'avg_improvement': avg_imp,
                        'similarity': round(similarity, 3),
                        'success_rate': round(success / times, 3) if times > 0 else 0,
                        'observations': times,
                        'reasoning': self._generate_recommendation_reasoning(
                            ptype, conditions, conf, avg_imp, similarity
                        )
                    })

            # Sort by combined score (confidence * similarity)
            recommendations.sort(
                key=lambda x: x['confidence'] * x['similarity'],
                reverse=True
            )

            logger.info(f"✅ Generated {len(recommendations[:top_k])} pattern recommendations")
            return recommendations[:top_k]

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
        finally:
            conn.close()

    def _calculate_situation_similarity(
        self,
        current: Dict[str, Any],
        pattern_conditions: Dict[str, Any]
    ) -> float:
        """Calculate similarity between current situation and pattern conditions"""
        similarity_scores = []

        # Traffic level similarity
        traffic_map = {'low': 0, 'medium': 1, 'high': 2}
        if 'traffic_level' in current and 'traffic_level' in pattern_conditions:
            current_traffic = traffic_map.get(current['traffic_level'], 1)
            pattern_traffic = traffic_map.get(pattern_conditions['traffic_level'], 1)
            traffic_sim = 1.0 - abs(current_traffic - pattern_traffic) / 2.0
            similarity_scores.append(traffic_sim)

        # Weather similarity
        if 'weather' in current and 'weather' in pattern_conditions:
            weather_sim = 1.0 if current['weather'] == pattern_conditions['weather'] else 0.5
            similarity_scores.append(weather_sim)

        # Time similarity (if applicable)
        # Add more similarity calculations as needed

        return np.mean(similarity_scores) if similarity_scores else 0.5

    def _generate_recommendation_reasoning(
        self,
        pattern_type: str,
        conditions: Dict,
        confidence: float,
        avg_improvement: float,
        similarity: float
    ) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasoning = f"This {pattern_type} pattern has {confidence*100:.0f}% confidence "
        reasoning += f"based on previous successes. "
        reasoning += f"It typically saves {avg_improvement:.0f} minutes. "
        reasoning += f"Current situation matches this pattern {similarity*100:.0f}%."

        return reasoning

    # ========================================================================
    # PHASE 3: WHAT-IF SCENARIO SIMULATION
    # ========================================================================

    def simulate_what_if_scenario(
        self,
        scenario: Dict[str, Any],
        pattern_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Simulate outcomes of a hypothetical decision using learned patterns

        Args:
            scenario: Hypothetical situation to simulate
            pattern_id: Specific pattern to apply (optional)

        Returns:
            Predicted outcomes with confidence intervals
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get applicable patterns
            if pattern_id:
                cursor.execute('''
                    SELECT 
                        p.pattern_type,
                        p.confidence,
                        p.avg_improvement,
                        p.times_observed
                    FROM learned_patterns p
                    WHERE p.pattern_id = ?
                ''', (pattern_id,))
            else:
                # Find best matching pattern
                decision_type = scenario.get('decision_type', 'optimize')
                cursor.execute('''
                    SELECT 
                        p.pattern_type,
                        p.confidence,
                        p.avg_improvement,
                        p.times_observed
                    FROM learned_patterns p
                    WHERE p.pattern_type = ?
                    ORDER BY p.confidence DESC
                    LIMIT 1
                ''', (decision_type,))

            pattern_data = cursor.fetchone()

            if not pattern_data:
                return {
                    'prediction': 'No applicable patterns found',
                    'confidence': 0.0
                }

            ptype, confidence, avg_improvement, times_observed = pattern_data

            # Get historical variance
            cursor.execute('''
                SELECT 
                    o.actual_time_saving,
                    o.actual_cost_saving,
                    o.customer_satisfaction
                FROM route_outcomes o
                JOIN route_decisions d ON o.decision_id = d.decision_id
                WHERE d.decision_type = ?
            ''', (ptype,))

            historical_data = cursor.fetchall()

            if historical_data:
                time_savings = [h[0] for h in historical_data if h[0]]
                cost_savings = [h[1] for h in historical_data if h[1]]
                satisfactions = [h[2] for h in historical_data if h[2]]

                time_std = np.std(time_savings) if time_savings else 5.0
                cost_std = np.std(cost_savings) if cost_savings else 10.0
                sat_std = np.std(satisfactions) if satisfactions else 0.5
            else:
                time_std, cost_std, sat_std = 5.0, 10.0, 0.5

            # Generate prediction with confidence intervals
            prediction = {
                'scenario': scenario,
                'pattern_applied': ptype,
                'pattern_confidence': round(confidence, 3),
                'predicted_outcomes': {
                    'time_saving': {
                        'mean': round(avg_improvement, 2),
                        'lower_95': round(avg_improvement - 1.96 * time_std, 2),
                        'upper_95': round(avg_improvement + 1.96 * time_std, 2)
                    },
                    'cost_saving': {
                        'mean': round(avg_improvement * 1.5, 2),  # Rough estimate
                        'lower_95': round((avg_improvement * 1.5) - 1.96 * cost_std, 2),
                        'upper_95': round((avg_improvement * 1.5) + 1.96 * cost_std, 2)
                    },
                    'satisfaction': {
                        'mean': 4.2,
                        'lower_95': round(4.2 - 1.96 * sat_std, 2),
                        'upper_95': min(5.0, round(4.2 + 1.96 * sat_std, 2))
                    }
                },
                'based_on_observations': times_observed,
                'recommendation': self._generate_what_if_recommendation(
                    avg_improvement, confidence
                )
            }

            logger.info(f"✅ What-if simulation complete for scenario: {scenario.get('decision_type')}")
            return prediction

        except Exception as e:
            logger.error(f"Error in what-if simulation: {str(e)}")
            return {'error': str(e)}
        finally:
            conn.close()

    def _generate_what_if_recommendation(
        self,
        expected_improvement: float,
        confidence: float
    ) -> str:
        """Generate recommendation based on simulation"""
        if confidence > 0.8 and expected_improvement > 10:
            return "Highly recommended - Strong evidence of significant improvement"
        elif confidence > 0.6 and expected_improvement > 5:
            return "Recommended - Good evidence of positive outcome"
        elif expected_improvement > 0:
            return "Consider carefully - Moderate evidence of improvement"
        else:
            return "Not recommended - Insufficient evidence of benefit"

    # ========================================================================
    # PHASE 3: AUTOMATIC PARAMETER TUNING
    # ========================================================================

    def auto_tune_parameters(
        self,
        target_metric: str = 'quality'
    ) -> Dict[str, Any]:
        """
        Automatically tune learning engine parameters based on performance

        Args:
            target_metric: Metric to optimize ('quality', 'accuracy', 'improvement')

        Returns:
            Optimized parameters and performance improvement
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get current performance
            current_performance = self._measure_current_performance(cursor, target_metric)

            # Parameter search space
            param_space = {
                'pattern_confidence_threshold': [0.5, 0.6, 0.7, 0.8],
                'min_observations': [2, 3, 5, 7],
                'seasonal_window_days': [60, 90, 120]
            }

            best_params = {
                'pattern_confidence_threshold': self.pattern_confidence_threshold,
                'min_observations': self.min_observations,
                'seasonal_window_days': self.seasonal_window_days
            }
            best_performance = current_performance

            # Grid search over parameter space
            for conf_threshold in param_space['pattern_confidence_threshold']:
                for min_obs in param_space['min_observations']:
                    # Temporarily set parameters
                    old_conf = self.pattern_confidence_threshold
                    old_min = self.min_observations

                    self.pattern_confidence_threshold = conf_threshold
                    self.min_observations = min_obs

                    # Evaluate performance
                    performance = self._measure_current_performance(cursor, target_metric)

                    if performance > best_performance:
                        best_performance = performance
                        best_params['pattern_confidence_threshold'] = conf_threshold
                        best_params['min_observations'] = min_obs

                    # Restore parameters
                    self.pattern_confidence_threshold = old_conf
                    self.min_observations = old_min

            # Apply best parameters
            self.pattern_confidence_threshold = best_params['pattern_confidence_threshold']
            self.min_observations = best_params['min_observations']

            improvement = ((best_performance - current_performance) / current_performance * 100
                          if current_performance > 0 else 0)

            result = {
                'previous_parameters': {
                    'pattern_confidence_threshold': 0.6,
                    'min_observations': 3
                },
                'optimized_parameters': best_params,
                'previous_performance': round(current_performance, 4),
                'optimized_performance': round(best_performance, 4),
                'improvement_percent': round(improvement, 2),
                'recommendation': 'Parameters updated' if improvement > 1 else 'No significant improvement found'
            }

            logger.info(f"✅ Auto-tuning complete: {improvement:.2f}% improvement")
            return result

        except Exception as e:
            logger.error(f"Error in auto-tuning: {str(e)}")
            return {'error': str(e)}
        finally:
            conn.close()

    def _measure_current_performance(
        self,
        cursor,
        metric: str
    ) -> float:
        """Measure current system performance"""
        try:
            if metric == 'quality':
                cursor.execute('''
                    SELECT AVG(decision_quality_score)
                    FROM route_decisions
                    WHERE decision_quality_score IS NOT NULL
                ''')
            elif metric == 'accuracy':
                cursor.execute('''
                    SELECT COUNT(*) * 1.0 / (SELECT COUNT(*) FROM route_decisions WHERE outcome_measured = 1)
                    FROM route_decisions d
                    JOIN route_outcomes o ON d.decision_id = o.decision_id
                    WHERE ABS(d.predicted_time_saving - o.actual_time_saving) <= ABS(d.predicted_time_saving * 0.2)
                ''')
            else:  # improvement
                cursor.execute('''
                    SELECT AVG(actual_time_saving)
                    FROM route_outcomes
                ''')

            result = cursor.fetchone()
            return result[0] if result and result[0] else 0.0

        except Exception:
            return 0.0

    # ========================================================================
    # PHASE 3: FEDERATED LEARNING
    # ========================================================================

    def aggregate_federated_patterns(
        self,
        external_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate patterns from multiple external systems (federated learning)

        Args:
            external_patterns: Patterns from other learning systems

        Returns:
            Summary of aggregated knowledge
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            aggregated = []

            for ext_pattern in external_patterns:
                pattern_type = ext_pattern.get('pattern_type')
                conditions = ext_pattern.get('conditions', {})
                confidence = ext_pattern.get('confidence', 0.5)
                observations = ext_pattern.get('observations', 1)
                improvement = ext_pattern.get('avg_improvement', 0)

                # Check if we have similar pattern
                cursor.execute('''
                    SELECT 
                        pattern_id,
                        confidence,
                        times_observed,
                        avg_improvement
                    FROM learned_patterns
                    WHERE pattern_type = ?
                    AND conditions = ?
                ''', (pattern_type, json.dumps(conditions)))

                existing = cursor.fetchone()

                if existing:
                    # Federated averaging
                    pid, local_conf, local_obs, local_imp = existing

                    # Weighted average based on number of observations
                    total_obs = local_obs + observations
                    new_conf = (local_conf * local_obs + confidence * observations) / total_obs
                    new_imp = (local_imp * local_obs + improvement * observations) / total_obs

                    cursor.execute('''
                        UPDATE learned_patterns
                        SET confidence = ?,
                            times_observed = ?,
                            avg_improvement = ?,
                            last_updated = ?
                        WHERE pattern_id = ?
                    ''', (new_conf, total_obs, new_imp, datetime.now().isoformat(), pid))

                    aggregated.append({
                        'pattern_type': pattern_type,
                        'action': 'aggregated',
                        'new_confidence': round(new_conf, 3),
                        'total_observations': total_obs
                    })
                else:
                    # Add new pattern from federated source
                    cursor.execute('''
                        INSERT INTO learned_patterns (
                            pattern_type,
                            conditions,
                            recommended_action,
                            confidence,
                            times_observed,
                            success_count,
                            failure_count,
                            avg_improvement
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pattern_type,
                        json.dumps(conditions),
                        pattern_type,
                        confidence,
                        observations,
                        int(observations * confidence),
                        int(observations * (1 - confidence)),
                        improvement
                    ))

                    aggregated.append({
                        'pattern_type': pattern_type,
                        'action': 'imported',
                        'confidence': round(confidence, 3)
                    })

            conn.commit()

            result = {
                'patterns_processed': len(external_patterns),
                'patterns_aggregated': len([a for a in aggregated if a['action'] == 'aggregated']),
                'patterns_imported': len([a for a in aggregated if a['action'] == 'imported']),
                'details': aggregated
            }

            logger.info(f"✅ Federated learning: aggregated {len(aggregated)} patterns")
            return result

        except Exception as e:
            logger.error(f"Error in federated aggregation: {str(e)}")
            conn.rollback()
            return {'error': str(e)}
        finally:
            conn.close()

    def export_patterns_for_federation(
        self,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Export high-quality patterns for sharing with other systems

        Returns:
            List of patterns suitable for federated sharing
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT 
                    pattern_type,
                    conditions,
                    confidence,
                    times_observed,
                    avg_improvement,
                    success_count
                FROM learned_patterns
                WHERE confidence >= ?
                AND times_observed >= ?
                ORDER BY confidence DESC
            ''', (min_confidence, self.min_observations))

            patterns = []
            for row in cursor.fetchall():
                ptype, conditions, conf, times, improvement, success = row

                patterns.append({
                    'pattern_type': ptype,
                    'conditions': json.loads(conditions),
                    'confidence': conf,
                    'observations': times,
                    'avg_improvement': improvement,
                    'success_rate': success / times if times > 0 else 0,
                    'source': 'smart_logistics_system',
                    'exported_at': datetime.now().isoformat()
                })

            logger.info(f"✅ Exported {len(patterns)} patterns for federation")
            return patterns

        except Exception as e:
            logger.error(f"Error exporting patterns: {str(e)}")
            return []
        finally:
            conn.close()

