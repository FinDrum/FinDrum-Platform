# FinDrum

**FinDrum** is a lightweight Python framework for building and orchestrating data pipelines with extensible architecture via operators, datasources, schedulers, and triggers.

This repository (`FinDrum-Platform`) is the core package and is **meant to be used as a library**. Custom logic (pipelines and extensions) should be defined in external projects.

---

## Installation

```bash
pip install findrum-platform
```

---

## Overview

Findrum pipelines are defined in YAML files and can include:

- A sequence of operators
- A datasource (provides data from external source)
- A scheduler (to run periodically)
- An event trigger (to respond to real-time events)

## Example structures:

### Example with `scheduler` and batch `datasource`:

```yaml
scheduler:
  type: MyCustomScheduler

pipeline:
  - id: batch_ingest
    datasource: MyDataSource
    params:
      key: value

  - id: transform
    operator: MyOperator
    depends_on: batch_ingest
    params:
      key: value
```

### Example with `event` and `pipeline`

```yaml
event:
  type: MyTrigger
  config:
    key: value

pipeline:
  - id: step1
    operator: MyOperator
    depends_on: MyTrigger
    params:
      key: value

  - id: step2
    operator: DownstreamOperator
    depends_on: step1
```

---

## Interfaces

Findrum provides a minimal interface for each pipeline component. These are **abstract base classes** that must be subclassed by your custom logic.

### `Operator` – Core processing unit

```python
from findrum.interfaces import Operator

class MyOperator(Operator):
    def run(self, input_data):
        ...
```

Use when defining a step in a pipeline. Must implement `run(input_data)`. We recommend that it returns a `pandas.DataFrame`.

---

### `DataSource` – Step that starts a pipeline

```python
from findrum.interfaces import DataSource

class MySource(DataSource):
    def fetch(self, **kwargs):
        ...
```

We recommend that it returns a `pandas.DataFrame`. It feeds the pipeline with data.

---

### `Scheduler` – Periodic trigger for pipelines

```python
from findrum.interfaces import Scheduler

class MyScheduler(Scheduler):
    def register(self, scheduler):
        # e.g., add job to APScheduler instance
        ...
```

Implements logic to execute the pipeline on a time interval or schedule.

---

### `EventTrigger` – React to system/file/bucket events

```python
from findrum.interfaces import EventTrigger

class MyTrigger(EventTrigger):
    def start(self):
        # Starts a file watcher, webhook listener, etc.
        ...
```

Runs the pipeline when an **external event occurs** (e.g., new Kafka message, file in MinIO). The trigger should call `self.emit(data)` to push input into the pipeline.

---

## Core Classes

You can import and use the main classes provided by Findrum:

```python
from findrum import Platform
```

- `Platform`: Main entrypoint to manage pipelines, register them, and run based on schedule or events.

---

## CLI Usage: `findrum-run`

After installing `findrum-platform`, a CLI tool is available:

### Run a pipeline immediately

```bash
findrum-run pipelines/my_pipeline.yaml
```

### Use a custom config file for extensions

```bash
findrum-run pipelines/my_pipeline.yaml --config config/config.yaml
```

### Enable logging (INFO level)

```bash
findrum-run pipelines/my_pipeline.yaml --verbose
```

---

## Extension Discovery

Findrum requires a `config.yaml` file with registered class paths:

```yaml
operators:
  - my_project.operators.MyCustomOperator

datasources:
  - my_project.datasources.MyDataSource

schedulers:
  - my_project.schedulers.MyScheduler

triggers:
  - my_project.triggers.MyTrigger
```

This lets Findrum dynamically import your components.

---

## Minimal Example For a Non-CLI runner

```python
from findrum import Platform

platform = Platform("config.yaml")
platform.register_pipeline("pipelines/my_pipeline.yaml")
platform.start()
```

You can also run your pipelines from a python file (like main.py for example) following the example above.

---

## Clean Project Structure

A typical project using Findrum should look like:

```
your-project/
├── operators/
│   └── my_operator.py
├── schedulers/
│   └── my_scheduler.py
├── triggers/
│   └── my_trigger.py
├── datasources/
│   └── my_datasource.py
├── pipelines/
│   └── my_pipeline.yaml
├── config.yaml
└── main.py (optional)
```

## Getting Started With Examples

To get started quickly, FinDrum includes runnable examples in the [`examples/`](./examples) folder.
