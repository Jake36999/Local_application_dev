# Directory Bundler v4.5 - Setup Guide

## Quick Setup

### 1. Install Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt
```

This will install:
- `requests` - HTTP library for LM Studio integration
- `types-requests` - Type stubs for mypy (fixes the import-untyped warning)
- `pytest` - Testing framework
- `pytest-cov` - Test coverage reports

### 2. Verify Installation

```powershell
# Check Python version (3.10+ recommended)
python --version

# Verify packages are installed
pip list | Select-String "requests|pytest"
```

Expected output:
```
pytest         7.4.0
pytest-cov     4.1.0
requests       2.31.0
types-requests 2.31.0
```

### 3. Run Type Checking (Optional)

```powershell
# Install mypy if not already installed
pip install mypy

# Run type checking with configuration
mypy Directory_bundler_v4.5.py --config-file mypy.ini
```

The mypy.ini file is configured to:
- Enable `check_untyped_defs` (fixes the annotation-unchecked warnings)
- Ignore missing imports for optional dependencies
- Use Python 3.10 type checking rules

### 4. Run Tests

```powershell
# Run all tests
pytest test_bundler.py -v

# Run with coverage report
pytest test_bundler.py --cov=. --cov-report=html

# Open coverage report
.\htmlcov\index.html
```

## Resolving Mypy Warnings

### Warning 1: "Library stubs not installed for requests"
**Solution:** `pip install types-requests` ✅ (included in requirements.txt)

### Warning 2: "annotation-unchecked" warnings
**Solution:** Added `check_untyped_defs = True` in mypy.ini ✅

### Warning 3: "Cannot find pytest"
**Solution:** `pip install pytest` ✅ (included in requirements.txt)

## Usage After Setup

### Run the Bundler:
```powershell
python Directory_bundler_v4.5.py
```

### Run Tests:
```powershell
pytest test_bundler.py -v
```

### Type Check:
```powershell
mypy Directory_bundler_v4.5.py --config-file mypy.ini
```

## Troubleshooting

### Issue: "pip is not recognized"
**Solution:** Add Python to PATH or use: `python -m pip install -r requirements.txt`

### Issue: Import errors in test_bundler.py
**Solution:** Ensure you're in the correct directory where all .py files are located

### Issue: LM Studio connection fails
**Solution:** LM Studio is optional. If not using AI features, select "Disable" during configuration

## Optional Features

### LM Studio Integration
If you want AI-powered analysis:
1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model in LM Studio
3. Start the local server (default: http://localhost:1234)
4. Enable LM Studio in bundler configuration

### LM Studio Performance Tuning (Speculative Decoding)
For faster local responses, enable speculative decoding in LM Studio and load a small draft model alongside your main model:
1. Start the LM Studio server (or use `ENABLE_LMS_BOOTSTRAP=1` in `Start_Web_Interface.bat` to auto-start).
2. In LM Studio, open **Settings → Experimental → Speculative Decoding** and toggle it on.
3. Load your primary model (e.g., `nous-hermes-2-mixtral`) and also load a smaller draft model (e.g., `LM_BOOTSTRAP_MODEL=lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF` or `astral-4b-coder`).
4. If using the bootstrap script, set `LM_BOOTSTRAP_MODEL` to the draft model and keep your main model loaded manually; the script handles server start and model load.
5. Keep both models loaded; LM Studio will automatically pair them for speculative decoding and lower latency.

### RAG System (Advanced)
If using the RAG system in Directory_bundler_test_folder:
```powershell
pip install pymongo chromadb
```

## Development Mode

For development with hot-reload:
```powershell
# Install development dependencies
pip install watchdog

# Or use pytest in watch mode
pytest-watch test_bundler.py
```

## Production Deployment

For production environments:
```powershell
# Install only production dependencies (no dev/test)
pip install requests types-requests

# Run with production settings
python Directory_bundler_v4.5.py
```

---

**All warnings should now be resolved after running:** `pip install -r requirements.txt`
