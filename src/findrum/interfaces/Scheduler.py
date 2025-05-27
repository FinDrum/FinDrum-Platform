from abc import ABC, abstractmethod

import logging

from findrum.engine.PipelineRunner import PipelineRunner

class Scheduler(ABC):
    def __init__(self, config, pipeline_path):
        self.config = config
        self.pipeline_path = pipeline_path

    @abstractmethod
    def register(self, scheduler):
        pass
    
    def _run_pipeline(self):
        logging.info(f"🕒 Executing pipeline from {self.pipeline_path}")
        runner = PipelineRunner.from_yaml(self.pipeline_path)
        runner.run()