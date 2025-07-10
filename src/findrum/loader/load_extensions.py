import yaml
import importlib

from findrum.registry import registry

CATEGORY_REGISTRY_MAP = {
    "operators": registry.OPERATOR_REGISTRY,
    "schedulers": registry.SCHEDULER_REGISTRY,
    "triggers": registry.EVENT_TRIGGER_REGISTRY,
    "datasources": registry.DATASOURCE_REGISTRY,
}

def load_extensions(config_path: str):
    """Dynamically load and register external classes from a YAML config file.

    This function reads a configuration file that lists full class paths for different
    extension categories (e.g., operators, schedulers, triggers, datasources), dynamically
    imports each class, and registers it in the appropriate registry.

    The expected YAML structure is:
        operators:
          - mypackage.my_operator.CustomOperator
        schedulers:
          - mypackage.my_scheduler.CustomScheduler
        triggers:
          - mypackage.my_trigger.CustomTrigger
        datasources:
          - mypackage.my_datasource.CustomDataSource

    Args:
        config_path (str): Path to the YAML configuration file containing class paths.

    Raises:
        ImportError: If a module or class cannot be imported.
        AttributeError: If the specified class does not exist in the module.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    for category, registry_dict in CATEGORY_REGISTRY_MAP.items():
        for full_class_path in config.get(category, []):
            module_path, class_name = full_class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            registry_dict[class_name] = cls

