import yaml
import logging
from datetime import datetime

from findrum.registry.registry import get_trigger, get_operator, get_datasource

logger = logging.getLogger("findrum")

class PipelineRunner:
    """Executes a data pipeline defined by a series of steps.

    Supports both batch and event-driven execution. Each step in the
    pipeline can be an operator or a datasource, and steps may depend
    on the output of other steps or an external event.
    """

    def __init__(self, pipeline_def: dict):
        """Initialize the PipelineRunner with a pipeline definition.

        Args:
            pipeline_def (dict): Parsed YAML dictionary defining the pipeline.
        """
        self.event_def = pipeline_def.get("event", {})
        self.pipeline_steps = pipeline_def.get("pipeline", [])
        self.results = {}
        self.param_overrides = {}

    def _resolve_input(self, step):
        """Resolve the input for a given step based on its dependencies.

        Args:
            step (dict): The pipeline step definition.

        Returns:
            Any: The resolved input data from dependent steps.
        """
        depends_on = step.get("depends_on")
        if isinstance(depends_on, list):
            return [self.results.get(dep) for dep in depends_on]
        elif depends_on:
            return self.results.get(depends_on)
        return None

    def _run_step(self, step, input_data=None):
        """Run a single step in the pipeline.

        Args:
            step (dict): The step definition.
            input_data (optional): Input data to the step. If not provided, resolved from dependencies.

        Returns:
            Any: The result of executing the step.

        Raises:
            ValueError: If neither operator nor datasource is defined for the step.
        """
        step_id = step["id"]
        operator_type = step.get("operator")
        datasource_type = step.get("datasource")
        params = step.get("params", {})

        resolved_params = {
            str(k): self.param_overrides.get(step_id, {}).get(k, v)
            for k, v in params.items()
        }

        if input_data is None:
            input_data = self._resolve_input(step)

        logger.info(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] → Executing step: {step_id}")

        if operator_type:
            OperatorClass = get_operator(operator_type)
            self.results[step_id] = OperatorClass(**resolved_params).run(input_data)
        elif datasource_type:
            DataSourceClass = get_datasource(datasource_type)
            self.results[step_id] = DataSourceClass(**resolved_params).fetch()
        else:
            raise ValueError(f"Step '{step_id}' must have either 'operator' or 'datasource'.")

        return self.results[step_id]

    def _should_use_event(self) -> bool:
        """Check whether the pipeline should be triggered by an event.

        Returns:
            bool: True if any step depends on the event type.
        """
        trigger_type = self.event_def.get("type")
        return any(step.get("depends_on") == trigger_type for step in self.pipeline_steps)

    def _execute_pipeline_with_data(self, data):
        """Execute steps that depend on an event, followed by others.

        Args:
            data (Any): The data passed from the event trigger.
        """
        executed_steps = set()
        trigger_type = self.event_def.get("type")

        for step in self.pipeline_steps:
            if step.get("depends_on") == trigger_type:
                self._run_step(step, input_data=data)
                executed_steps.add(step["id"])

        for step in self.pipeline_steps:
            if step["id"] not in executed_steps:
                self._run_step(step)

    def _run_event_trigger(self):
        """Set up and start the event trigger to run the pipeline on event."""
        trigger_type = self.event_def["type"]
        config = self.event_def.get("config", {})
        TriggerClass = get_trigger(trigger_type)
        trigger_instance = TriggerClass(**config)

        def emit(data):
            self._execute_pipeline_with_data(data)

        trigger_instance.emit = emit
        trigger_instance.start()

    def _run_batch_pipeline(self):
        """Run all pipeline steps sequentially in batch mode."""
        for step in self.pipeline_steps:
            self._run_step(step)

    def run(self):
        """Run the pipeline either in event or batch mode.

        Returns:
            dict: Results from all executed steps.
        """
        if self.event_def and self._should_use_event():
            self._run_event_trigger()
        else:
            self._run_batch_pipeline()

        return self.results

    def run_with_data(self, data):
        """Run the pipeline using external input data (used for triggers).

        Args:
            data (Any): Data injected into the pipeline.

        Returns:
            dict: Results from all executed steps.
        """
        return self.results

    def run_with_data(self, data):
        self._execute_pipeline_with_data(data)
        return self.results

    @classmethod
    def from_yaml(cls, path: str):
        """Create a PipelineRunner from a YAML file.

        Args:
            path (str): Path to the YAML pipeline file.

        Returns:
            PipelineRunner: An instance initialized with the parsed pipeline.

        Raises:
            ValueError: If the YAML file is not valid or does not contain a dictionary.
        """
        with open(path, "r") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError(f"{path} must contain a valid dictionary with pipeline definition.")

        return cls(config)