OPERATOR_REGISTRY = {}
SCHEDULER_REGISTRY = {}
EVENT_TRIGGER_REGISTRY = {}
DATASOURCE_REGISTRY = {}

def get_datasource(name):
    """Retrieve a datasource class from the registry by name.

    Args:
        name (str): Name of the datasource class to retrieve.

    Returns:
        Type: The datasource class.

    Raises:
        ValueError: If the datasource is not found in the registry.
    """
    if name not in DATASOURCE_REGISTRY:
        raise ValueError(f"Datasource '{name}' not found in registry.")
    return DATASOURCE_REGISTRY[name]

def get_operator(name: str):
    """Retrieve an operator class from the registry by name.

    Args:
        name (str): Name of the operator class to retrieve.

    Returns:
        Type: The operator class.

    Raises:
        ValueError: If the operator is not found in the registry.
    """
    cls = OPERATOR_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Operator '{name}' not found in registry.")
    return cls

def get_trigger(name: str):
    """Retrieve an event trigger class from the registry by name.

    Args:
        name (str): Name of the event trigger class to retrieve.

    Returns:
        Type: The event trigger class.

    Raises:
        ValueError: If the trigger is not found in the registry.
    """
    cls = EVENT_TRIGGER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Trigger '{name}' not found in registry.")
    return cls

def get_scheduler(name: str):
    """Retrieve a scheduler class from the registry by name.

    Args:
        name (str): Name of the scheduler class to retrieve.

    Returns:
        Type: The scheduler class.

    Raises:
        ValueError: If the scheduler is not found in the registry.
    """
    cls = SCHEDULER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Scheduler '{name}' not found in registry.")
    return cls

