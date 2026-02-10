# LLM Workflow Builder - Architecture & Data Flow

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CANONICAL CODE PLATFORM                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI LAYER                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ui_app.py                                                       │
│  ├─ 🏠 Dashboard                                                │
│  ├─ 📊 Analysis                                                 │
│  ├─ 🚀 Extraction                                               │
│  ├─ 📈 Drift History                                            │
│  ├─ 🎛️ Orchestrator                                             │
│  ├─ 🤖 RAG Analysis                                             │
│  ├─ 🤖 LLM Builder ◄─── NEW! (renders llm_workflow_ui)         │
│  └─ ⚙️ Settings                                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              │ Imports & Renders
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    LLM WORKFLOW LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  llm_workflow_ui.py (450+ lines)                               │
│  └─ LLMWorkflowUI class                                        │
│     ├─ render() - Main UI orchestration                        │
│     ├─ _render_llm_suggestions_panel() - Left pane             │
│     ├─ _render_workflow_builder_panel() - Right pane           │
│     ├─ _render_workflow_preview() - YAML preview               │
│     └─ Various helper methods                                  │
│                                                                  │
└──────────────────┬──────────────────┬──────────────────────────┘
                   │                  │
       ┌───────────▼──────┐    ┌──────▼──────────────┐
       │                  │    │                     │
       │ LLM Integration  │    │ Workflow Definition │
       │                  │    │ & Validation        │
       │                  │    │                     │
       
┌──────────────────────────────────────────────────────────────────┐
│         LLM INTEGRATION & WORKFLOW ORCHESTRATION                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  llm_integration.py (450+ lines)      workflow_builder.py       │
│  ├─ LLMConfig                         ├─ Workflow               │
│  ├─ LMStudioClient                    ├─ WorkflowStep           │
│  │  ├─ is_available()                 ├─ WorkflowMetadata       │
│  │  ├─ generate_workflow_..()         ├─ WorkflowBuilder        │
│  │  ├─ validate_workflow()            │  ├─ create_workflow()   │
│  │  ├─ optimize_workflow()            │  ├─ add_step()          │
│  │  ├─ explain_component()            │  ├─ from_llm_..()       │
│  │  ├─ stream_generation()            │  ├─ save_workflow()     │
│  │  └─ get_llm_client()              │  ├─ load_workflow()     │
│  │                                    │  ├─ validate_..()       │
│  │                                    │  └─ get_stats()         │
│  │                                    │                         │
│  workflow_schema.py (600+ lines)      │                         │
│  ├─ ComponentType (Enum)              │                         │
│  ├─ ComponentParameter                │                         │
│  ├─ ComponentDefinition               │                         │
│  ├─ WorkflowSchemaGenerator           │                         │
│  │  ├─ register_component()           │                         │
│  │  ├─ list_components()              │                         │
│  │  ├─ generate_schema()              │                         │
│  │  ├─ validate_workflow_..()         │                         │
│  │  └─ suggest_component_..()         │                         │
│  └─ WorkflowValidator                 │                         │
│     ├─ validate_yaml()                │                         │
│     └─ _check_best_practices()        │                         │
│                                        │                         │
└────────────────────┬───────────────────┼────────────────────────┘
                     │                   │
                     │                   │
                     ▼                   ▼
         ┌──────────────────┐  ┌─────────────────┐
         │  LM STUDIO API   │  │  YAML/JSON      │
         │  HTTP Endpoint   │  │  Processing     │
         │  192.168.0.190   │  │                 │
         │  :1234           │  └─────────────────┘
         │                  │
         │ Workflow         │
         │ Suggestion       │
         │ Generation       │
         │ & Validation     │
         └──────────────────┘

```

---

## Data Flow Diagram

### 1. Workflow Generation Flow

```
┌─ START ─────────────────────────────────────────────────┐
│                                                          │
│ User enters requirement in LLM Builder (Left Panel)     │
│ "Extract functions and check rules"                     │
│                                                          │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ User selects components                                │
│ [✓] file_ingester                                       │
│ [✓] code_extractor                                      │
│ [✓] rule_engine                                         │
│ [✓] report_generator                                    │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ Click: 🚀 Generate with AI                             │
│                                                         │
│ LLMWorkflowUI._generate_suggestions() called            │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ LMStudioClient.generate_workflow_suggestions()          │
│                                                         │
│ Builds prompt:                                          │
│  - "You are a workflow architect"                      │
│  - "Available components: [...]"                        │
│  - "Requirements: Extract functions and check rules"   │
│  - "Generate workflow configuration as JSON"           │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ HTTP POST to LM Studio                                 │
│ http://192.168.0.190:1234/v1/chat/completions         │
│                                                         │
│ Request:                                                │
│ {                                                       │
│   "model": "local-model",                              │
│   "messages": [{"role": "user", "content": "..."}],   │
│   "temperature": 0.7,                                  │
│   "max_tokens": 2048                                   │
│ }                                                       │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼ (10-30 seconds)
┌──────────────────────────────────────────────────────────┐
│ LM Studio generates response                            │
│                                                         │
│ Response example:                                       │
│ {                                                       │
│   "reasoning": "These components create a pipeline...",│
│   "steps": [                                            │
│     {                                                   │
│       "component": "file_ingester",                     │
│       "name": "Load Files",                             │
│       "parameters": {                                   │
│         "source_path": "/code",                         │
│         "recursive": true                              │
│       },                                                │
│       "outputs": ["raw_files"]                          │
│     },                                                  │
│     ...                                                 │
│   ]                                                     │
│ }                                                       │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ Parse JSON response                                     │
│                                                         │
│ _parse_workflow_response()                              │
│  ├─ Extract JSON from response                         │
│  ├─ Load as Python dict                                │
│  └─ Return with metadata                               │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ Display suggestions (Left Panel)                        │
│                                                         │
│ _display_suggestions()                                  │
│  ├─ Show reasoning                                      │
│  ├─ List suggested steps                                │
│  ├─ Show parameters                                     │
│  └─ Buttons: [✅ Accept] [🔄 Regenerate] [💬 Explain] │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ User clicks: ✅ Accept Suggestion                      │
│                                                         │
│ _accept_suggestion(suggestion_obj)                      │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ WorkflowBuilder.from_llm_suggestion()                   │
│                                                         │
│  1. create_workflow(name)                               │
│  2. For each step in suggestion:                        │
│     - add_step(component, parameters, inputs, outputs) │
│  3. Return fully constructed Workflow object            │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ Display in Right Panel (Workflow Builder)               │
│                                                         │
│ Workflow now shows:                                     │
│  1. Step 1: file_ingester                              │
│  2. Step 2: code_extractor                              │
│  3. Step 3: rule_engine                                 │
│  4. Step 4: report_generator                            │
│                                                         │
│ Each step has [✏️] [🗑️] buttons                         │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ Preview Section (Bottom)                                │
│                                                         │
│ Shows:                                                  │
│  - Live YAML representation                             │
│  - Validation status (✅ or ❌)                          │
│  - Connection validation                                │
│  - [📋 Copy YAML] button                                │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ User clicks: 💾 Save Workflow                          │
│                                                         │
│ WorkflowBuilder.save_workflow()                         │
│  1. Get workflow from session state                     │
│  2. Convert to YAML: workflow.to_yaml()                 │
│  3. Write to: workflows/{name}.yaml                     │
│  4. Show success message                                │
└──────────────────────┬─────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ YAML file saved                                         │
│ Location: workflows/my_workflow.yaml                    │
│                                                         │
│ File ready for:                                         │
│  - Execution by orchestrator (future)                   │
│  - Loading in future sessions                           │
│  - Sharing with team                                    │
│  - Version control (git)                                │
│                                                         │
└──────────────────────────────────────────────────────────┘
```

### 2. Validation Flow

```
User clicks [Validate] or submits workflow
         │
         ▼
WorkflowValidator.validate_yaml(yaml_string)
         │
         ├─ YAML parsing
         │  ├─ yaml.safe_load()
         │  └─ Check for syntax errors
         │
         ├─ Structure validation
         │  ├─ Required fields present?
         │  ├─ version, name, steps
         │  └─ Errors list
         │
         ├─ Step validation (for each step)
         │  ├─ Component exists?
         │  ├─ Required parameters present?
         │  └─ Parameter types correct?
         │
         ├─ Connection validation
         │  ├─ Inputs refer to previous outputs?
         │  ├─ Data types compatible?
         │  └─ No orphaned steps?
         │
         ├─ Best practices check
         │  ├─ Too many steps? (>10)
         │  ├─ Timeout set?
         │  ├─ Error handling?
         │  └─ Warnings list
         │
         └─ Return result
            ├─ valid: bool
            ├─ errors: List[str]
            ├─ warnings: List[str]
            └─ Display in UI
```

### 3. Component Registration Flow

```
System startup
         │
         ▼
WorkflowSchemaGenerator.__init__()
         │
         ├─ _load_default_components()
         │  │
         │  ├─ Create ComponentDefinition for each:
         │  │  1. file_ingester
         │  │  2. code_extractor
         │  │  3. drift_detector
         │  │  4. rule_engine
         │  │  5. rag_analyzer
         │  │  6. result_aggregator
         │  │  7. report_generator
         │  │
         │  └─ register_components(components)
         │
         └─ Components now available for:
            ├─ Suggestions (show to user)
            ├─ Validation (check against schema)
            ├─ Generation (LLM can suggest them)
            └─ Explanation (describe to user)
```

---

## Module Interactions

```
┌───────────────────────────────────────┐
│        llm_workflow_ui.py             │ ◄─── User Interface
│     (LLMWorkflowUI class)             │      (Streamlit)
└───────────────┬───────────────────────┘
                │
        ┌───────┴────────┬─────────────┬──────────────┐
        │                │             │              │
        ▼                ▼             ▼              ▼
    ┌───────┐     ┌──────────┐   ┌──────────┐  ┌─────────────┐
    │ User  │     │   LLM    │   │Workflow  │  │  Workflow   │
    │Input  │     │Integration  │Builder   │  │Schema Gen   │
    └───┬───┘     └──┬────────┘   └──┬──────┘  └──────┬──────┘
        │           │               │               │
        └─────┬─────┴───────┬───────┴──────────────┘
              │             │
              ▼             ▼
    ┌─────────────────────────────┐
    │ Session State Persistence   │
    │ (st.session_state)          │
    └─────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────┐
    │ File System                 │
    │ workflows/ folder           │
    │ (YAML files)                │
    └─────────────────────────────┘
```

---

## Component Flow

```
ComponentDefinition
    │
    ├─ name
    ├─ type (ComponentType.EXTRACTOR, etc.)
    ├─ description
    ├─ version
    ├─ parameters (List[ComponentParameter])
    │   └─ name, type, required, default, options
    ├─ inputs (List[str])
    ├─ outputs (List[str])
    ├─ examples
    └─ tags
         │
         ▼
    Registered in WorkflowSchemaGenerator
         │
         ├─ Available for suggestions
         ├─ Used in schema validation
         ├─ Listed for user selection
         └─ Explained via LLM
```

---

## YAML Generation Pipeline

```
User Requirement
    │
    ├─ Text: "Extract code and check rules"
    │
    ▼
LLM Prompt Construction
    │
    ├─ System: "You are a workflow architect"
    ├─ User: Requirement + Components + Context
    │
    ▼
LM Studio Processing
    │
    ├─ Load model
    ├─ Generate response
    ├─ Return JSON
    │
    ▼
Response Parsing
    │
    ├─ Extract JSON from text
    ├─ Parse into Python dict
    │
    ▼
Workflow Object Creation
    │
    ├─ WorkflowStep for each suggestion
    ├─ Add to Workflow
    │
    ▼
YAML Serialization
    │
    ├─ Call workflow.to_yaml()
    ├─ Uses yaml.dump()
    │
    ▼
YAML File
    │
    └─ version: "1.0.0"
       name: "..."
       steps:
         - id: "..."
           component: "..."
           parameters: {...}
           inputs: [...]
           outputs: [...]
```

---

## Error Handling Flow

```
                    ┌─ LM Studio Unavailable
                    │  └─ Show "🔴 Status"
                    │  └─ Offer help text
                    │
User Action
    │
    ├─ YAML Parse Error
    │  │  └─ "YAML parse error: ..."
    │  │  └─ Display error line
    │
    ├─ Validation Error
    │  │  └─ "Missing component: ..."
    │  │  └─ Highlight issue
    │
    ├─ Connection Error
    │  │  └─ "Input 'xyz' not found in outputs"
    │  │  └─ Show dependency chain
    │
    ├─ Parameter Error
    │  │  └─ "Missing required param: ..."
    │  │  └─ Show required params
    │
    └─ File Error
       └─ "Failed to save workflow"
       └─ Check permissions
```

---

## State Management

```
Streamlit Session State
    │
    └─ workflow_builder_state (dict)
       │
       ├─ current_workflow (Workflow object)
       │  └─ Name, description, steps
       │
       ├─ suggestions (dict)
       │  └─ From LLM response
       │
       ├─ workflow_yaml (str)
       │  └─ YAML representation
       │
       ├─ validation_result (dict)
       │  └─ Validation status & errors
       │
       └─ accepted_changes (list)
          └─ Change history
```

---

## Integration Points

### 1. With Message Bus
```
bus.publish_event("WORKFLOW_GENERATED", {
    "workflow_name": "...",
    "components": [...],
    "timestamp": "..."
})
```

### 2. With Orchestrator
```
orchestrator.execute_workflow(workflow)
    └─ When executor module available
```

### 3. With RAG System
```
rag_component = ComponentDefinition(...)
    └─ Enables semantic analysis in workflows
```

### 4. With Settings Database
```
settings_db.set_setting("llm_endpoint", "...")
    └─ Persistent configuration
```

---

## Performance Characteristics

```
Operation               Time        Complexity
─────────────────────────────────────────────
Generate Suggestion    10-30s      O(n) where n = component count
Parse YAML             <100ms      O(m) where m = step count
Validate Workflow      50-100ms    O(m*p) where p = param count
Save to File           <50ms       O(1)
Load from File         <100ms      O(m)
Render UI              <1s         O(1)
Schema Generation      <10ms       O(n)

n = number of components (~10)
m = number of workflow steps (5-15 typical)
p = parameters per step (2-10 typical)
```

---

**This architecture enables intuitive, AI-assisted workflow authoring while maintaining clean separation of concerns and integration with the broader Canonical Code Platform.**
