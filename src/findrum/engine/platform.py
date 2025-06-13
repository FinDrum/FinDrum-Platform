import os
import time
import yaml
import json
import hashlib
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from findrum.loader.load_extensions import load_extensions
from findrum.engine.pipeline_runner import PipelineRunner
from findrum.registry.registry import SCHEDULER_REGISTRY, get_trigger

logger = logging.getLogger("findrum")


class Platform:
    def __init__(self, extensions_config: str = "config.yaml", verbose: bool = False, verbose: bool = False):
        self.extensions_config = extensions_config
        self.verbose = verbose
        self.scheduler = BlockingScheduler()

        self.event_trigger_map = {}
        self.event_instances = {}

        self._setup_logging()
        load_extensions(self.extensions_config)

    def _setup_logging(self):
        if self.verbose:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s | [%(levelname)s] | %(message)s"))
            logger.addHandler(handler)
            logger.propagate = False
            logger.info("Verbose mode enabled.")

    def register_pipeline(self, pipeline_path: str):
        if not os.path.exists(pipeline_path):
            raise FileNotFoundError(f"Pipeline not found: {pipeline_path}")

        with open(pipeline_path, "r") as f:
            config = yaml.safe_load(f)

        runner = PipelineRunner(config)

        if "event" in config:
            self._register_event_pipeline(config["event"], runner, pipeline_path)
            return

        if "scheduler" in config:
            self._register_scheduler(config["scheduler"], pipeline_path)
            return

        logger.info(f"🚀 Running unscheduled pipeline: {pipeline_path}")
        runner.run()

    def _register_event_pipeline(self, event_def: dict, runner: PipelineRunner, pipeline_path: str):
        event_key = self._get_event_key(event_def)

        self.event_trigger_map.setdefault(event_key, []).append(runner)

        if event_key not in self.event_instances:
            TriggerClass = get_trigger(event_def["type"])
            trigger_instance = TriggerClass(**event_def.get("config", {}))

            def emit(data, key=event_key):
                for r in self.event_trigger_map[key]:
                    r.run_with_data(data)

            trigger_instance.emit = emit
            self.event_instances[event_key] = trigger_instance

            logger.info(f"🔔 Created trigger: {event_def['type']}")

        logger.info(f"🔗 Pipeline '{pipeline_path}' registered to event trigger.")
    
    def _get_event_key(self, event_def: dict) -> str:
        key = {
            "type": event_def.get("type"),
            "config": event_def.get("config", {})
        }
        return hashlib.md5(json.dumps(key, sort_keys=True).encode()).hexdigest()

    def _register_scheduler(self, scheduler_block: dict, pipeline_path: str):
        scheduler_type = scheduler_block.get("type")
        scheduler_config = scheduler_block.get("config", {})

        SchedulerClass = SCHEDULER_REGISTRY.get(scheduler_type)
        if not SchedulerClass:
            raise ValueError(f"Scheduler '{scheduler_type}' not registered")

        scheduler_instance = SchedulerClass(config=scheduler_config, pipeline_path=pipeline_path)
        scheduler_instance.register(self.scheduler)
        logger.info(f"⏱️ Scheduler registered: {scheduler_type} → {pipeline_path}")

    def start(self):
        jobs = self.scheduler.get_jobs()
        logger.info(f"📋 Scheduler jobs found: {len(jobs)}")

        for trigger in self.event_instances.values():
            logger.info(f"🟢 Starting trigger: {trigger.__class__.__name__}")
            trigger.start()

        if jobs:
            logger.info("🔁 Starting scheduler...")
            self.scheduler.start()
        elif self.event_instances:
            logger.info("🟢 Event triggers detected. Keeping process alive...")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("⛔ Interrupt received. Exiting.")

        logger.info("✅ No active schedulers or triggers. Shutting down.")