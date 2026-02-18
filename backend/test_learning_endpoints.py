"""
Test script for self-learning endpoints
Run this after starting the backend server
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/genai-agents"

def test_learning_endpoints():
    """Test all learning-related endpoints"""
    
    print("🧪 Testing Self-Learning Endpoints\n")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   Status: {response.json().get('status')}")
        else:
            print(f"   ⚠️ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Learning Statistics
    print("\n2️⃣ Testing Learning Statistics...")
    try:
        response = requests.get(f"{BASE_URL}/learning/statistics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print("   ✅ Statistics retrieved successfully")
            print(f"   📊 Total Decisions: {stats.get('total_decisions', 0)}")
            print(f"   🎯 Prediction Accuracy: {stats.get('prediction_accuracy', 0) * 100:.1f}%")
            print(f"   🧠 Total Patterns: {stats.get('total_patterns', 0)}")
            print(f"   📈 Quality Improvement: {stats.get('quality_improvement', 0):+.1f}%")
        else:
            print(f"   ⚠️ Status code: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Learned Patterns
    print("\n3️⃣ Testing Learned Patterns...")
    try:
        response = requests.get(f"{BASE_URL}/learning/patterns?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            patterns = data.get('patterns', [])
            print(f"   ✅ Retrieved {len(patterns)} patterns")
            
            for i, pattern in enumerate(patterns[:3], 1):
                print(f"\n   Pattern {i}:")
                print(f"   • Type: {pattern.get('pattern_type')}")
                print(f"   • Confidence: {pattern.get('confidence', 0) * 100:.0f}%")
                print(f"   • Observations: {pattern.get('observations', 0)}")
                print(f"   • Avg Improvement: {pattern.get('avg_improvement_minutes', 0):.1f} min")
                print(f"   • Description: {pattern.get('description', 'N/A')[:80]}...")
        else:
            print(f"   ⚠️ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Learning Insights
    print("\n4️⃣ Testing Learning Insights...")
    try:
        response = requests.get(f"{BASE_URL}/route-optimizer/learning-insights", timeout=5)
        if response.status_code == 200:
            data = response.json()
            insights = data.get('insights', {})
            print("   ✅ Insights retrieved successfully")
            print(f"   Status: {insights.get('learning_status', 'unknown')}")
            print(f"   Top Patterns: {len(insights.get('top_patterns', []))}")
        else:
            print(f"   ⚠️ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 5: Simulate Outcome
    print("\n5️⃣ Testing Simulate Outcome...")
    try:
        # First, we need to make a decision to have an active decision_id
        # For testing, we'll just try to simulate directly
        response = requests.post(
            f"{BASE_URL}/learning/simulate-outcome",
            json={"success": True},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Outcome simulation successful")
            print(f"   Learning Triggered: {data.get('learning_triggered', False)}")
            outcome = data.get('outcome', {})
            print(f"   Time Saving: {outcome.get('actual_time_saving', 0)} min")
            print(f"   Cost Saving: ${outcome.get('actual_cost_saving', 0):.2f}")
        else:
            print(f"   ⚠️ Status code: {response.status_code}")
            print(f"   Note: This is expected if no recent decision was made")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("\n💡 Tip: If you see errors, make sure:")
    print("   1. Backend server is running (python app.py)")
    print("   2. Learning data is seeded (python seed_learning_data.py)")
    print("   3. Azure OpenAI credentials are configured")
    print("\n📚 See SELF_LEARNING_QUICK_START.md for more info")


if __name__ == "__main__":
    print("\n⏳ Waiting for server to be ready...")
    time.sleep(2)
    test_learning_endpoints()

