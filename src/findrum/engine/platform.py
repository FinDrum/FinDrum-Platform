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
    """Main entry point for managing and running Findrum pipelines.

    The Platform class loads user-defined extensions (operators, triggers,
    schedulers, datasources), registers pipelines defined in YAML configuration
    files, and runs them either as scheduled jobs or in response to events.
    """

    def __init__(self, extensions_config: str = "config.yaml", verbose: bool = False):
        """Initialize the platform, load extensions, and prepare the scheduler.

        Args:
            extensions_config (str): Path to the YAML file for custom extension classes.
            verbose (bool): Whether to enable verbose logging to the console.
        """
        self.extensions_config = extensions_config
        self.verbose = verbose
        self.scheduler = BlockingScheduler()

        self.event_trigger_map = {}
        self.event_instances = {}

        self._setup_logging()
        load_extensions(self.extensions_config)

    def _setup_logging(self):
        """Configure logging if verbose mode is enabled."""
        if self.verbose:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s | [%(levelname)s] | %(message)s"))
            logger.addHandler(handler)
            logger.propagate = False
            logger.info("Verbose mode enabled.")

    def register_pipeline(self, pipeline_path: str):
        """Register a pipeline defined in a YAML file for execution.

        Depending on the config, the pipeline may be executed immediately,
        registered to an event trigger, or scheduled.

        Args:
            pipeline_path (str): Path to the pipeline configuration file.

        Raises:
            FileNotFoundError: If the pipeline file does not exist.
        """
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
        """Register a pipeline to be triggered by a specific event.

        Args:
            event_def (dict): Event configuration block from pipeline YAML.
            runner (PipelineRunner): The pipeline runner instance.
            pipeline_path (str): Path to the pipeline file.
        """
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
        """Generate a consistent hash key for an event configuration.

        Args:
            event_def (dict): The event definition block.

        Returns:
            str: A unique MD5 hash representing the event configuration.
        """
        key = {
            "type": event_def.get("type"),
            "config": event_def.get("config", {})
        }
        return hashlib.md5(json.dumps(key, sort_keys=True).encode()).hexdigest()

    def _register_scheduler(self, scheduler_block: dict, pipeline_path: str):
        """Register a pipeline to a scheduler.

        Args:
            scheduler_block (dict): Scheduler configuration block from pipeline YAML.
            pipeline_path (str): Path to the pipeline file.

        Raises:
            ValueError: If the scheduler type is not registered.
        """
        scheduler_type = scheduler_block.get("type")
        scheduler_config = scheduler_block.get("config", {})

        SchedulerClass = SCHEDULER_REGISTRY.get(scheduler_type)
        if not SchedulerClass:
            raise ValueError(f"Scheduler '{scheduler_type}' not registered")

        scheduler_instance = SchedulerClass(config=scheduler_config, pipeline_path=pipeline_path)
        scheduler_instance.register(self.scheduler)
        logger.info(f"⏱️ Scheduler registered: {scheduler_type} → {pipeline_path}")

    def start(self):
        """Start the platform: run all registered triggers and schedulers.

        Triggers will begin listening for events, and schedulers will be started
        if jobs are registered. If only triggers exist, the process stays alive
        waiting for events.
        """
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