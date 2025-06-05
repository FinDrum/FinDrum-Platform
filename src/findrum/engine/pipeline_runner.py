import yaml
import logging
from datetime import datetime
from findrum.registry.registry import get_trigger, get_operator, get_datasource

logger = logging.getLogger("findrum")

class PipelineRunner:
    def __init__(self, pipeline_def):
        self.event_def = pipeline_def.get("event", {})
        self.pipeline_steps = pipeline_def.get("pipeline", [])
        self.results = {}
        self.param_overrides = {}

    def override_params(self, overrides: dict):
        self.param_overrides.update(overrides)
        return self

    def _should_use_event(self, trigger_type: str) -> bool:
        return any(step.get("depends_on") == trigger_type for step in self.pipeline_steps)

    def _run_event_trigger(self):
        trigger_type = self.event_def["type"]
        config = self.event_def.get("config", {})
        TriggerClass = get_trigger(trigger_type)
        trigger_instance = TriggerClass(**config)

        def emit(data):
            executed_steps = set()

            for step in self.pipeline_steps:
                if step.get("depends_on") == trigger_type:
                    result = self._run_step(step, input_data=data)
                    executed_steps.add(step["id"])

            for step in self.pipeline_steps:
                if step["id"] not in executed_steps:
                    self._run_step(step)

        trigger_instance.emit = emit
        trigger_instance.start()

    def _run_step(self, step, input_data=None):
        step_id = step["id"]
        operator_type = step.get("operator")
        datasource_type = step.get("datasource")
        depends_on = step.get("depends_on")
        params = step.get("params", {})

        step_overrides = self.param_overrides.get(step_id, {})
        resolved_params = {str(k): step_overrides.get(k, v) for k, v in params.items()}

        if input_data is None:
            if isinstance(depends_on, list):
                input_data = [self.results.get(dep) for dep in depends_on]
            elif depends_on:
                input_data = self.results.get(depends_on)

        logger.info(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] → Executing step: {step_id}")

        if operator_type:
            OperatorClass = get_operator(operator_type)
            self.results[step_id] = OperatorClass(**resolved_params).run(input_data)
        elif datasource_type:
            if depends_on:
                raise ValueError(f"Datasource step '{step_id}' cannot depend on another step.")
            DataSourceClass = get_datasource(datasource_type)
            self.results[step_id] = DataSourceClass(**resolved_params).fetch()
        else:
            raise ValueError(f"Step '{step_id}' must have either 'operator' or 'datasource'.")

        return self.results[step_id]

    def _run_batch_pipeline(self):
        for step in self.pipeline_steps:
            self._run_step(step)

    def run(self):
        if self.event_def:
            trigger_type = self.event_def.get("type")
            if self._should_use_event(trigger_type):
                self._run_event_trigger()
                return self.results

        self._run_batch_pipeline()
        return self.results

    @classmethod
    def from_yaml(cls, path):
        with open(path, "r") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError(f"{path} must contain a valid dictionary with pipeline definition.")

        return cls(config)