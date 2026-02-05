"""Quick smoke test for Directory Bundler + LM Studio proxy.

Usage:
  python test_proxy.py

Env overrides:
  LM_MODEL: model id (default astral-4b-coder)
  LM_BASE_URL: LM Studio base (default http://localhost:1234)
  PROXY_URL: Bundler base (default http://localhost:8000)
"""
import os
import sys
import json
import requests

MODEL = os.environ.get("LM_MODEL", "astral-4b-coder")
LM_BASE = os.environ.get("LM_BASE_URL", "http://localhost:1234")
PROXY = os.environ.get("PROXY_URL", "http://localhost:8000")

def pretty(name, ok, detail=""):
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" - {detail}" if detail else ""))

def do_request(name, method, url, **kwargs):
    # Prefer caller-supplied timeout; default to 10s
    if "timeout" not in kwargs:
        kwargs["timeout"] = 10
    try:
        resp = requests.request(method, url, **kwargs)
        return resp
    except Exception as exc:
        pretty(name, False, f"exception: {exc}")
        return None

def main():
    # 1) Bundler status
    resp = do_request("bundler status", "get", f"{PROXY}/api/status?uid=test")
    if not resp:
        return 1
    pretty("bundler status", resp.ok, f"{resp.status_code}")

    # 2) LM Studio direct models
    resp = do_request("lmstudio models", "get", f"{LM_BASE}/v1/models")
    if not resp:
        return 1
    pretty("lmstudio models", resp.ok, f"{resp.status_code}")

    # 3) Proxy load
    load_body = {
        "action": "load",
        "model": MODEL,
        "base_url": LM_BASE,
        "context_length": 8192,
        "gpu_offload_ratio": 0.5,
        "ttl": 3600,
        "identifier": "smoke-test"
    }
    resp = do_request("proxy load", "post", f"{PROXY}/api/lmstudio/model", json=load_body, timeout=30)
    if not resp:
        return 1
    pretty("proxy load", resp.ok, f"{resp.status_code} {resp.text}")

    # 4) Proxy unload
    unload_body = {"action": "unload", "model": MODEL, "base_url": LM_BASE}
    resp = do_request("proxy unload", "post", f"{PROXY}/api/lmstudio/model", json=unload_body, timeout=30)
    if not resp:
        return 1
    pretty("proxy unload", resp.ok, f"{resp.status_code} {resp.text}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
