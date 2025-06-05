import yaml
import os
import logging
logger = logging.getLogger("findrum")
import threading
from apscheduler.schedulers.blocking import BlockingScheduler

from findrum.loader.load_extensions import load_extensions
from findrum.engine.pipeline_runner import PipelineRunner
from findrum.registry.registry import EVENT_TRIGGER_REGISTRY, SCHEDULER_REGISTRY


class Platform:
    def __init__(self, extensions_config: str = "config.yaml"):
        self.extensions_config = extensions_config
        self.scheduler = BlockingScheduler()
        load_extensions(self.extensions_config)

    def register_pipeline(self, pipeline_path: str):
        if not os.path.exists(pipeline_path):
            raise FileNotFoundError(f"Pipeline not found: {pipeline_path}")

        with open(pipeline_path) as f:
            config = yaml.safe_load(f)

        if "scheduler" in config:
            self._register_scheduler(config["scheduler"], pipeline_path)
        else:
            logger.info(f"🚀 Starting pipeline: {pipeline_path}")
            runner = PipelineRunner(config)
            runner.run()

    def _register_scheduler(self, scheduler_block, pipeline_path):
        scheduler_type = scheduler_block.get("type")
        scheduler_config = scheduler_block.get("config", {})

        SchedulerClass = SCHEDULER_REGISTRY.get(scheduler_type)
        if not SchedulerClass:
            raise ValueError(f"Scheduler '{scheduler_type}' not registered")

        logger.info(f"⏱️ Scheduler detected: {scheduler_type} → registered...")
        scheduler_instance = SchedulerClass(config=scheduler_config, pipeline_path=pipeline_path)
        scheduler_instance.register(self.scheduler)
    
    def start(self):
        if self.scheduler.get_jobs():
            logger.info("🔁 Starting scheduler...")
            self.scheduler.start()
        else:
            logger.info("✅ No scheduled jobs to run.")