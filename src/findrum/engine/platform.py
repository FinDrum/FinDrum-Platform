import yaml
import os
import logging
import time
logger = logging.getLogger("findrum")
from apscheduler.schedulers.blocking import BlockingScheduler

from findrum.loader.load_extensions import load_extensions
from findrum.engine.pipeline_runner import PipelineRunner
from findrum.registry.registry import SCHEDULER_REGISTRY

class Platform:
    def __init__(self, extensions_config: str = "config.yaml", verbose: bool = False):
        self.extensions_config = extensions_config
        self.scheduler = BlockingScheduler()
        self.has_event_triggers = False
        self.verbose = verbose

        if self.verbose:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s | [%(levelname)s] | %(message)s"))
            logger.addHandler(handler)
            logger.propagate = False
            logger.info("Verbose mode enabled.")
        load_extensions(self.extensions_config)

    def register_pipeline(self, pipeline_path: str):
        if not os.path.exists(pipeline_path):
            raise FileNotFoundError(f"Pipeline not found: {pipeline_path}")

        with open(pipeline_path) as f:
            config = yaml.safe_load(f)

        if "event" in config:
            self.has_event_triggers = True
            logger.info(f"🔔 Event trigger detected in: {pipeline_path}")

        if "scheduler" in config:
            self._register_scheduler(config["scheduler"], pipeline_path)
        elif "event" not in config:
            logger.info(f"🚀 Running unscheduled pipeline: {pipeline_path}")
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
        jobs = self.scheduler.get_jobs()
        logger.info(f"📋 Scheduler jobs found: {len(jobs)}")

        if jobs:
            logger.info("🔁 Starting scheduler...")
            self.scheduler.start()
        elif self.has_event_triggers:
            logger.info("🟢 Event triggers detectados. Manteniendo proceso activo...")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("⛔ Interrupción recibida. Saliendo.")
        else:
            logger.info("✅ No hay schedulers ni triggers activos. Finalizando.")