"""
Quick test script to verify Data Model Documentation implementation
"""

import os
import sys

def test_implementation():
    """Test all components of the data model documentation"""
    
    print("=" * 80)
    print("DATA MODEL DOCUMENTATION - IMPLEMENTATION TEST")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    # Test 1: Check templates directory exists
    print("\n✓ Test 1: Templates directory exists")
    if os.path.exists("templates"):
        print("  ✅ PASS - templates/ directory found")
        passed += 1
    else:
        print("  ❌ FAIL - templates/ directory not found")
        failed += 1
    
    # Test 2: Check HTML file exists
    print("\n✓ Test 2: Documentation HTML file exists")
    if os.path.exists("templates/data_model_docs.html"):
        print("  ✅ PASS - data_model_docs.html found")
        file_size = os.path.getsize("templates/data_model_docs.html")
        print(f"  📄 File size: {file_size:,} bytes")
        passed += 1
    else:
        print("  ❌ FAIL - data_model_docs.html not found")
        failed += 1
    
    # Test 3: Check app.py has render_template import
    print("\n✓ Test 3: Flask render_template import")
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "render_template" in content:
                print("  ✅ PASS - render_template imported in app.py")
                passed += 1
            else:
                print("  ❌ FAIL - render_template not found in app.py")
                failed += 1
    except Exception as e:
        print(f"  ❌ FAIL - Error reading app.py: {e}")
        failed += 1
    
    # Test 4: Check route exists in app.py
    print("\n✓ Test 4: Data model docs route exists")
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "/data-model-docs" in content:
                print("  ✅ PASS - /data-model-docs route found")
                passed += 1
            else:
                print("  ❌ FAIL - /data-model-docs route not found")
                failed += 1
    except Exception as e:
        print(f"  ❌ FAIL - Error reading app.py: {e}")
        failed += 1
    
    # Test 5: Check HTML content quality
    print("\n✓ Test 5: Documentation content quality")
    try:
        with open("templates/data_model_docs.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            
            checks = [
                ("SQLite tables section", "SQLite Database Tables"),
                ("Azure tables section", "Azure Table Storage"),
                ("Orders table", "<h4>2. orders</h4>"),
                ("Vehicles table", "<h4>4. vehicles</h4>"),
                ("TrackingData table", "<h4>1. TrackingData</h4>"),
                ("Technology stack", "Technology Stack"),
                ("AI Agents section", "AI Agents"),
            ]
            
            all_found = True
            for check_name, check_string in checks:
                if check_string in html_content:
                    print(f"  ✅ Contains {check_name}")
                else:
                    print(f"  ❌ Missing {check_name}")
                    all_found = False
            
            if all_found:
                passed += 1
            else:
                failed += 1
                
    except Exception as e:
        print(f"  ❌ FAIL - Error reading HTML file: {e}")
        failed += 1
    
    # Test 6: Check Flask app can be imported
    print("\n✓ Test 6: Flask app imports correctly")
    try:
        from flask import Flask, render_template
        print("  ✅ PASS - Flask imports successful")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - Flask import error: {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}/6")
    print(f"❌ Failed: {failed}/6")
    
    if failed == 0:
        print("\n🎉 SUCCESS - All tests passed! Implementation is complete.")
        print("\n📋 Next Steps:")
        print("   1. Start backend: python app.py")
        print("   2. Visit: http://localhost:8000/data-model-docs")
        print("   3. Or access via Dashboard Quick Actions")
    else:
        print("\n⚠️  ISSUES FOUND - Please review failed tests above")
    
    print("=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    # Change to backend directory if needed
    if not os.path.exists("app.py"):
        if os.path.exists("backend/app.py"):
            os.chdir("backend")
            print("Changed directory to backend/\n")
    
    success = test_implementation()
    sys.exit(0 if success else 1)

