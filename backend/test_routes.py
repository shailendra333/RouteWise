"""Test script to check Flask routes"""
import sys
print("Testing Flask app routes...")

try:
    from app import app
    print("\n✅ Flask app imported successfully\n")
    
    print("Registered Routes:")
    print("-" * 80)
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{methods:10s} {rule.rule:50s} -> {rule.endpoint}")
    print("-" * 80)
    
    # Check for specific routes
    routes_to_check = [
        '/api/agents/status',
        '/api/agents/health',
        '/api/genai-agents/compare',
        '/api/genai-agents/status',
        '/api/genai-agents/health'
    ]
    
    print("\nChecking specific routes:")
    for route in routes_to_check:
        found = any(str(rule.rule) == route for rule in app.url_map.iter_rules())
        status = "✅ FOUND" if found else "❌ NOT FOUND"
        print(f"  {status}: {route}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

