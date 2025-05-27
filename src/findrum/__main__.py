from findrum.engine.platform import Platform
import argparse
import sys
import os
import logging
logger = logging.getLogger("findrum")

user_root = os.getcwd()
if user_root not in sys.path:
    sys.path.insert(0, user_root)

def main():
    parser = argparse.ArgumentParser(description="Run Findrum pipelines")
    parser.add_argument("pipeline", help="Path to the pipeline YAML file")
    parser.add_argument("--config", default="config.yaml", help="Path to extension config YAML")
    parser.add_argument("--verbose", action="store_true", help="Show info-level logs")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s | [%(levelname)s] | %(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
        logger.info("Verbose logging enabled.")

    platform = Platform(args.config)
    platform.register_pipeline(args.pipeline)

    if platform.scheduler.get_jobs():
        platform.start()