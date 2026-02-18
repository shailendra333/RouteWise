"""
Test script to verify Agent Comparison endpoints
Run this before starting the frontend to ensure backend is working
"""

import requests
import json
from colorama import init, Fore, Style

init()

def test_endpoint(name, url, expected_status=200):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"{Fore.GREEN}✅ PASS{Style.RESET_ALL} - {name}")
            print(f"    Status: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                print(f"    Response: {json.dumps(data, indent=2)[:200]}...")
            return True
        else:
            print(f"{Fore.RED}❌ FAIL{Style.RESET_ALL} - {name}")
            print(f"    Expected: {expected_status}, Got: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}❌ FAIL{Style.RESET_ALL} - {name}")
        print(f"    Error: Cannot connect to backend. Is it running on http://localhost:5000?")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ FAIL{Style.RESET_ALL} - {name}")
        print(f"    Error: {str(e)}")
        return False

def main():
    print("=" * 80)
    print(f"{Fore.CYAN}Testing Agent Comparison Dashboard Endpoints{Style.RESET_ALL}")
    print("=" * 80)
    print()

    base_url = "http://localhost:5000"

    tests = [
        ("Backend Health", f"{base_url}/api/health"),
        ("Traditional Agents Status", f"{base_url}/api/agents/status"),
        ("Traditional Agents Health", f"{base_url}/api/agents/health"),
        ("GenAI Agents Status", f"{base_url}/api/genai-agents/status"),
        ("GenAI Agents Health", f"{base_url}/api/genai-agents/health"),
        ("Agent Comparison", f"{base_url}/api/genai-agents/compare"),
    ]

    results = []
    for name, url in tests:
        print()
        result = test_endpoint(name, url)
        results.append((name, result))

    print()
    print("=" * 80)
    print(f"{Fore.CYAN}Test Summary{Style.RESET_ALL}")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Fore.GREEN}✅ PASS{Style.RESET_ALL}" if result else f"{Fore.RED}❌ FAIL{Style.RESET_ALL}"
        print(f"{status} - {name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print(f"{Fore.GREEN}✅ All tests passed! Agent Comparison Dashboard should work.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Some tests failed. Backend may not be running or configured correctly.{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}To start the backend:{Style.RESET_ALL}")
        print("  cd backend")
        print("  start-backend.bat")

if __name__ == "__main__":
    main()

