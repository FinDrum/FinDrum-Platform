from abc import ABC, abstractmethod
from findrum.engine.PipelineRunner import PipelineRunner

class EventTrigger(ABC):
    def __init__(self, config: dict, pipeline_path: str):
        self.config = config
        self.pipeline_path = pipeline_path

    @abstractmethod
    def start(self):
        pass

    def _run_pipeline(self, overrides: dict = None):
        """Internal method for executing the pipeline with optional overrides."""
        from datetime import datetime
        import logging

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"[{timestamp}] 📡 Executing pipeline from {self.pipeline_path}")

        runner = PipelineRunner.from_yaml(self.pipeline_path)
        if overrides:
            runner.override_params(overrides)
        runner.run()