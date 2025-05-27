import yaml
import logging
from datetime import datetime
from findrum.registry.registry import get_operator, get_datasource

logger = logging.getLogger("findrum")

class PipelineRunner:
    def __init__(self, pipeline_def):
        self.pipeline_def = pipeline_def
        self.results = {}
        self.param_overrides = {}

    def override_params(self, overrides: dict):
        self.param_overrides.update(overrides)
        return self

    def run(self):
        for step in self.pipeline_def:
            step_id = step["id"]
            operator = step.get("operator")
            datasource = step.get("datasource")
            depends_on = step.get("depends_on")
            params = step.get("params", {})
            
            step_overrides = self.param_overrides.get(step_id, {})
            resolved_params = {k: step_overrides.get(k, v) for k, v in params.items()}

            if isinstance(depends_on, list):
                input_data = [self.results.get(dep) for dep in depends_on]
            elif depends_on:
                input_data = self.results.get(depends_on)
            else:
                input_data = None

            logger.info(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] → Executing step: {step_id}")

            if operator:
                OperatorClass = get_operator(operator)
                self.results[step_id] = OperatorClass(**resolved_params).run(input_data)
            elif datasource:
                if depends_on:
                    raise ValueError(f"Datasource step '{step_id}' cannot depend on another step.")
                DataSourceClass = get_datasource(datasource)
                self.results[step_id] = DataSourceClass(**resolved_params).fetch()
            else:
                raise ValueError(f"Step '{step_id}' must have either 'operator' or 'datasource'.")

        return self.results

    @classmethod
    def from_yaml(cls, path):
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        pipeline_def = config.get("pipeline")
        if pipeline_def is None:
            raise ValueError(f"File {path} does not contain 'pipeline' section.")
        return cls(pipeline_def)
