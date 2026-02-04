"""
Workflow Builder and YAML Manager

Handles creation, modification, and execution of YAML-defined workflows with LLM assistance.
"""

import yaml
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Represents a single workflow step"""
    id: str
    name: str
    component: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    retry: Optional[Dict[str, int]] = None
    timeout_ms: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class WorkflowMetadata:
    """Workflow metadata"""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = ""
    tags: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Workflow:
    """Complete workflow definition"""
    version: str = "1.0.0"
    name: str = ""
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    metadata: WorkflowMetadata = field(default_factory=WorkflowMetadata)
    globals: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": asdict(self.metadata),
            "globals": self.globals
        }

    def to_yaml(self) -> str:
        """Convert to YAML string"""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)


class WorkflowBuilder:
    """Build workflows programmatically or from LLM suggestions"""

    def __init__(self):
        """Initialize workflow builder"""
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_history: Dict[str, List[Workflow]] = {}

    def create_workflow(
        self,
        name: str,
        description: str = "",
        author: str = ""
    ) -> Workflow:
        """Create new workflow
        
        Args:
            name: Workflow name
            description: Description
            author: Author name
            
        Returns:
            New Workflow instance
        """
        workflow = Workflow(
            name=name,
            description=description,
            metadata=WorkflowMetadata(author=author)
        )
        self.workflows[name] = workflow
        self.workflow_history[name] = [workflow]
        logger.info(f"Created workflow: {name}")
        return workflow

    def add_step(
        self,
        workflow_name: str,
        component: str,
        step_name: str = "",
        parameters: Optional[Dict] = None,
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None
    ) -> WorkflowStep:
        """Add step to workflow
        
        Args:
            workflow_name: Target workflow
            component: Component name
            step_name: Step display name
            parameters: Component parameters
            inputs: Input variable names
            outputs: Output variable names
            
        Returns:
            Added WorkflowStep
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        step = WorkflowStep(
            id=str(uuid.uuid4())[:8],
            name=step_name or component,
            component=component,
            parameters=parameters or {},
            inputs=inputs or [],
            outputs=outputs or []
        )

        workflow.steps.append(step)
        logger.info(f"Added step to {workflow_name}: {component}")
        return step

    def from_llm_suggestion(
        self,
        suggestion: Dict[str, Any],
        name: str
    ) -> Workflow:
        """Create workflow from LLM suggestion
        
        Args:
            suggestion: LLM suggestion dictionary
            name: Workflow name
            
        Returns:
            Created Workflow
        """
        workflow = self.create_workflow(
            name,
            description=suggestion.get("reasoning", "")
        )

        steps = suggestion.get("steps", [])
        for i, step_spec in enumerate(steps):
            try:
                self.add_step(
                    name,
                    component=step_spec.get("component"),
                    step_name=step_spec.get("name"),
                    parameters=step_spec.get("parameters"),
                    inputs=step_spec.get("inputs", []),
                    outputs=step_spec.get("outputs", [])
                )
            except Exception as e:
                logger.error(f"Failed to add step from LLM: {e}")

        return workflow

    def modify_step(
        self,
        workflow_name: str,
        step_id: str,
        **updates
    ) -> Optional[WorkflowStep]:
        """Modify existing step
        
        Args:
            workflow_name: Workflow name
            step_id: Step ID to modify
            **updates: Fields to update
            
        Returns:
            Modified step or None if not found
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return None

        for step in workflow.steps:
            if step.id == step_id:
                for key, value in updates.items():
                    if hasattr(step, key):
                        setattr(step, key, value)
                logger.info(f"Modified step {step_id} in {workflow_name}")
                return step

        return None

    def remove_step(
        self,
        workflow_name: str,
        step_id: str
    ) -> bool:
        """Remove step from workflow
        
        Args:
            workflow_name: Workflow name
            step_id: Step ID to remove
            
        Returns:
            True if removed, False if not found
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return False

        original_len = len(workflow.steps)
        workflow.steps = [s for s in workflow.steps if s.id != step_id]

        if len(workflow.steps) < original_len:
            logger.info(f"Removed step {step_id} from {workflow_name}")
            return True

        return False

    def reorder_steps(
        self,
        workflow_name: str,
        step_order: List[str]
    ) -> bool:
        """Reorder workflow steps
        
        Args:
            workflow_name: Workflow name
            step_order: List of step IDs in desired order
            
        Returns:
            True if successful
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return False

        step_map = {step.id: step for step in workflow.steps}
        new_steps = []

        for step_id in step_order:
            if step_id in step_map:
                new_steps.append(step_map[step_id])
            else:
                logger.warning(f"Step {step_id} not found")

        workflow.steps = new_steps
        return True

    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get workflow by name
        
        Args:
            name: Workflow name
            
        Returns:
            Workflow or None
        """
        return self.workflows.get(name)

    def list_workflows(self) -> List[str]:
        """List all workflows
        
        Returns:
            List of workflow names
        """
        return sorted(self.workflows.keys())

    def save_workflow(
        self,
        workflow_name: str,
        filepath: str
    ) -> bool:
        """Save workflow to YAML file
        
        Args:
            workflow_name: Workflow to save
            filepath: Target file path
            
        Returns:
            True if successful
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return False

        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(workflow.to_yaml())
            logger.info(f"Saved workflow to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            return False

    def load_workflow(
        self,
        filepath: str,
        name: Optional[str] = None
    ) -> Optional[Workflow]:
        """Load workflow from YAML file
        
        Args:
            filepath: Path to YAML file
            name: Optional override name
            
        Returns:
            Loaded Workflow or None
        """
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)

            workflow = self._dict_to_workflow(data)
            if name:
                workflow.name = name

            self.workflows[workflow.name] = workflow
            self.workflow_history[workflow.name] = [workflow]
            logger.info(f"Loaded workflow from {filepath}")
            return workflow

        except Exception as e:
            logger.error(f"Failed to load workflow: {e}")
            return None

    def export_workflow(self, workflow_name: str) -> Optional[Dict]:
        """Export workflow as dictionary
        
        Args:
            workflow_name: Workflow to export
            
        Returns:
            Workflow dictionary or None
        """
        workflow = self.workflows.get(workflow_name)
        return workflow.to_dict() if workflow else None

    def clone_workflow(
        self,
        source_name: str,
        new_name: str
    ) -> Optional[Workflow]:
        """Clone existing workflow
        
        Args:
            source_name: Source workflow name
            new_name: New workflow name
            
        Returns:
            Cloned Workflow or None
        """
        source = self.workflows.get(source_name)
        if not source:
            return None

        import copy
        cloned = copy.deepcopy(source)
        cloned.name = new_name
        cloned.metadata.created_at = datetime.now().isoformat()

        self.workflows[new_name] = cloned
        self.workflow_history[new_name] = [cloned]
        logger.info(f"Cloned workflow from {source_name} to {new_name}")
        return cloned

    def validate_workflow_connections(
        self,
        workflow_name: str
    ) -> Tuple[bool, List[str]]:
        """Validate workflow step connections
        
        Args:
            workflow_name: Workflow to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return False, ["Workflow not found"]

        errors = []
        step_outputs = {}

        for i, step in enumerate(workflow.steps):
            # Check if inputs are available from previous steps
            for input_var in step.inputs:
                if input_var not in step_outputs and i > 0:
                    errors.append(
                        f"Step {step.name}: Input '{input_var}' not found in previous outputs"
                    )

            # Record outputs for next steps
            for output_var in step.outputs:
                step_outputs[output_var] = step.id

        return len(errors) == 0, errors

    def get_workflow_stats(self, workflow_name: str) -> Optional[Dict]:
        """Get workflow statistics
        
        Args:
            workflow_name: Workflow name
            
        Returns:
            Stats dictionary or None
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return None

        component_types = {}
        for step in workflow.steps:
            comp_type = step.component
            component_types[comp_type] = component_types.get(comp_type, 0) + 1

        return {
            "name": workflow.name,
            "step_count": len(workflow.steps),
            "components": component_types,
            "unique_components": len(component_types),
            "created_at": workflow.metadata.created_at,
            "updated_at": workflow.metadata.updated_at
        }

    # ==================== Private Helpers ====================

    def _dict_to_workflow(self, data: Dict) -> Workflow:
        """Convert dictionary to Workflow
        
        Args:
            data: Workflow dictionary
            
        Returns:
            Workflow instance
        """
        steps = [
            WorkflowStep(
                id=step.get("id", str(uuid.uuid4())[:8]),
                name=step.get("name", ""),
                component=step.get("component", ""),
                parameters=step.get("parameters", {}),
                inputs=step.get("inputs", []),
                outputs=step.get("outputs", []),
                condition=step.get("condition"),
                retry=step.get("retry"),
                timeout_ms=step.get("timeout_ms")
            )
            for step in data.get("steps", [])
        ]

        metadata_data = data.get("metadata", {})
        metadata = WorkflowMetadata(
            created_at=metadata_data.get("created_at", datetime.now().isoformat()),
            updated_at=metadata_data.get("updated_at", datetime.now().isoformat()),
            author=metadata_data.get("author", ""),
            tags=metadata_data.get("tags", []),
            notes=metadata_data.get("notes", "")
        )

        return Workflow(
            version=data.get("version", "1.0.0"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            steps=steps,
            metadata=metadata,
            globals=data.get("globals", {})
        )
