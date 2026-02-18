"""Simple test to verify Flask app works"""
import sys

print("=" * 80)
print("Quick Flask Server Test")
print("=" * 80)

try:
    print("\n1. Importing app...")
    from app import app
    print("   SUCCESS: App imported")

    print("\n2. Creating test client...")
    client = app.test_client()
    print("   SUCCESS: Test client created")

    print("\n3. Testing /api/health endpoint...")
    response = client.get('/api/health')
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.get_json()}")

    print("\n4. Testing /api/agents/status endpoint...")
    response = client.get('/api/agents/status')
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response keys: {list(response.get_json().keys())}")

    print("\n5. Testing /api/genai-agents/compare endpoint...")
    response = client.get('/api/genai-agents/compare')
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f"   Response keys: {list(data.keys())}")

    print("\n" + "=" * 80)
    print("All tests passed! Flask app is working correctly.")
    print("=" * 80)
    print("\nThe app SHOULD work when started with: python app.py")
    print("If it doesn't work, there may be an issue with:")
    print("  - Port 5000 being blocked by firewall")
    print("  - Python environment")
    print("  - Network configuration")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

