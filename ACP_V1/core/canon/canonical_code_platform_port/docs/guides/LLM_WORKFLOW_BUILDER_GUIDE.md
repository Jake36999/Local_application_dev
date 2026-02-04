# LLM-Assisted Workflow Builder System

**Status**: ✅ COMPLETE  
**Version**: 1.0.0  
**Last Updated**: February 2, 2026  
**LM Studio Endpoint**: `http://192.168.0.190:1234`

---

## Overview

The LLM-Assisted Workflow Builder combines three powerful capabilities:

1. **LLM Integration** - Real-time connection to LM Studio for workflow suggestions
2. **Workflow Schema & Validation** - Component-based workflow definitions with YAML support
3. **Two-Window UI** - Side-by-side LLM suggestions and user controls in Streamlit

This enables non-technical users to design complex code analysis workflows with AI guidance.

---

## Architecture

### Module Dependencies

```
llm_workflow_ui.py (Streamlit UI)
    ↓
llm_integration.py (LM Studio client)
workflow_builder.py (YAML orchestration)
workflow_schema.py (Component schema & validation)
```

### Data Flow

```
User Requirement (text)
    ↓
LLM Prompt Generation
    ↓
LM Studio (http://192.168.0.190:1234)
    ↓
JSON Response Parsing
    ↓
Workflow from LLM Suggestion
    ↓
YAML Export / Save
```

---

## Modules

### 1. llm_integration.py - LM Studio Client

**Purpose**: Connect to LM Studio and request workflow suggestions

**Key Classes**:

#### `LLMConfig`
Configuration for LLM connection:
```python
LLMConfig(
    endpoint="http://192.168.0.190:1234",
    model="local-model",
    temperature=0.7,
    max_tokens=2048,
    timeout=60
)
```

#### `LMStudioClient`
Main client for LM Studio interaction:

**Methods**:

- `is_available()` → bool
  - Check if LM Studio endpoint is responding
  - Returns True if accessible

- `generate_workflow_suggestions(components, requirements, context)` → Dict
  - Generate workflow from natural language requirements
  - Returns: `{"success": bool, "suggestions": {...}, "reasoning": str}`

- `validate_workflow(workflow_yaml, schema)` → Dict
  - Use LLM to validate YAML against schema
  - Returns: validation status, issues, suggestions

- `optimize_workflow(workflow_yaml, constraints)` → Dict
  - Suggest optimizations to existing workflow
  - Returns: optimization suggestions with reasoning

- `explain_component(component_name, spec)` → Dict
  - Get LLM explanation of component usage
  - Returns: explanation, examples, parameter patterns

- `stream_generation(prompt, callback)` → Generator
  - Stream LLM output for real-time feedback
  - Yields: text chunks as generated

**Example Usage**:

```python
from llm_integration import get_llm_client

client = get_llm_client()

# Check availability
if client.is_available():
    print("LM Studio ready!")
else:
    print("LM Studio not responding")

# Generate suggestions
suggestions = client.generate_workflow_suggestions(
    available_components=["file_ingester", "code_extractor", "rule_engine"],
    user_requirements="Extract code and check for violations",
    context={"platform": "Canonical Code Platform"}
)

if suggestions["success"]:
    print(suggestions["suggestions"]["reasoning"])
```

---

### 2. workflow_schema.py - Component Definitions & Validation

**Purpose**: Define available components and validate workflow structure

**Key Classes**:

#### `ComponentParameter`
Parameter definition for a component:
```python
ComponentParameter(
    name="max_depth",
    type="integer",
    description="Maximum recursion depth",
    required=False,
    default=10,
    constraints={"min": 1, "max": 100}
)
```

#### `ComponentDefinition`
Complete component specification:
```python
ComponentDefinition(
    name="code_extractor",
    type=ComponentType.EXTRACTOR,
    description="Extract code structures from source files",
    version="1.0.0",
    parameters=[...],
    inputs=["raw_files"],
    outputs=["extracted_code"],
    tags=["extraction", "analysis"]
)
```

#### `WorkflowSchemaGenerator`
Generate JSON schemas from registered components:

**Methods**:

- `register_component(component)` → None
  - Register single component

- `register_components(components)` → None
  - Register multiple components

- `list_components(filter_type, filter_tags)` → List[str]
  - List available components with optional filtering

- `generate_schema()` → Dict
  - Generate complete JSON schema for all components
  - Used for workflow validation

- `get_component_schema(name)` → Dict
  - Get schema for specific component

- `validate_workflow_structure(workflow_dict)` → Tuple[bool, List[str]]
  - Validate workflow against schema
  - Returns: (is_valid, errors)

- `suggest_component_sequence(input_type, output_type, constraints)` → List[str]
  - Suggest component sequences based on data types

#### `WorkflowValidator`
Validate YAML workflow files:

**Methods**:

- `validate_yaml(yaml_content)` → Tuple[bool, Dict]
  - Parse and validate YAML workflow
  - Returns: (is_valid, validation_result)

- Result includes:
  - `valid`: bool
  - `errors`: List[str]
  - `warnings`: List[str]
  - `workflow`: parsed dict

**Pre-registered Components**:

1. **file_ingester** (EXTRACTOR)
   - Inputs: file_system
   - Outputs: raw_files
   - Params: source_path, file_patterns, recursive

2. **code_extractor** (EXTRACTOR)
   - Inputs: raw_files
   - Outputs: extracted_code
   - Params: extract_type, language

3. **drift_detector** (ANALYZER)
   - Inputs: extracted_code
   - Outputs: drift_report
   - Params: sensitivity, pattern_db

4. **rule_engine** (ANALYZER)
   - Inputs: extracted_code
   - Outputs: rule_violations
   - Params: rules_file, severity_threshold

5. **rag_analyzer** (ANALYZER)
   - Inputs: extracted_code
   - Outputs: semantic_analysis
   - Params: query, top_k

6. **result_aggregator** (PROCESSOR)
   - Inputs: drift_report, rule_violations, semantic_analysis
   - Outputs: aggregated_results
   - Params: format

7. **report_generator** (OUTPUT)
   - Inputs: aggregated_results
   - Outputs: report
   - Params: output_path, template

**Example Usage**:

```python
from workflow_schema import WorkflowSchemaGenerator, WorkflowValidator

# Generate schema
schema_gen = WorkflowSchemaGenerator()

# List components
components = schema_gen.list_components()
print(components)  # ['file_ingester', 'code_extractor', ...]

# Get specific component
comp = schema_gen.get_component("rule_engine")
print(comp.description)

# Validate workflow
validator = WorkflowValidator(schema_gen)
is_valid, result = validator.validate_yaml(yaml_string)

if not is_valid:
    for error in result["errors"]:
        print(f"Error: {error}")
```

---

### 3. workflow_builder.py - YAML Orchestration

**Purpose**: Build, modify, and manage workflows programmatically

**Key Classes**:

#### `WorkflowStep`
Single workflow step:
```python
WorkflowStep(
    id="abc123",
    name="Extract Code",
    component="code_extractor",
    parameters={"extract_type": "functions", "language": "python"},
    inputs=["raw_files"],
    outputs=["extracted_code"],
    condition=None,
    retry={"max_attempts": 3, "backoff_ms": 1000},
    timeout_ms=30000
)
```

#### `Workflow`
Complete workflow definition:
```python
Workflow(
    version="1.0.0",
    name="Full Analysis Pipeline",
    description="Extract, analyze, and report",
    steps=[...],
    metadata=WorkflowMetadata(...),
    globals={...}
)
```

#### `WorkflowBuilder`
Programmatic workflow construction:

**Methods**:

- `create_workflow(name, description, author)` → Workflow
  - Create new workflow

- `add_step(workflow_name, component, parameters, inputs, outputs)` → WorkflowStep
  - Add step to workflow

- `from_llm_suggestion(suggestion, name)` → Workflow
  - Create workflow from LLM suggestion JSON

- `modify_step(workflow_name, step_id, **updates)` → WorkflowStep
  - Modify existing step

- `remove_step(workflow_name, step_id)` → bool
  - Remove step from workflow

- `reorder_steps(workflow_name, step_order)` → bool
  - Reorder workflow steps

- `get_workflow(name)` → Workflow
  - Get workflow by name

- `save_workflow(workflow_name, filepath)` → bool
  - Save workflow to YAML file

- `load_workflow(filepath, name)` → Workflow
  - Load workflow from YAML

- `export_workflow(workflow_name)` → Dict
  - Export as dictionary

- `clone_workflow(source_name, new_name)` → Workflow
  - Clone existing workflow

- `validate_workflow_connections(workflow_name)` → Tuple[bool, List]
  - Validate step-to-step data flow

- `get_workflow_stats(workflow_name)` → Dict
  - Get workflow statistics

**Example Usage**:

```python
from workflow_builder import WorkflowBuilder

builder = WorkflowBuilder()

# Create workflow
workflow = builder.create_workflow(
    name="My Pipeline",
    description="Custom analysis pipeline"
)

# Add steps
builder.add_step(
    "My Pipeline",
    component="file_ingester",
    parameters={"source_path": "/code", "recursive": True},
    outputs=["raw_files"]
)

builder.add_step(
    "My Pipeline",
    component="code_extractor",
    parameters={"extract_type": "functions"},
    inputs=["raw_files"],
    outputs=["extracted_code"]
)

# Save as YAML
builder.save_workflow("My Pipeline", "workflows/pipeline.yaml")

# Load back
loaded = builder.load_workflow("workflows/pipeline.yaml")
```

---

### 4. llm_workflow_ui.py - Streamlit UI Component

**Purpose**: Two-window Streamlit interface for workflow building

**Main Class**: `LLMWorkflowUI`

**Features**:

- **Left Panel**: LLM Suggestions
  - Natural language requirement input
  - Component selector
  - AI generation button
  - Suggestion display with acceptance controls

- **Right Panel**: Workflow Builder
  - Workflow name/description
  - Create/Load/Save controls
  - Step management (add/edit/delete)
  - Reordering support

- **Preview Section**:
  - Live YAML preview
  - Validation with error display
  - Connection validation
  - Copy to clipboard

**Integration**:

```python
# In ui_app.py
from llm_workflow_ui import render_llm_workflow_builder_tab

elif tab == "🤖 LLM Builder":
    render_llm_workflow_builder_tab()
```

---

## YAML Workflow Format

### Schema

```yaml
version: "1.0.0"
name: "Workflow Name"
description: "What this workflow does"

globals:
  timeout_default: 30000
  max_retries: 3

metadata:
  author: "Your Name"
  tags: ["analysis", "extraction"]
  notes: "Optional notes"

steps:
  - id: "step_001"
    name: "Ingest Source Files"
    component: "file_ingester"
    parameters:
      source_path: "/path/to/code"
      file_patterns: ["*.py", "*.ts"]
      recursive: true
    outputs: ["raw_files"]

  - id: "step_002"
    name: "Extract Code"
    component: "code_extractor"
    parameters:
      extract_type: "functions"
      language: "auto"
    inputs: ["raw_files"]
    outputs: ["extracted_code"]

  - id: "step_003"
    name: "Check Rules"
    component: "rule_engine"
    parameters:
      rules_file: "rules/governance.yaml"
      severity_threshold: "warning"
    inputs: ["extracted_code"]
    outputs: ["rule_violations"]

  - id: "step_004"
    name: "Generate Report"
    component: "report_generator"
    parameters:
      output_path: "./reports/"
      template: "standard"
    inputs: ["rule_violations"]
    outputs: ["report"]
    retry:
      max_attempts: 3
      backoff_ms: 1000
    timeout_ms: 60000
```

### Step Specification

**Required Fields**:
- `id`: Unique step identifier
- `name`: Display name
- `component`: Component to use (must be registered)

**Optional Fields**:
- `parameters`: Key-value parameters for component
- `inputs`: List of input variable names
- `outputs`: List of output variable names
- `condition`: Conditional execution expression
- `retry`: Retry configuration
- `timeout_ms`: Step timeout in milliseconds

---

## User Guide

### Getting Started

#### 1. Ensure LM Studio is Running

```bash
# LM Studio should be running at http://192.168.0.190:1234
# Launch LM Studio and load a model
# Example: Mistral 7B, Llama 2, or similar
```

#### 2. Start the UI

```bash
streamlit run ui_app.py
```

#### 3. Navigate to "LLM Builder" Tab

```
🤖 LLM Builder
```

### Building a Workflow

#### Step 1: Enter Requirements

In the **Left Panel (AI Suggestions)**:

```
What workflow do you need?
→ "I need to extract all functions from Python files, 
    check them against our governance rules, and generate a report"
```

#### Step 2: Select Components

Click the **Available Components** dropdown and select:
- `file_ingester`
- `code_extractor`
- `rule_engine`
- `report_generator`

#### Step 3: Generate with AI

Click **🚀 Generate with AI**

The LLM will:
1. Analyze your requirements
2. Select appropriate components
3. Suggest parameter values
4. Propose optimal step sequence
5. Return suggestions in 10-30 seconds

#### Step 4: Review Suggestions

**Left Panel** shows:
- **Reasoning**: Why these components were chosen
- **Steps**: Suggested pipeline
- **Parameters**: Recommended values

#### Step 5: Accept Suggestion

Click **✅ Accept Suggestion**

This creates the workflow in the **Right Panel (Workflow Builder)**

#### Step 6: Customize (Optional)

**Right Panel** allows:
- Edit step parameters
- Add/remove steps
- Reorder steps
- Adjust timeout/retry settings

#### Step 7: Validate

**Preview Section** shows:
- YAML representation
- ✅ Validation status
- ⚠️ Best practice warnings
- Connection flow verification

#### Step 8: Save Workflow

Click **💾 Save Workflow**

Saved to: `workflows/{workflow_name}.yaml`

### Modifying Workflows

#### Load Existing

1. Click **📂 Load from File**
2. Select YAML file
3. Workflow loads in builder

#### Edit Steps

1. Click **✏️** on step to edit
2. Modify parameters
3. Changes reflected in YAML

#### Remove Steps

1. Click **🗑️** on step
2. Step removed from workflow

#### Add Steps

1. Click **➕ Add Step**
2. Select component
3. Enter parameters
4. Step added to sequence

### Explaining Components

1. Hover over component name in suggestions
2. Click **💬 Get Explanation**
3. LLM explains:
   - What it does
   - When to use it
   - Common patterns
   - Potential issues

---

## Examples

### Example 1: Simple Analysis Pipeline

**Requirement**: "Analyze Python code for best practices"

**Generated Workflow**:
```yaml
version: "1.0.0"
name: "Python Best Practices Check"

steps:
  - id: "01"
    name: "Load Files"
    component: "file_ingester"
    parameters:
      source_path: "./src"
      file_patterns: ["*.py"]
    outputs: ["raw_files"]

  - id: "02"
    name: "Extract"
    component: "code_extractor"
    parameters:
      extract_type: "all"
      language: "python"
    inputs: ["raw_files"]
    outputs: ["extracted_code"]

  - id: "03"
    name: "Validate"
    component: "rule_engine"
    parameters:
      rules_file: "rules/best_practices.yaml"
      severity_threshold: "warning"
    inputs: ["extracted_code"]
    outputs: ["issues"]

  - id: "04"
    name: "Report"
    component: "report_generator"
    parameters:
      output_path: "./reports"
      template: "standard"
    inputs: ["issues"]
```

### Example 2: Multi-Tool Analysis

**Requirement**: "Extract components, check for drift, verify rules, and create report"

**Generated Workflow**:
```yaml
version: "1.0.0"
name: "Comprehensive Analysis"

steps:
  - id: "01"
    name: "Ingest"
    component: "file_ingester"
    outputs: ["raw_files"]

  - id: "02"
    name: "Extract"
    component: "code_extractor"
    inputs: ["raw_files"]
    outputs: ["extracted_code"]

  - id: "03"
    name: "Detect Drift"
    component: "drift_detector"
    inputs: ["extracted_code"]
    outputs: ["drift_report"]
    parameters:
      sensitivity: "high"

  - id: "04"
    name: "Check Rules"
    component: "rule_engine"
    inputs: ["extracted_code"]
    outputs: ["rule_violations"]

  - id: "05"
    name: "Semantic Analysis"
    component: "rag_analyzer"
    inputs: ["extracted_code"]
    outputs: ["semantic_analysis"]
    parameters:
      query: "code quality issues"

  - id: "06"
    name: "Aggregate"
    component: "result_aggregator"
    inputs: ["drift_report", "rule_violations", "semantic_analysis"]
    outputs: ["aggregated"]
    parameters:
      format: "json"

  - id: "07"
    name: "Report"
    component: "report_generator"
    inputs: ["aggregated"]
    parameters:
      template: "detailed"
```

---

## Advanced Features

### Workflow Optimization

1. Right-click workflow in **Preview**
2. Select **🔄 Optimize**
3. LLM suggests:
   - Parallel execution opportunities
   - Caching strategies
   - Resource optimization
   - Error handling improvements

### Workflow Validation

The system validates:
- ✅ Required parameters present
- ✅ Input/output connections valid
- ✅ Data types compatible
- ✅ Component availability
- ⚠️ Best practices compliance

### Component Custom Parameters

Add custom parameters to any step:

```yaml
parameters:
  source_path: "/code"
  timeout: 30000
  retry_count: 3
  custom_var: "value"
  cache_enabled: true
```

### Conditional Execution

Steps can execute conditionally:

```yaml
steps:
  - id: "check_errors"
    component: "rule_engine"
    condition: "previous_step.error_count > 0"
    ...
```

### Error Retry

Configure automatic retries:

```yaml
retry:
  max_attempts: 3
  backoff_ms: 1000  # exponential: 1s, 2s, 4s
```

---

## Troubleshooting

### LM Studio Not Available

**Error**: "🔴 LM Studio unavailable"

**Solutions**:
1. Check LM Studio is running at `http://192.168.0.190:1234`
2. Verify network connectivity
3. Reload page (F5)

### Import Errors

**Error**: "ModuleNotFoundError: No module named 'yaml'"

**Solution**:
```bash
pip install pyyaml requests
```

### Workflow Won't Save

**Error**: "Failed to save workflow"

**Solutions**:
1. Create `workflows/` directory: `mkdir workflows`
2. Check write permissions
3. Ensure disk space available

### Generated Workflow Invalid

**Issue**: Validation shows errors

**Solutions**:
1. Regenerate suggestions
2. Manually edit to fix
3. Check component names are correct
4. Verify parameters match component schema

---

## Integration with System

### Running Generated Workflows

Once saved, workflows can be executed:

```python
from workflow_builder import WorkflowBuilder
from workflow_schema import WorkflowValidator

builder = WorkflowBuilder()
validator = WorkflowValidator(schema_gen)

# Load workflow
workflow = builder.load_workflow("workflows/my_pipeline.yaml")

# Validate
is_valid, result = validator.validate_yaml(workflow.to_yaml())

# Execute (when orchestrator supports it)
if is_valid:
    orchestrator.execute_workflow(workflow)
```

### Sending to Message Bus

Workflows can publish to the message bus:

```python
from bus.message_bus import MessageBus

bus = MessageBus()

# Publish workflow execution
bus.publish_event(
    event_type="WORKFLOW_EXECUTE",
    payload_json=json.dumps({
        "workflow_name": workflow.name,
        "steps": len(workflow.steps),
        "components": list(set(s.component for s in workflow.steps))
    })
)
```

---

## Performance Considerations

### LLM Generation Time

- **First generation**: ~10-30 seconds (depends on model)
- **Subsequent**: ~5-10 seconds (cached)
- **Streaming**: Real-time feedback available

### Workflow Complexity

- **Recommended max steps**: 10-15
- **Recommended max parameters**: 20 per step
- **Data flow**: Validate before execution

### Resource Usage

- **LM Studio**: Runs locally on `192.168.0.190`
- **UI**: Minimal overhead (Streamlit)
- **Storage**: YAML files ~10KB each

---

## API Reference

### Quick Start Code

```python
from llm_integration import get_llm_client
from workflow_builder import WorkflowBuilder
from workflow_schema import WorkflowSchemaGenerator

# Initialize
client = get_llm_client()
builder = WorkflowBuilder()
schema_gen = WorkflowSchemaGenerator()

# Generate
suggestions = client.generate_workflow_suggestions(
    available_components=schema_gen.list_components(),
    user_requirements="Extract and analyze code"
)

# Create from suggestion
workflow = builder.from_llm_suggestion(
    suggestions["suggestions"],
    name="Generated Workflow"
)

# Save
builder.save_workflow("Generated Workflow", "workflows/generated.yaml")

print(f"Workflow saved with {len(workflow.steps)} steps")
```

### Batch Generation

```python
# Generate multiple variations
for i in range(3):
    suggestions = client.generate_workflow_suggestions(
        available_components=["file_ingester", "code_extractor"],
        user_requirements="My analysis requirement",
        context={"iteration": i}
    )
    
    workflow = builder.from_llm_suggestion(
        suggestions["suggestions"],
        name=f"Pipeline_v{i}"
    )
    builder.save_workflow(f"Pipeline_v{i}", f"workflows/pipeline_v{i}.yaml")
```

---

## Contributing

To add new components:

```python
from workflow_schema import ComponentDefinition, ComponentParameter, ComponentType

new_component = ComponentDefinition(
    name="my_component",
    type=ComponentType.PROCESSOR,
    description="Does something useful",
    version="1.0.0",
    parameters=[
        ComponentParameter("param1", "string", "Description"),
        ComponentParameter("param2", "integer", "Description", default=10)
    ],
    inputs=["input_type"],
    outputs=["output_type"],
    tags=["custom", "processing"]
)

schema_gen.register_component(new_component)
```

---

## FAQ

**Q: Can I use different LLM models?**
A: Yes! Change the `model` field in `LLMConfig` to any model available in your LM Studio instance.

**Q: How do I add custom components?**
A: Register them with `WorkflowSchemaGenerator.register_component()`.

**Q: Can workflows run in parallel?**
A: The framework supports it via `condition` fields and step reordering. Full parallel execution coming in v2.

**Q: Where are workflows stored?**
A: By default in `workflows/` directory as YAML files.

**Q: Can I export workflows to other formats?**
A: Current format is YAML/JSON. Other formats can be added via plugins.

---

## Support

For issues or questions:

1. Check **Troubleshooting** section above
2. Verify LM Studio connection: `http://192.168.0.190:1234`
3. Check logs for detailed errors
4. Review example workflows in `workflows/` directory

---

**Built for the Canonical Code Platform**  
*Making code analysis accessible to everyone*
