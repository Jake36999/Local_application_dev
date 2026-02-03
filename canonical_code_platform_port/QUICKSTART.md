# Canonical Code Platform - 5-Minute Quickstart

**Get from zero to microservice extraction in 5 minutes**

> **After this quickstart:** Read [WORKFLOWS.md](WORKFLOWS.md) for detailed command reference  
> **For system design:** See [ARCHITECTURE.md](ARCHITECTURE.md)  
> **For advanced usage:** Check [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md)

---

## ⏱️ What You'll Accomplish

By the end of this guide, you'll:
1. ✅ Install the platform (30 seconds)
2. ✅ Analyze your first file (1 minute)
3. ✅ View results in professional UI (1 minute)
4. ✅ Extract a microservice (2 minutes)
5. ✅ Verify system health (30 seconds)

**Total Time:** ~5 minutes

---

## 📋 Prerequisites

- **Python 3.11+** installed
- **5 minutes** of your time
- **Optional:** Docker (for deployment testing)

**That's it!** No external dependencies required for core functionality.

---

## 🚀 Step 1: Install (30 seconds)

### Option A: Clone Repository
```bash
git clone <repo-url>
cd canonical_code_platform__v2
```

### Option B: Download ZIP
1. Download and extract ZIP
2. Open terminal in extracted folder

### Install UI (Optional)
```bash
pip install streamlit
```

**✓ Checkpoint:** You should see `workflows/workflow_ingest.py` in your directory:
```bash
ls workflows/workflow_ingest.py
# or on Windows:
dir workflows/workflow_ingest.py
```

---

## 🔍 Step 2: Analyze Your First File (1 minute)

### Create a Test File

```bash
# Linux/Mac
cat > test_calculator.py << 'EOF'
"""Simple calculator module for testing"""

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b

def multiply(x: int, y: int) -> int:
    """Multiply two numbers.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Product of x and y
    """
    return x * y

class Calculator:
    """Basic calculator with history tracking."""
    
    def __init__(self):
        """Initialize calculator with empty history."""
        self.history = []
    
    def calculate(self, operation: str, a: int, b: int) -> int:
        """Perform calculation and track in history.
        
        Args:
            operation: Operation to perform ('add' or 'multiply')
            a: First operand
            b: Second operand
            
        Returns:
            Result of calculation
        """
        if operation == 'add':
            result = add_numbers(a, b)
        elif operation == 'multiply':
            result = multiply(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.history.append((operation, a, b, result))
        return result
EOF
```

**Windows PowerShell:**
```powershell
@'
"""Simple calculator module for testing"""

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y

class Calculator:
    """Basic calculator with history tracking."""
    
    def __init__(self):
        self.history = []
    
    def calculate(self, operation: str, a: int, b: int) -> int:
        """Perform calculation and track in history."""
        if operation == 'add':
            result = add_numbers(a, b)
        elif operation == 'multiply':
            result = multiply(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.history.append((operation, a, b, result))
        return result
'@ | Out-File -Encoding utf8 test_calculator.py
```

### Run the Analysis

```bash
python workflows/workflow_ingest.py test_calculator.py
```

**Expected Output:**
```
========================================
Canonical Code Platform - Ingestion Workflow
========================================

Target file: test_calculator.py

Phase 1/5: Foundation ...................... ✓ SUCCESS
Phase 2/5: Symbol Tracking ................. ✓ SUCCESS
Phase 3/5: Call Graph ...................... ⊘ SKIPPED
Phase 4/5: Cut Analysis .................... ✓ SUCCESS
Phase 5/5: Governance Validation ........... ✓ SUCCESS

========================================
WORKFLOW COMPLETE: 4/5 phases succeeded
========================================

✓ canon.db updated with 5 components
✓ governance_report.txt (1523 chars)
✓ governance_report.json (machine-readable)
```

**✓ Checkpoint:** You should see `canon.db` created:
```bash
ls canon.db
```

**⏱️ Time Elapsed:** 1 minute 30 seconds

---

## 🎨 Step 3: View Results in UI (1 minute)

### Launch the UI

```bash
streamlit run ui_app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

### Explore the 5 Tabs

#### 🏠 **Dashboard Tab** (Start Here)
- **System Metrics**: 1 file ingested, 5 components
- **Phase Status**: 7 green badges showing operational phases
- **Recent Activity**: Your test_calculator.py ingestion

#### 📊 **Analysis Tab**
1. Select "test_calculator.py" from dropdown
2. Select "add_numbers" component
3. **Left pane:** See your source code
4. **Right pane:** See:
   - Cut analysis score (likely 0.85)
   - Tier: LOCAL_UTILITY
   - Zero governance violations (well-documented!)

#### 🚀 **Extraction Tab**
- **Gate Status:** ✅ PASS (0 blocking errors)
- **Ready for Extraction:** 2 components
- **Candidates:** add_numbers, multiply

#### 📈 **Drift History Tab**
- Shows version 1 of test_calculator.py
- No drift yet (first ingestion)

#### ⚙️ **Settings Tab**
- Database stats
- Workflow command reference
- System information

**✓ Checkpoint:** Dashboard shows "1 file ingested, 5 components"

**⏱️ Time Elapsed:** 2 minutes 30 seconds

---

## 🚀 Step 4: Extract a Microservice (2 minutes)

### Run Extraction

```bash
# Close UI first (Ctrl+C) to avoid database lock
python workflows/workflow_extract.py
```

**Expected Output:**
```
========================================
Canonical Code Platform - Extraction Workflow
========================================

Checking governance gates...

✓ GATE STATUS: PASS
  0 blocking errors found

Identifying extraction candidates...
  2 candidates found (score > 0.5, no errors)

Generating microservice artifacts...

Generated Services:
--------------------------------------------------
📦 add_numbers (Tier: LOCAL_UTILITY, Score: 0.85)
   Files:
     - extracted_services/add_numbers/interface.py
     - extracted_services/add_numbers/api.py
     - extracted_services/add_numbers/Dockerfile
     - extracted_services/add_numbers/deployment.yaml
     - extracted_services/add_numbers/requirements.txt
     - extracted_services/add_numbers/README.md

📦 multiply (Tier: LOCAL_UTILITY, Score: 0.75)
   Files: [6 files]

========================================
EXTRACTION COMPLETE
========================================

✓ 2 services generated
✓ 12 total files created
```

### Explore Generated Files

```bash
ls extracted_services/add_numbers/
```

**You'll see:**
- `interface.py` - Abstract base class
- `api.py` - FastAPI endpoints
- `Dockerfile` - Container build
- `deployment.yaml` - Kubernetes config
- `requirements.txt` - Dependencies
- `README.md` - Documentation

### View the API

```bash
cat extracted_services/add_numbers/api.py
```

**You'll see:**
```python
"""
FastAPI service for add_numbers
Auto-generated by Canonical Code Platform
"""

from fastapi import FastAPI
from pydantic import BaseModel
from interface import AddNumbersInterface

app = FastAPI(
    title="add_numbers Service",
    description="Add two numbers together.",
    version="1.0.0"
)

class AddNumbersRequest(BaseModel):
    a: int
    b: int

class AddNumbersResponse(BaseModel):
    result: int

@app.post("/add_numbers", response_model=AddNumbersResponse)
def add_numbers_endpoint(request: AddNumbersRequest):
    """Add two numbers together."""
    result = request.a + request.b
    return AddNumbersResponse(result=result)
```

**✓ Checkpoint:** You should see 2 folders in `extracted_services/`

**⏱️ Time Elapsed:** 4 minutes 30 seconds

---

## ✅ Step 5: Verify System Health (30 seconds)

### Run Verification

```bash
python workflows/workflow_verify.py
```

**Expected Output:**
```
========================================
Canonical Code Platform - System Verification
========================================

Phase 1: Foundation .................... ✓ PASS
Phase 2: Symbol Tracking ............... ✓ PASS
Phase 3: Call Graph .................... ✗ FAIL (expected)
Phase 4: Semantic Rebuild .............. ✓ PASS
Phase 5: Comment Metadata .............. ✗ FAIL (expected)
Phase 6: Drift Detection ............... ✓ PASS
Phase 7: Governance .................... ✓ PASS

========================================
VERIFICATION SUMMARY
========================================

Overall Status: ⚠ NEEDS ATTENTION
  ✓ 5 phases operational
  ✗ 2 phases need schema updates

System Verdict: OPERATIONAL (with known gaps)
```

**Note:** Phase 3 & 5 failures are EXPECTED (schema evolution in progress)

**✓ Checkpoint:** You see "5 phases operational"

**⏱️ Time Elapsed:** 5 minutes

---

## 🎉 Congratulations!

You've successfully:
- ✅ Analyzed a Python file
- ✅ Viewed results in professional UI
- ✅ Extracted 2 microservices
- ✅ Verified system health

---

## 🎯 Next Steps

### Option 1: Test Deployment (Requires Docker)

```bash
cd extracted_services/add_numbers
docker build -t add-numbers:latest .
docker run -p 8000:8000 add-numbers:latest

# In another terminal:
curl http://localhost:8000/docs
```

### Option 2: Analyze Your Real Code

```bash
python workflows/workflow_ingest.py path/to/your/code.py
streamlit run ui_app.py
```

### Option 3: Try Drift Detection

```bash
# Modify test_calculator.py (add a new function)
echo "def subtract(a, b): return a - b" >> test_calculator.py

# Re-ingest
python workflows/workflow_ingest.py test_calculator.py

# View drift in UI
streamlit run ui_app.py
# Go to Drift History tab
```

### Option 4: Batch Analysis

```bash
# Linux/Mac
for file in src/*.py; do
    python workflows/workflow_ingest.py "$file"
done

# Windows PowerShell
Get-ChildItem src/*.py | ForEach-Object {
    python workflows/workflow_ingest.py $_.FullName
}
```

---

## ❓ Troubleshooting

### Issue: "No module named 'streamlit'"

**Solution:**
```bash
pip install streamlit
```

### Issue: "Database is locked"

**Solution:**
```bash
# Close the UI (Ctrl+C in Streamlit terminal)
# Wait 5 seconds
# Retry your command
```

### Issue: "No extraction candidates"

**Possible causes:**
1. **Governance violations**: Check `governance_report.txt`
2. **Low scores**: View Analysis tab in UI
3. **No suitable functions**: Add more functions to your file

**Solution:**
```bash
cat governance_report.txt
# Fix any ERROR-level violations
# Re-run: python workflows/workflow_ingest.py test_calculator.py
```

### Issue: "Gate BLOCKED"

**Solution:**
```bash
# Check report
cat governance_report.txt

# Common fixes:
# - Add docstrings: """Description here"""
# - Remove unused imports
# - Simplify complex functions
# - Replace magic numbers with constants

# Re-ingest after fixes
python workflows/workflow_ingest.py test_calculator.py
```

---

## 📚 Learn More

- **[WORKFLOWS.md](WORKFLOWS.md)** - Comprehensive workflow documentation
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migrating from old scripts
- **[README.md](README.md)** - Project overview
- **[VERIFICATION_PLAN.md](VERIFICATION_PLAN.md)** - Implementation status

---

## 🐛 Found a Bug?

1. Check [WORKFLOWS.md](WORKFLOWS.md) error handling section
2. Run verification: `python workflows/workflow_verify.py`
3. Check database: `sqlite3 canon.db ".tables"`

---

**Welcome to the Canonical Code Platform!** 🚀

**Last Updated:** February 2026  
**Version:** 2.0 (Quickstart for Workflow Consolidation)
