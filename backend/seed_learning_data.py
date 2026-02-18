"""
Seed learning data for demonstration
Populates the database with sample decisions and outcomes to showcase learning
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta

DATABASE = 'smart_logistics.db'


def seed_learning_data():
    """Seed sample learning data to demonstrate the self-learning system"""

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("🌱 Seeding learning data...")

    # Clear existing learning data
    cursor.execute('DELETE FROM route_decisions')
    cursor.execute('DELETE FROM route_outcomes')
    cursor.execute('DELETE FROM learned_patterns')
    cursor.execute('DELETE FROM learning_metrics')

    # Scenario 1: High traffic rerouting (mostly successful)
    print("📊 Creating high traffic reroute scenarios...")
    for i in range(15):
        timestamp = datetime.now() - timedelta(days=random.randint(1, 30))

        # Create decision
        cursor.execute('''
            INSERT INTO route_decisions (
                timestamp, agent_id, decision_type, num_active_routes,
                traffic_conditions, weather_conditions, genai_reasoning,
                confidence_score, predicted_time_saving, predicted_cost_saving,
                routes_affected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp.isoformat(),
            'genai_route_optimizer_001',
            'reroute',
            random.randint(5, 15),
            json.dumps({'traffic_level': 'high', 'zone': 'downtown'}),
            json.dumps({'condition': 'clear'}),
            'Heavy traffic detected on Route A. Rerouting via Route B to avoid congestion.',
            random.uniform(0.7, 0.9),
            random.randint(10, 20),
            random.uniform(15.0, 30.0),
            json.dumps(['route_1', 'route_2'])
        ))

        decision_id = cursor.lastrowid

        # Create successful outcome (85% success rate)
        is_success = random.random() < 0.85

        if is_success:
            actual_time = random.randint(12, 22)  # Close to predicted
            actual_cost = random.uniform(16.0, 32.0)
            success_rate = random.uniform(0.9, 1.0)
            satisfaction = random.uniform(4.0, 5.0)
            issues = []
        else:
            actual_time = random.randint(5, 10)  # Less than predicted
            actual_cost = random.uniform(5.0, 15.0)
            success_rate = random.uniform(0.7, 0.85)
            satisfaction = random.uniform(3.0, 3.8)
            issues = ['unexpected_road_closure']

        cursor.execute('''
            INSERT INTO route_outcomes (
                decision_id, actual_time_saving, actual_cost_saving,
                delivery_success_rate, customer_satisfaction,
                issues_encountered, measured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision_id,
            actual_time,
            actual_cost,
            success_rate,
            satisfaction,
            json.dumps(issues),
            (timestamp + timedelta(hours=2)).isoformat()
        ))

        # Calculate quality score
        time_accuracy = 1.0 - min(abs(cursor.execute(
            'SELECT predicted_time_saving FROM route_decisions WHERE decision_id = ?',
            (decision_id,)
        ).fetchone()[0] - actual_time) / 20.0, 1.0)

        quality_score = (0.3 * time_accuracy + 0.3 * 0.9 + 0.2 * success_rate + 0.2 * (satisfaction / 5.0))

        cursor.execute('''
            UPDATE route_decisions 
            SET decision_quality_score = ?, outcome_measured = 1, learning_processed = 1
            WHERE decision_id = ?
        ''', (quality_score, decision_id))

    # Scenario 2: Route optimization (moderately successful)
    print("📊 Creating route optimization scenarios...")
    for i in range(12):
        timestamp = datetime.now() - timedelta(days=random.randint(1, 25))

        cursor.execute('''
            INSERT INTO route_decisions (
                timestamp, agent_id, decision_type, num_active_routes,
                traffic_conditions, weather_conditions, genai_reasoning,
                confidence_score, predicted_time_saving, predicted_cost_saving,
                routes_affected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp.isoformat(),
            'genai_route_optimizer_001',
            'optimize',
            random.randint(8, 20),
            json.dumps({'traffic_level': 'medium'}),
            json.dumps({'condition': 'clear'}),
            'Inefficient route sequence detected. Optimizing delivery order to reduce total distance.',
            random.uniform(0.6, 0.8),
            random.randint(8, 15),
            random.uniform(12.0, 25.0),
            json.dumps(['route_3', 'route_4', 'route_5'])
        ))

        decision_id = cursor.lastrowid

        # 70% success rate
        is_success = random.random() < 0.70

        if is_success:
            actual_time = random.randint(9, 17)
            actual_cost = random.uniform(13.0, 27.0)
            success_rate = random.uniform(0.85, 1.0)
            satisfaction = random.uniform(3.8, 4.5)
            issues = []
        else:
            actual_time = random.randint(3, 8)
            actual_cost = random.uniform(5.0, 12.0)
            success_rate = random.uniform(0.75, 0.9)
            satisfaction = random.uniform(3.2, 3.9)
            issues = ['minor_delay']

        cursor.execute('''
            INSERT INTO route_outcomes (
                decision_id, actual_time_saving, actual_cost_saving,
                delivery_success_rate, customer_satisfaction,
                issues_encountered, measured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision_id,
            actual_time,
            actual_cost,
            success_rate,
            satisfaction,
            json.dumps(issues),
            (timestamp + timedelta(hours=3)).isoformat()
        ))

        time_accuracy = 1.0 - min(abs(cursor.execute(
            'SELECT predicted_time_saving FROM route_decisions WHERE decision_id = ?',
            (decision_id,)
        ).fetchone()[0] - actual_time) / 15.0, 1.0)

        quality_score = (0.3 * time_accuracy + 0.3 * 0.8 + 0.2 * success_rate + 0.2 * (satisfaction / 5.0))

        cursor.execute('''
            UPDATE route_decisions 
            SET decision_quality_score = ?, outcome_measured = 1, learning_processed = 1
            WHERE decision_id = ?
        ''', (quality_score, decision_id))

    # Scenario 3: Priority handling (very successful)
    print("📊 Creating priority handling scenarios...")
    for i in range(8):
        timestamp = datetime.now() - timedelta(days=random.randint(1, 20))

        cursor.execute('''
            INSERT INTO route_decisions (
                timestamp, agent_id, decision_type, num_active_routes,
                traffic_conditions, weather_conditions, genai_reasoning,
                confidence_score, predicted_time_saving, predicted_cost_saving,
                routes_affected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp.isoformat(),
            'genai_route_optimizer_001',
            'prioritize',
            random.randint(6, 12),
            json.dumps({'traffic_level': 'low'}),
            json.dumps({'condition': 'clear'}),
            'High priority delivery detected. Adjusting sequence to prioritize urgent orders.',
            random.uniform(0.75, 0.95),
            random.randint(5, 12),
            random.uniform(8.0, 18.0),
            json.dumps(['route_6'])
        ))

        decision_id = cursor.lastrowid

        # 92% success rate
        is_success = random.random() < 0.92

        if is_success:
            actual_time = random.randint(6, 14)
            actual_cost = random.uniform(9.0, 20.0)
            success_rate = random.uniform(0.95, 1.0)
            satisfaction = random.uniform(4.5, 5.0)
            issues = []
        else:
            actual_time = random.randint(2, 5)
            actual_cost = random.uniform(3.0, 8.0)
            success_rate = random.uniform(0.85, 0.95)
            satisfaction = random.uniform(3.8, 4.3)
            issues = []

        cursor.execute('''
            INSERT INTO route_outcomes (
                decision_id, actual_time_saving, actual_cost_saving,
                delivery_success_rate, customer_satisfaction,
                issues_encountered, measured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision_id,
            actual_time,
            actual_cost,
            success_rate,
            satisfaction,
            json.dumps(issues),
            (timestamp + timedelta(hours=1)).isoformat()
        ))

        time_accuracy = 1.0 - min(abs(cursor.execute(
            'SELECT predicted_time_saving FROM route_decisions WHERE decision_id = ?',
            (decision_id,)
        ).fetchone()[0] - actual_time) / 12.0, 1.0)

        quality_score = (0.3 * time_accuracy + 0.3 * 0.95 + 0.2 * success_rate + 0.2 * (satisfaction / 5.0))

        cursor.execute('''
            UPDATE route_decisions 
            SET decision_quality_score = ?, outcome_measured = 1, learning_processed = 1
            WHERE decision_id = ?
        ''', (quality_score, decision_id))

    # Create learned patterns
    print("🧠 Creating learned patterns...")

    # Pattern 1: High traffic reroute
    cursor.execute('''
        INSERT INTO learned_patterns (
            pattern_type, conditions, recommended_action, confidence,
            times_observed, success_count, failure_count, avg_improvement
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'reroute',
        json.dumps({'decision_type': 'reroute', 'traffic_level': 'high'}),
        'reroute',
        0.85,
        15,
        13,
        2,
        16.5
    ))

    # Pattern 2: Medium traffic optimization
    cursor.execute('''
        INSERT INTO learned_patterns (
            pattern_type, conditions, recommended_action, confidence,
            times_observed, success_count, failure_count, avg_improvement
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'optimize',
        json.dumps({'decision_type': 'optimize', 'traffic_level': 'medium'}),
        'optimize',
        0.70,
        12,
        8,
        4,
        11.3
    ))

    # Pattern 3: Priority handling
    cursor.execute('''
        INSERT INTO learned_patterns (
            pattern_type, conditions, recommended_action, confidence,
            times_observed, success_count, failure_count, avg_improvement
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'prioritize',
        json.dumps({'decision_type': 'prioritize', 'traffic_level': 'low'}),
        'prioritize',
        0.92,
        8,
        7,
        1,
        9.2
    ))

    conn.commit()
    conn.close()

    print("✅ Learning data seeded successfully!")
    print(f"   - 15 high traffic reroute decisions (85% success)")
    print(f"   - 12 optimization decisions (70% success)")
    print(f"   - 8 priority handling decisions (92% success)")
    print(f"   - 3 learned patterns created")
    print("\n🎓 The system now has historical learning data to demonstrate improvement!")


if __name__ == '__main__':
    seed_learning_data()

