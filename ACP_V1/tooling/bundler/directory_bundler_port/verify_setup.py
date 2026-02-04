"""
Quick verification script to check if all dependencies are installed correctly.
"""
import sys

def check_imports():
    """Verify all required packages can be imported."""
    print("Checking Directory Bundler dependencies...")
    print("-" * 50)
    
    packages = [
        ("requests", "HTTP library for LM Studio"),
        ("pytest", "Testing framework"),
        ("pytest_cov", "Coverage plugin"),
    ]
    
    all_ok = True
    for package, description in packages:
        try:
            __import__(package)
            print(f"✅ {package:20} - {description}")
        except ImportError as e:
            print(f"❌ {package:20} - MISSING ({e})")
            all_ok = False
    
    # Check types-requests via pip (it's a stub package, not directly importable)
    import subprocess
    try:
        result = subprocess.run(['pip', 'show', 'types-requests'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {'types-requests':20} - Type stubs for mypy")
        else:
            print(f"❌ {'types-requests':20} - MISSING")
            all_ok = False
    except Exception:
        print(f"⚠️  {'types-requests':20} - Could not verify")
    
    print("-" * 50)
    
    if all_ok:
        print("\n🎉 All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Restart VS Code to refresh mypy type checking")
        print("2. Run tests: pytest test_bundler.py -v")
        print("3. Run bundler: python Directory_bundler_v4.5.py")
        return 0
    else:
        print("\n⚠️  Some dependencies are missing.")
        print("Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(check_imports())
