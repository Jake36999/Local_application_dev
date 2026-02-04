"""
Streamlit components for LLM-assisted workflow builder

Two-window layout: LLM suggestions (left) and user controls (right)
"""

import streamlit as st
import json
import yaml
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

# Import our modules
from llm_integration import get_llm_client, LLMConfig
from workflows.workflow_builder import WorkflowBuilder, Workflow, WorkflowStep
from workflow_schema import WorkflowSchemaGenerator, WorkflowValidator

logger = logging.getLogger(__name__)


class LLMWorkflowUI:
    """Streamlit UI for LLM-assisted workflow building"""

    def __init__(self):
        """Initialize workflow UI"""
        self._init_session_state()
        self.llm_client = get_llm_client()
        self.workflow_builder = WorkflowBuilder()
        self.schema_gen = WorkflowSchemaGenerator()
        self.validator = WorkflowValidator(self.schema_gen)

    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if "workflow_builder_state" not in st.session_state:
            st.session_state.workflow_builder_state = {
                "current_workflow": None,
                "suggestions": None,
                "workflow_yaml": "",
                "validation_result": None,
                "accepted_changes": []
            }

    def render(self):
        """Main render function for workflow builder tab"""
        st.title("🤖 LLM-Assisted Workflow Builder")
        
        # Two-column layout
        col_suggestions, col_builder = st.columns([1, 1], gap="large")

        with col_suggestions:
            self._render_llm_suggestions_panel()

        with col_builder:
            self._render_workflow_builder_panel()

        # Full-width sections below
        st.divider()
        self._render_workflow_preview()

    def _render_llm_suggestions_panel(self):
        """Left panel: LLM suggestions"""
        st.subheader("🎯 AI Suggestions")

        with st.container(border=True):
            st.write("**Get LLM-powered workflow suggestions**")

            # Input for requirements
            requirements = st.text_area(
                "What workflow do you need?",
                placeholder="E.g., 'I need to extract code, analyze it for drift, run rules, and generate a report'",
                height=100,
                key="workflow_requirements"
            )

            # Available components selector
            available_components = self.schema_gen.list_components()
            selected_components = st.multiselect(
                "Available components:",
                available_components,
                default=available_components[:3],
                key="selected_components"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Generate with AI", type="primary"):
                    self._generate_suggestions(requirements, selected_components)

            with col2:
                llm_status = "🟢 Ready" if self.llm_client.is_available() else "🔴 Unavailable"
                st.metric("LM Studio", llm_status)

        # Display suggestions
        if st.session_state.workflow_builder_state["suggestions"]:
            self._display_suggestions()

    def _render_workflow_builder_panel(self):
        """Right panel: Workflow builder and controls"""
        st.subheader("⚙️ Workflow Builder")

        with st.container(border=True):
            # Workflow name and description
            col1, col2 = st.columns(2)
            with col1:
                workflow_name = st.text_input(
                    "Workflow name:",
                    value="new_workflow",
                    key="workflow_name"
                )
            with col2:
                st.write("**Status:**")
                if st.session_state.workflow_builder_state["current_workflow"]:
                    st.success("Workflow created")
                else:
                    st.info("No active workflow")

            # Create/Load workflow
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✏️ Create New"):
                    self._create_new_workflow(workflow_name)

            with col2:
                if st.button("📂 Load from File"):
                    st.session_state.show_file_loader = True

            with col3:
                if st.session_state.workflow_builder_state["current_workflow"]:
                    if st.button("💾 Save Workflow"):
                        self._save_workflow()

        # File loader
        if st.session_state.get("show_file_loader"):
            uploaded_file = st.file_uploader("Choose YAML file:", type="yaml")
            if uploaded_file:
                self._load_workflow_from_file(uploaded_file)
                st.session_state.show_file_loader = False

        # Active workflow management
        if st.session_state.workflow_builder_state["current_workflow"]:
            self._render_workflow_management()

    def _render_workflow_management(self):
        """Render workflow step management"""
        st.write("**Steps:**")

        workflow = st.session_state.workflow_builder_state["current_workflow"]
        
        if not workflow.steps:
            st.info("No steps yet. Add steps or accept LLM suggestion.")
        else:
            # Display steps
            for i, step in enumerate(workflow.steps):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**{i+1}. {step.component}**")
                        st.caption(f"Parameters: {len(step.parameters)}")

                    with col2:
                        if st.button("✏️", key=f"edit_{step.id}"):
                            st.session_state.editing_step = step.id

                    with col3:
                        if st.button("🗑️", key=f"delete_{step.id}"):
                            workflow.steps = [s for s in workflow.steps if s.id != step.id]
                            st.rerun()

            # Add step form
            with st.expander("➕ Add Step"):
                component = st.selectbox(
                    "Component:",
                    self.schema_gen.list_components(),
                    key="add_step_component"
                )

                step_name = st.text_input(
                    "Step name:",
                    value=component,
                    key="add_step_name"
                )

                if st.button("Add Step"):
                    self._add_step_to_workflow(workflow.name, component, step_name)
                    st.rerun()

    def _render_workflow_preview(self):
        """Render YAML preview and validation"""
        st.subheader("📋 Workflow Preview")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**YAML Representation:**")
            if st.session_state.workflow_builder_state["current_workflow"]:
                workflow = st.session_state.workflow_builder_state["current_workflow"]
                yaml_content = workflow.to_yaml()
                st.code(yaml_content, language="yaml")
                
                # Copy to clipboard
                if st.button("📋 Copy YAML"):
                    st.write("YAML copied to clipboard!")
            else:
                st.info("Create or load a workflow to see preview")

        with col2:
            st.write("**Validation:**")
            if st.session_state.workflow_builder_state["current_workflow"]:
                self._validate_and_display()
            else:
                st.info("No workflow to validate")

    def _generate_suggestions(self, requirements: str, components: list):
        """Generate suggestions from LLM"""
        if not requirements.strip():
            st.warning("Please enter workflow requirements")
            return

        with st.spinner("🤔 Generating suggestions..."):
            suggestions = self.llm_client.generate_workflow_suggestions(
                available_components=components,
                user_requirements=requirements,
                context={
                    "platform": "Canonical Code Platform",
                    "focus": "code analysis and governance",
                    "timestamp": datetime.now().isoformat()
                }
            )

            if suggestions.get("success"):
                st.session_state.workflow_builder_state["suggestions"] = suggestions
                st.success("✅ Suggestions generated!")
            else:
                st.error(f"❌ Generation failed: {suggestions.get('error')}")

    def _display_suggestions(self):
        """Display LLM suggestions"""
        suggestions = st.session_state.workflow_builder_state["suggestions"]

        st.write("**AI Suggestions:**")

        with st.container(border=True):
            suggestion_obj = suggestions.get("suggestions", {})
            
            # Display reasoning
            if "reasoning" in suggestion_obj:
                st.write("**Reasoning:**")
                st.write(suggestion_obj["reasoning"])

            # Display steps
            if "steps" in suggestion_obj:
                st.write("**Suggested Steps:**")
                for i, step in enumerate(suggestion_obj["steps"], 1):
                    st.write(f"{i}. **{step.get('component')}** - {step.get('name')}")
                    if step.get("parameters"):
                        st.write(f"   Parameters: {step['parameters']}")

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Accept Suggestion"):
                self._accept_suggestion(suggestion_obj)

        with col2:
            if st.button("🔄 Regenerate"):
                st.session_state.workflow_builder_state["suggestions"] = None
                st.rerun()

        with col3:
            if st.button("💬 Get Explanation"):
                st.info("Request detailed explanation for suggestions")

    def _accept_suggestion(self, suggestion: Dict):
        """Accept LLM suggestion and create workflow"""
        if not st.session_state.workflow_name:
            st.warning("Please enter a workflow name")
            return

        try:
            workflow = self.workflow_builder.from_llm_suggestion(
                suggestion,
                st.session_state.workflow_name
            )
            st.session_state.workflow_builder_state["current_workflow"] = workflow
            st.success("✅ Workflow created from suggestion!")
            st.session_state.workflow_builder_state["suggestions"] = None
            st.rerun()
        except Exception as e:
            st.error(f"Failed to create workflow: {str(e)}")

    def _create_new_workflow(self, name: str):
        """Create new workflow"""
        if not name.strip():
            st.warning("Please enter workflow name")
            return

        description = st.text_input("Workflow description (optional):")
        
        workflow = self.workflow_builder.create_workflow(
            name=name,
            description=description
        )
        st.session_state.workflow_builder_state["current_workflow"] = workflow
        st.success(f"✅ Created workflow: {name}")
        st.rerun()

    def _add_step_to_workflow(self, workflow_name: str, component: str, step_name: str):
        """Add step to workflow"""
        self.workflow_builder.add_step(
            workflow_name,
            component=component,
            step_name=step_name
        )
        st.success(f"Added {component} step")

    def _validate_and_display(self):
        """Validate workflow and display results"""
        workflow = st.session_state.workflow_builder_state["current_workflow"]
        yaml_content = workflow.to_yaml()

        # Validate structure
        is_valid, result = self.validator.validate_yaml(yaml_content)

        if is_valid:
            st.success("✅ Workflow is valid")
            if result.get("warnings"):
                st.warning("Warnings:")
                for warning in result["warnings"]:
                    st.write(f"• {warning}")
        else:
            st.error("❌ Validation errors:")
            for error in result.get("errors", []):
                st.write(f"• {error}")

        # Connection validation
        is_connected, connection_errors = self.workflow_builder.validate_workflow_connections(
            workflow.name
        )
        if is_connected:
            st.success("✅ Step connections valid")
        else:
            st.warning("Connection issues:")
            for error in connection_errors:
                st.write(f"• {error}")

    def _save_workflow(self):
        """Save workflow to file"""
        workflow = st.session_state.workflow_builder_state["current_workflow"]
        filepath = f"workflows/{workflow.name}.yaml"

        success = self.workflow_builder.save_workflow(workflow.name, filepath)
        if success:
            st.success(f"✅ Saved to {filepath}")
        else:
            st.error("Failed to save workflow")

    def _load_workflow_from_file(self, uploaded_file):
        """Load workflow from uploaded file"""
        try:
            yaml_content = uploaded_file.read().decode()
            workflow = self.workflow_builder.load_workflow(
                filepath=None,
                name=uploaded_file.name.replace(".yaml", "")
            )
            # Parse YAML directly
            data = yaml.safe_load(yaml_content)
            workflow = self.workflow_builder._dict_to_workflow(data)
            workflow.name = uploaded_file.name.replace(".yaml", "")
            self.workflow_builder.workflows[workflow.name] = workflow

            st.session_state.workflow_builder_state["current_workflow"] = workflow
            st.success(f"✅ Loaded {workflow.name}")
        except Exception as e:
            st.error(f"Failed to load workflow: {str(e)}")


# Exported render function for main UI
def render_llm_workflow_builder_tab():
    """Render LLM workflow builder tab"""
    ui = LLMWorkflowUI()
    ui.render()
