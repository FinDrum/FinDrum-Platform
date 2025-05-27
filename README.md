# 📘 Findrum Platform

Welcome to **Findrum** — a flexible framework for defining and executing data pipelines with support for **custom operators**, **data sources**, **schedulers**, and **event-based triggers**.

---

## 🚀 What is Findrum?

Findrum lets you:

- Compose pipelines using YAML.
- Extend the framework by implementing your own operators, data sources, triggers, and schedulers.
- Run pipelines on a schedule or in response to external events (e.g., file creation).
- Keep platform logic separate from user-defined behavior.

---

## 🧱 Project Structure

```
findrum/                  # Core framework
├── engine/               # Platform and PipelineRunner
├── interfaces/           # Base interfaces (Operator, Scheduler, EventTrigger)
├── registry/             # Component registries
├── loader/               # Extension loader
├── __main__.py           # CLI entry point
operators/                # Your custom operators & data sources
schedulers/               # Your custom schedulers
triggers/                 # Your custom event triggers
pipelines/                # YAML pipeline definitions
config.yaml               # Extension registration
requirements.txt
pyproject.toml
README.md
```

---

## ⚙️ 1. Requirements

- Python **3.12**
- Recommended: `virtualenv`
- Linux/macOS/Windows compatible

### Install Python 3.12

#### Using `pyenv` (Linux/macOS)

```bash
curl https://pyenv.run | bash

# Add to shell config (.bashrc, .zshrc)
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

# Restart terminal
pyenv install 3.12.9
pyenv global 3.12.9
```

#### On Windows

Download and install from [Python.org](https://www.python.org/downloads/release/python-3120/), check "Add to PATH" during install.

---

## 💼 2. Setup Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### Install Findrum

```bash
pip install .
```

### In case that you want to try the example files. You would need to execute

```bash
pip install -r requirements.txt
```

---

## 🧩 3. Register Extensions

In `config.yaml`:

```yaml
operators:
  - operators.my_operators.SaveToCSVOperator
  - operators.my_operators.PrintCSVOperator
  - operators.my_sources.CustomDataSource

schedulers:
  - schedulers.my_schedulers.Every10SecondsScheduler

triggers:
  - triggers.my_triggers.LocalCSVTrigger
```

---

## 🔧 4. Implement Components

You can implement and register your own components by extending the provided interfaces.

---

### ✅ 1. Custom Operator

```python
# operators/my_operators.py
import pandas as pd
from findrum.interfaces.Operator import Operator

class SaveToCSVOperator(Operator):
    def run(self, input_data):
        if isinstance(input_data, pd.DataFrame):
            input_data.to_csv(self.params['path_output'], index=False)
            print("💾 Data saved to output.csv")
        return input_data

class PrintCSVOperator(Operator):
    def run(self, input_data):
        df = pd.read_csv(self.params['path_input'])
        print("🖨️ CSV file content:")
        print(df)
        return df
```

---

### ✅ 2. Custom DataSource

```python
# operators/my_sources.py
import pandas as pd
from findrum.interfaces.DataSource import DataSource

class CustomDataSource(DataSource):
    def fetch(self, **kwargs):
        return pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })
```

---

### ✅ 3. Custom Scheduler

```python
# schedulers/my_schedulers.py
from apscheduler.triggers.interval import IntervalTrigger
from findrum.interfaces.Scheduler import Scheduler
from findrum.engine.PipelineRunner import PipelineRunner

class Every10SecondsScheduler(Scheduler):
    def register(self, scheduler):
        trigger = IntervalTrigger(seconds=10)
        scheduler.add_job(
            func=self._run_pipeline,
            trigger=trigger,
            id=self.pipeline_path,
            name=f"{self.pipeline_path} (every 10s)",
            replace_existing=True
        )
```

---

### ✅ 4. Custom Event Trigger

```python
# triggers/my_triggers.py
import time
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from findrum.interfaces.EventTrigger import EventTrigger
from findrum.engine.PipelineRunner import PipelineRunner

class LocalFileTrigger(EventTrigger):
    def start(self):
        path_to_watch = self.config.get("path", ".")
        file_suffix = self.config.get("suffix", ".csv")

        logging.info(f"👀 Watching folder: {path_to_watch} (files *{file_suffix})")

        class Handler(FileSystemEventHandler):
            def __init__(self, pipeline_path):
                self.last_run_time = 0
                self.pipeline_path = pipeline_path

            def on_modified(self, event):
                if event.is_directory or not event.src_path.endswith(file_suffix):
                    return
                now = time.time()
                if now - self.last_run_time < 2:
                    return
                self.last_run_time = now
                logging.info(f"📂 File modified: {event.src_path}")

                logging.info(f"📡 Executing pipeline from {self.pipeline_path}")

                runner = PipelineRunner.from_yaml(self.pipeline_path)
                runner.override_params({"file_path": event.src_path})
                runner.run()

        observer = Observer()
        handler = Handler(self.pipeline_path)
        observer.schedule(handler, path=path_to_watch, recursive=False)

        def run_observer():
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        thread = threading.Thread(target=run_observer, daemon=True)
        thread.start()
```

---

### ✅ 5. Define Pipelines

```yaml
# pipelines/mock_pipeline.yaml
scheduler:
  type: Every10SecondsScheduler

pipeline:
  - id: fetch
    operator: CustomDataSource
  - id: save
    operator: SaveToCSVOperator
    depends_on: fetch
    params:
      path_output: "output.csv"
```

```yaml
# pipelines/event_listener_pipeline.yaml
event:
  type: LocalCSVTrigger
  config:
    path: .
    suffix: .csv

pipeline:
  - id: load
    operator: PrintCSVOperator
    params:
      path_input: "output.csv"
```

---

### ✅ 6. Run the Platform

#### Run via CLI (Preferred)

```bash
findrum-run pipelines/mock_pipeline.yaml
```

Add `--config` to define config path:

```bash
findrum-run pipelines/mock_pipeline.yaml --config config/config.yaml
```

Add `--verbose` for full logging output:

```bash
findrum-run pipelines/mock_pipeline.yaml --verbose
```

✅ Use ps aux | grep findrum and kill <PID> to stop background processes.

#### Optional main.py Script

```python
# main.py
from findrum.engine.Platform import Platform

if __name__ == "__main__":
    platform = Platform("config.yaml")
    platform.register_pipeline("pipelines/mock_pipeline.yaml")
    platform.register_pipeline("pipelines/event_listener_pipeline.yaml")
    platform.start()
```
