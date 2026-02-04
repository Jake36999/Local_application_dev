# LLM Workflow Builder - Quick Start

**5-minute setup guide**

---

## Prerequisites

### 1. LM Studio Installation

Download and install LM Studio from: https://lmstudio.ai/

### 2. Load a Model

1. Open LM Studio
2. Select a model (recommend: **Mistral 7B** or **Llama 2**)
3. Click **Load Model**
4. Wait for it to fully load

### 3. Start Local Server

1. In LM Studio, go to **Local Server** tab
2. Set to: **0.0.0.0:1234**
3. Click **Start Server**
4. You should see: **Server running at...**

### 4. Verify Connection

```bash
# Test connection (from project directory)
curl http://192.168.0.190:1234/v1/models
```

You should get a JSON response with model info.

---

## Installation

### 1. Install Python Packages

```bash
pip install pyyaml requests streamlit
```

### 2. Create Workflows Directory

```bash
mkdir workflows
```

### 3. Verify Files Exist

```bash
# Check these files are present:
ls -la
# Should see:
# - llm_integration.py
# - workflow_schema.py  
# - workflow_builder.py
# - llm_workflow_ui.py
# - ui_app.py
```

---

## Startup

### Start the System

```bash
# Terminal 1: Start Streamlit UI
streamlit run ui_app.py

# Terminal 2 (optional): Start orchestrator
python orchestrator.py --init
```

### Access UI

1. Open browser: **http://localhost:8501**
2. Click on **🤖 LLM Builder** tab
3. You should see the two-panel interface

---

## First Workflow

### Step 1: Write Your Requirements

In the **Left Panel**, type:

```
Extract all Python functions from source files and check 
them against governance rules, then generate a report
```

### Step 2: Select Components

In **Available Components**, select:
- ✓ file_ingester
- ✓ code_extractor
- ✓ rule_engine
- ✓ report_generator

### Step 3: Generate

Click **🚀 Generate with AI**

Wait 10-30 seconds for the LLM to respond...

### Step 4: Review Suggestions

**Left Panel** shows:
- ✍️ Reasoning: Why these components
- 📋 Steps: Pipeline sequence
- ⚙️ Parameters: Recommended settings

### Step 5: Accept

Click **✅ Accept Suggestion**

Your workflow now appears in **Right Panel**!

### Step 6: Review YAML

**Bottom Section** shows:

```yaml
version: "1.0.0"
name: "my_workflow"

steps:
  - id: "01"
    name: "Ingest Files"
    component: "file_ingester"
    parameters:
      source_path: "/code"
      recursive: true
    outputs: ["raw_files"]
  
  - id: "02"
    name: "Extract Code"
    component: "code_extractor"
    inputs: ["raw_files"]
    outputs: ["extracted_code"]
    ...
```

### Step 7: Validate

Check **Validation** section:
- ✅ Green = Valid workflow
- ⚠️ Yellow = Best practice warnings
- ❌ Red = Errors to fix

### Step 8: Save

Click **💾 Save Workflow**

Saved to: `workflows/my_workflow.yaml`

---

## Common Tasks

### Regenerate Different Suggestion

1. Change **User Requirement** text
2. Click **🔄 Regenerate**
3. Try different requirements each time

### Edit Generated Workflow

1. In **Right Panel**, click **✏️** on a step
2. Modify parameters
3. Changes appear in YAML preview

### Add More Steps

1. Click **➕ Add Step**
2. Select component
3. Enter parameters
4. Click **Add Step**

### Load Saved Workflow

1. Click **📂 Load from File**
2. Select YAML from `workflows/` folder
3. Workflow appears in builder

### Export Workflow

1. Click **📋 Copy YAML**
2. YAML copied to clipboard
3. Paste into editor/file

---

## Configuration

### Change LM Studio Endpoint

Edit `llm_integration.py`:

```python
class LLMConfig:
    endpoint: str = "http://YOUR_IP:1234"  # Change here
    model: str = "local-model"
    temperature: float = 0.7
```

### Change Model Temperature

Lower = More deterministic responses (0.3)  
Higher = More creative responses (0.9)

```python
config = LLMConfig(temperature=0.5)
client = LMStudioClient(config)
```

### Adjust Timeout

If LM Studio is slow, increase timeout:

```python
config = LLMConfig(timeout=120)  # 120 seconds
```

---

## Troubleshooting

### "LM Studio not available"

**Check**:
1. LM Studio is running
2. Server is started (not just app)
3. Model is loaded
4. Correct IP: `192.168.0.190:1234`

**Test**:
```bash
curl http://192.168.0.190:1234/v1/models
```

### "No suggestions generated"

**Try**:
1. Write more specific requirements
2. Select specific components
3. Check LM Studio logs for errors
4. Try different model

### "YAML validation failed"

**Fix**:
1. Check component names are spelled correctly
2. Required parameters must have values
3. Input variable names must match previous outputs

### "ModuleNotFoundError: No module named 'yaml'"

**Fix**:
```bash
pip install pyyaml
```

### "Permission denied: workflows/"

**Fix**:
```bash
mkdir workflows
chmod 755 workflows  # macOS/Linux
```

---

## Examples

### Example: Data Pipeline

**Requirement**:
```
Analyze TypeScript files for type safety issues and 
generate recommendations
```

**Generated Workflow**:
- file_ingester (source_path: "./src", file_patterns: ["*.ts"])
- code_extractor (extract_type: "functions", language: "typescript")
- rule_engine (rules_file: "rules/typescript.yaml")
- report_generator (template: "standard")

### Example: Quality Gates

**Requirement**:
```
Check code against all governance rules and report 
any critical violations before deployment
```

**Generated Workflow**:
- file_ingester
- code_extractor (extract_type: "all")
- rule_engine (severity_threshold: "error")
- result_aggregator (format: "json")
- report_generator (template: "executive")

---

## Next Steps

1. ✅ Generate first workflow
2. ✅ Save to YAML
3. ✅ Modify and customize
4. 📋 Run workflow through orchestrator (coming soon)
5. 📊 Integrate with CI/CD pipeline

---

## Tips & Tricks

### Tip 1: Be Specific

❌ Bad: "Analyze code"  
✅ Good: "Extract Python functions and check them against security rules"

### Tip 2: Start Simple

❌ Complex: 10 components in one workflow  
✅ Simple: 3-5 components, then expand

### Tip 3: Use Comments

```yaml
# This workflow extracts code from Python files
# and generates a report of governance violations
```

### Tip 4: Version Your Workflows

```
workflows/
  pipeline_v1.yaml
  pipeline_v2.yaml
  pipeline_final.yaml
```

### Tip 5: Copy Working Workflows

```bash
# Clone a working workflow as base
cp workflows/working.yaml workflows/my_new_workflow.yaml
# Then modify in the builder
```

---

## Support Resources

- **Full Documentation**: `LLM_WORKFLOW_BUILDER_GUIDE.md`
- **API Reference**: See module docstrings
- **Examples**: `workflows/` directory
- **Schemas**: `workflow_schema.py` for registered components

---

**You're ready! Start building! 🚀**

Next time you need a workflow: Just describe what you want, and the LLM will suggest the best approach!
