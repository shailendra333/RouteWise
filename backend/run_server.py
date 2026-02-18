"""
Simple server runner that catches and displays all errors
"""
import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("STARTING FLASK SERVER")
print("=" * 80)

try:
    # Import the app
    print("\n1. Importing Flask app...")
    from app import app, init_db, logger
    print("   [OK] Flask app imported")

    # Initialize database
    print("\n2. Initializing database...")
    init_db()
    print("   [OK] Database initialized")

    # Check blueprints
    print("\n3. Registered Blueprints:")
    for bp_name in app.blueprints:
        print(f"   - {bp_name}")

    # List all routes
    print("\n4. Available Routes (first 10):")
    for i, rule in enumerate(list(app.url_map.iter_rules())[:10]):
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"   {methods:10s} {rule.rule}")

    print("\n" + "=" * 80)
    print("SERVER STARTING ON http://0.0.0.0:5000")
    print("=" * 80)
    print("\nServer is ready! Press Ctrl+C to stop.\n")

    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)

except KeyboardInterrupt:
    print("\n\nServer stopped by user.")
    sys.exit(0)

except Exception as e:
    print(f"\n[FATAL ERROR] Server failed to start: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

