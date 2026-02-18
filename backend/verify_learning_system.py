"""
Quick verification script to test if learning endpoints are working
Run this after restarting the server
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/genai-agents"

print("🔍 Quick Learning System Verification\n")
print("=" * 60)

# Test 1: Health Check
print("\n1. Health Check...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Server is healthy")
    else:
        print(f"   ❌ Server returned: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ Cannot connect to server: {e}")
    print("   💡 Make sure server is running on port 8000")
    exit(1)

# Test 2: Learning Statistics
print("\n2. Learning Statistics...")
try:
    response = requests.get(f"{BASE_URL}/learning/statistics", timeout=10)
    if response.status_code == 200:
        data = response.json()
        stats = data.get('statistics', {})
        print("   ✅ Learning system is working!")
        print(f"   📊 Total Decisions: {stats.get('total_decisions', 0)}")
        print(f"   🎯 Prediction Accuracy: {stats.get('prediction_accuracy', 0) * 100:.1f}%")
        print(f"   🧠 Patterns Learned: {stats.get('total_patterns', 0)}")
        print(f"   📈 Quality Improvement: {stats.get('quality_improvement', 0):+.1f}%")
    else:
        data = response.json()
        print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
        if 'not available' in str(data):
            print("   💡 The agent failed to initialize. Check Azure OpenAI credentials.")
        exit(1)
except Exception as e:
    print(f"   ❌ Request failed: {e}")
    exit(1)

# Test 3: Learned Patterns
print("\n3. Learned Patterns...")
try:
    response = requests.get(f"{BASE_URL}/learning/patterns?limit=3", timeout=10)
    if response.status_code == 200:
        data = response.json()
        patterns = data.get('patterns', [])
        print(f"   ✅ Found {len(patterns)} patterns")

        if patterns:
            print("\n   📚 Top Pattern:")
            p = patterns[0]
            print(f"   • Type: {p.get('pattern_type')}")
            print(f"   • Confidence: {p.get('confidence', 0) * 100:.0f}%")
            print(f"   • Observations: {p.get('observations', 0)}")
            print(f"   • Description: {p.get('description', 'N/A')[:70]}...")
    else:
        print(f"   ⚠️ Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Request failed: {e}")

print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETE!")
print("\n🎉 Self-Learning System is Ready for Demo!")
print("\n📚 Next steps:")
print("   1. Run full test: python test_learning_endpoints.py")
print("   2. Try simulation: POST to /learning/simulate-outcome")
print("   3. Check dashboard: Open frontend component")
print("\n" + "=" * 60)

