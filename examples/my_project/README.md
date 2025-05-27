# My Project Example (FinDrum)

This is a minimal working example to demonstrate how to run a pipeline using [FinDrum](https://github.com/FinDrum/findrum-platform).

## 🗂️ Contents

```
my_project/
├── config.yaml            # Component registry (operators, datasources, schedulers)
├── datasource.py          # A basic DataSource returning a DataFrame
├── my_operator.py         # Two Operators: SumOperator, PrintOperator
└── sample_pipeline.yaml   # The pipeline definition
```

## 🚀 How to Run

You can execute this pipeline from different directories:

### ✅ Option 1: From `examples/`

This is the recommended way for trying the example directly:

```bash
cd examples
findrum-run my_project/sample_pipeline.yaml --config=my_project/config.yaml --verbose
```

To make this work, your `config.yaml` must refer to modules **without** the `my_project.` prefix:

```yaml
# config.yaml if running from inside this folder
operators:
  - my_project.my_operator.SumOperator
  - my_project.my_operator.PrintOperator

datasources:
  - my_project.datasource.MyDataSource
```

---

### ⚠️ Option 2: From within `my_project/`

You **can** also run it from here, but Python module resolution will behave differently:

```bash
cd examples/my_project
findrum-run sample_pipeline.yaml --config=config.yaml --verbose
```

To make this work, your `config.yaml` must refer to modules **without** the `my_project.` prefix:

```yaml
# config.yaml if running from inside this folder
operators:
  - my_operator.SumOperator
  - my_operator.PrintOperator

datasources:
  - datasource.MyDataSource
```

Alternatively, modify your `PYTHONPATH` or `sys.path` manually, but this is less portable.

---

## 🧩 Notes

- This project is **not the required structure** — it’s just an example.
- You are free to structure your real projects however you want.
- Just ensure that the class paths in `config.yaml` are valid Python import strings from your execution root.
