import sys
import os

print("Starting Flask app diagnostics...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

try:
    print("\nImporting Flask app...")
    from app import app, init_db

    print("Initializing database...")
    init_db()

    print("\nFlask app configuration:")
    print(f"  Debug: {app.debug}")
    print(f"  Testing: {app.testing}")

    print("\nRegistered routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if 'static' not in str(rule):
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"  {methods:10s} {rule.rule}")

    print("\nStarting Flask server...")
    print("Server will be available at http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

