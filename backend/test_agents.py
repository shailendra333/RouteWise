"""
Test Script for AI Agents System
Run this to test all AI agent functionalities with real data
"""

import requests
import json
from time import sleep

API_BASE = "http://localhost:5000/api"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_health_check():
    """Test system health"""
    print_section("1. HEALTH CHECK")

    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ System Status: {response.json()['status']}")

        # Test agents health
        response = requests.get(f"{API_BASE}/agents/health")
        if response.status_code == 200:
            print(f"✅ AI Agents Status: {response.json()['status']}")
        else:
            print(f"⚠️  AI Agents: Not available")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_database_stats():
    """Test database statistics"""
    print_section("2. DATABASE STATISTICS")

    try:
        response = requests.get(f"{API_BASE}/database-stats")
        data = response.json()

        if data['success']:
            stats = data['stats']
            print(f"📦 Total Orders: {stats['total_orders']}")
            print(f"🚛 Total Routes: {stats['total_routes']}")
            print(f"📈 Total Forecasts: {stats['total_forecasts']}")
            print(f"🤖 Agent Logs: {stats['total_agent_logs']}")
            print(f"\n📊 Orders by Zone:")
            for zone_data in stats['orders_by_zone']:
                print(f"   Zone {zone_data['zone']}: {zone_data['count']} orders")
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_agent_status():
    """Test agent status"""
    print_section("3. AI AGENT STATUS")

    try:
        response = requests.get(f"{API_BASE}/agents/status")
        data = response.json()

        if data['success']:
            for agent_name, agent_info in data['status']['agents'].items():
                print(f"\n🤖 {agent_info['name']}")
                print(f"   Status: {agent_info['status']}")
                print(f"   Success Rate: {agent_info['metrics']['success_rate']*100:.1f}%")
                print(f"   Tasks Completed: {agent_info['metrics']['tasks_completed']}")
                print(f"   Avg Execution Time: {agent_info['metrics']['average_execution_time']:.2f}s")
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_route_optimizer():
    """Test route optimizer agent"""
    print_section("4. ROUTE OPTIMIZER AGENT")

    try:
        # Get sample orders
        print("📥 Fetching sample orders...")
        orders_response = requests.get(f"{API_BASE}/data-preview?type=orders&limit=15")
        orders = orders_response.json()['data']

        # Prepare test data
        data = {
            "current_routes": [{
                "route_id": 1,
                "deliveries": [
                    {
                        "id": order['id'],
                        "lat": order['latitude'],
                        "lon": order['longitude'],
                        "priority": "urgent" if i < 2 else "normal"
                    }
                    for i, order in enumerate(orders[:10])
                ],
                "efficiency": 0.65
            }],
            "traffic_data": {
                "congestion_level": "high"
            }
        }

        print("🚀 Executing route optimization...")
        response = requests.post(
            f"{API_BASE}/agents/route-optimizer/execute",
            json=data
        )

        result = response.json()

        if result['success']:
            agent_result = result['result']['result']
            if agent_result['success']:
                improvements = agent_result.get('improvements', {})
                print(f"✅ Route Optimization Complete!")
                print(f"   Routes Optimized: {improvements.get('total_routes_optimized', 0)}")
                print(f"   Time Saved: {improvements.get('estimated_time_saved', 0)} minutes")
                print(f"   Cost Saved: ${improvements.get('estimated_cost_saved', 0)}")
                print(f"   Execution Time: {result['result']['execution_time']:.2f}s")
            else:
                print(f"⚠️  Optimization completed with issues")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_demand_predictor():
    """Test demand predictor agent"""
    print_section("5. DEMAND PREDICTOR AGENT")

    try:
        # Get historical orders
        print("📥 Fetching historical orders...")
        orders_response = requests.get(f"{API_BASE}/data-preview?type=orders&limit=100")
        orders = orders_response.json()['data']

        data = {
            "historical_orders": orders,
            "current_capacity": {
                "vehicles": 10,
                "drivers": 10,
                "deliveries_per_vehicle": 30
            },
            "external_factors": {
                "weather": {"condition": "clear"},
                "events": ["sports_game"],
                "holidays": []
            }
        }

        print("🚀 Executing demand forecasting...")
        response = requests.post(
            f"{API_BASE}/agents/demand-predictor/execute",
            json=data
        )

        result = response.json()

        if result['success']:
            agent_result = result['result']['result']
            if 'forecasts_generated' in agent_result:
                print(f"✅ Demand Forecasting Complete!")
                print(f"   Forecasts Generated: {agent_result['forecasts_generated']}")
                print(f"   Execution Time: {result['result']['execution_time']:.2f}s")

                # Show first 3 forecasts
                if 'result' in agent_result and 'forecasts' in agent_result['result']:
                    print(f"\n📈 Sample Forecasts:")
                    for forecast in agent_result['result']['forecasts'][:3]:
                        print(f"   {forecast['date']}: {forecast['predicted_demand']:.0f} orders")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_simulation():
    """Test scenario simulation"""
    print_section("6. SCENARIO SIMULATION")

    scenarios = ['high_demand', 'traffic_congestion', 'emergency']

    for scenario in scenarios:
        try:
            print(f"\n🎯 Testing scenario: {scenario}")
            response = requests.post(
                f"{API_BASE}/agents/simulate",
                json={'scenario': scenario, 'parameters': {}}
            )

            result = response.json()

            if result['success']:
                insights = result['insights']
                print(f"✅ Simulation Complete!")
                print(f"   Agents Activated: {insights['agents_activated']}")
                print(f"   Execution Time: {insights['execution_time']:.2f}s")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")

            sleep(1)  # Pause between simulations

        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_agent_activity():
    """Test agent activity logs"""
    print_section("7. AGENT ACTIVITY LOGS")

    try:
        response = requests.get(f"{API_BASE}/agents/activity?limit=5")
        data = response.json()

        if data['success']:
            print(f"📋 Recent Activity ({data['count']} logs):\n")
            for log in data['logs'][:5]:
                status = "✅" if log['success'] else "❌"
                print(f"{status} {log['agent_name']}")
                print(f"   Action: {log['action']}")
                print(f"   Time: {log['execution_time']:.2f}s")
                print(f"   Timestamp: {log['timestamp']}")
                print()
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_agent_statistics():
    """Test agent statistics"""
    print_section("8. AGENT STATISTICS")

    try:
        response = requests.get(f"{API_BASE}/agents/statistics")
        data = response.json()

        if data['success']:
            print("📊 Performance Statistics:\n")
            for agent_name, stats in data['statistics'].items():
                print(f"🤖 {agent_name}:")
                print(f"   Total Actions: {stats['total_actions']}")
                print(f"   Success Rate: {stats['success_rate']}%")
                print(f"   Avg Execution Time: {stats['avg_execution_time']}s")
                print()
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("\n" + "🤖 " + "="*58 + " 🤖")
    print("  AI AGENTS SYSTEM - COMPREHENSIVE TEST SUITE")
    print("🤖 " + "="*58 + " 🤖")

    # Test each component
    test_health_check()
    test_database_stats()
    test_agent_status()
    test_route_optimizer()
    sleep(1)
    test_demand_predictor()
    sleep(1)
    test_simulation()
    test_agent_activity()
    test_agent_statistics()

    print("\n" + "="*60)
    print("  ✅ ALL TESTS COMPLETED!")
    print("="*60 + "\n")
    print("💡 TIP: Visit http://localhost:5173/ai-agents to see the UI!")
    print()

if __name__ == "__main__":
    print("\n⚠️  Make sure the backend server is running on http://localhost:5000")
    input("Press Enter to start tests...")
    main()

