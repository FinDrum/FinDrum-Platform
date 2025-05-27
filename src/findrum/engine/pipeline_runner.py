import yaml
import logging
logger = logging.getLogger("findrum")
from datetime import datetime
from findrum.registry.registry import get_operator, get_datasource

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

            resolved_params = {
                k: self.param_overrides.get(k, v) for k, v in params.items()
            }

            input_data = self.results.get(depends_on) if depends_on else None

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{timestamp}] → Executing step: {step_id}")

            if operator:
                OperatorClass = get_operator(operator)
                instance = OperatorClass(**resolved_params)
                self.results[step_id] = instance.run(input_data)
            elif datasource:
                if depends_on:
                    raise ValueError("Datasource step cannot depend on another step.")
                DataSourceClass = get_datasource(datasource)
                instance = DataSourceClass(**resolved_params)
                self.results[step_id] = instance.fetch()
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
