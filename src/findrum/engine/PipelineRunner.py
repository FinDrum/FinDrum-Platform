import yaml
import logging
from datetime import datetime
from findrum.registry.Registry import get_operator

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
            id = step["id"]
            operator = step["operator"]
            depends_on = step.get("depends_on")
            params = step.get("params", {})

            resolved_params = {
                k: self.param_overrides.get(k, v) for k, v in params.items()
            }

            input_data = self.results.get(depends_on) if depends_on else None

            OperatorClass = get_operator(operator)
            operator = OperatorClass(**resolved_params)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"[{timestamp}] → Excuting step: {id}")

            self.results[id] = operator.run(input_data)

        return self.results

    @classmethod
    def from_yaml(cls, path):
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        pipeline_def = config.get("pipeline")
        if pipeline_def is None:
            raise ValueError(f"File {path} does not contain 'pipeline' section.")
        return cls(pipeline_def)
