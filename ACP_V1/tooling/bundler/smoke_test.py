import requests
import sys

def test_endpoint(name, url, method="GET", payload=None, timeout=6):
    print(f"Testing {name}...", end=" ")
    try:
        if method == "GET":
            resp = requests.get(url, timeout=timeout)
        else:
            resp = requests.post(url, json=payload, timeout=timeout)

        if 200 <= resp.status_code < 300:
            print(f"✅ OK ({resp.status_code})")
            return True
        else:
            print(f"❌ FAIL ({resp.status_code})")
            print(f"   Response: {resp.text[:100]}...")
            return False
    except Exception as exc:
        print(f"❌ ERROR: {exc}")
        return False

print("=== SMOKE TEST: Directory Bundler & LM Studio ===\n")

bundler_ok = test_endpoint("Bundler Backend", "http://localhost:8000/api/status?uid=test", timeout=3)
lms_ok = test_endpoint("LM Studio (Direct)", "http://localhost:1234/v1/models", timeout=6)
proxy_ok = test_endpoint("Proxy Bridge", "http://localhost:8000/api/lmstudio/models?base_url=http://localhost:1234", timeout=8)

print("\n" + "=" * 40)
if bundler_ok and lms_ok and proxy_ok:
    print("🚀 SYSTEM HEALTHY - Ready for Development")
    sys.exit(0)
else:
    print("⚠ SYSTEM ISSUES DETECTED - Check logs")
    sys.exit(1)
