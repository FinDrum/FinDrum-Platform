OPERATOR_REGISTRY = {}
SCHEDULER_REGISTRY = {}
EVENT_TRIGGER_REGISTRY = {}

def get_operator(name: str):
    cls = OPERATOR_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Operator '{name}' not found in registry.")
    return cls

def get_trigger(name: str):
    cls = EVENT_TRIGGER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Trigger '{name}' not found in registry.")
    return cls

def get_scheduler(name: str):
    cls = SCHEDULER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Trigger '{name}' not found in registry.")
    return cls

