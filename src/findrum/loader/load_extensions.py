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
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    for category, registry_dict in CATEGORY_REGISTRY_MAP.items():
        for full_class_path in config.get(category, []):
            module_path, class_name = full_class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            registry_dict[class_name] = cls
