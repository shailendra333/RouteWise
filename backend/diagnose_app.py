"""Diagnostic script to check what's happening with Flask app"""
import sys
import traceback

print("=" * 80)
print("Flask App Diagnostic")
print("=" * 80)
print()

# Test imports
print("1. Testing imports...")
try:
    from agents_api import agents_bp
    print("   [OK] agents_api imported successfully")
    print(f"   Blueprint name: {agents_bp.name}")
    print(f"   URL prefix: {agents_bp.url_prefix}")
except Exception as e:
    print(f"   [FAIL] Failed to import agents_api: {e}")
    traceback.print_exc()

try:
    from ai_agents.genai_agents_api import genai_agents_bp
    print("   [OK] genai_agents_api imported successfully")
    print(f"   Blueprint name: {genai_agents_bp.name}")
    print(f"   URL prefix: {genai_agents_bp.url_prefix}")
except Exception as e:
    print(f"   [FAIL] Failed to import genai_agents_api: {e}")
    traceback.print_exc()

print()
print("2. Testing Flask app creation...")
try:
    from app import app
    print("   [OK] Flask app imported successfully")

    print()
    print("3. Checking registered routes...")
    print("   " + "-" * 76)
    route_count = 0
    for rule in app.url_map.iter_rules():
        if 'static' not in str(rule.rule):
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"   {methods:10s} {rule.rule}")
            route_count += 1
    print("   " + "-" * 76)
    print(f"   Total routes (excluding static): {route_count}")
    
    print()
    print("4. Checking blueprints...")
    for bp_name, bp in app.blueprints.items():
        print(f"   [OK] Blueprint: {bp_name} (prefix: {bp.url_prefix})")

    print()
    print("5. Testing route lookup...")
    test_routes = ['/api/health', '/api/agents/status', '/api/genai-agents/compare']
    for route in test_routes:
        try:
            with app.test_request_context(route):
                from flask import request
                adapter = app.url_map.bind('localhost')
                endpoint, values = adapter.match(route)
                print(f"   [OK] {route} -> {endpoint}")
        except Exception as e:
            print(f"   [FAIL] {route} -> {e}")

except Exception as e:
    print(f"   [FAIL] Failed to import Flask app: {e}")
    traceback.print_exc()

print()
print("=" * 80)
print("Diagnostic Complete")
print("=" * 80)

