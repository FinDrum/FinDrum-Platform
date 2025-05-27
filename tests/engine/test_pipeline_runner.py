import pytest
from findrum.engine.pipeline_runner import PipelineRunner

def test_pipeline_runner_from_yaml_and_run(dummy_pipeline_yaml):
    runner = PipelineRunner.from_yaml(dummy_pipeline_yaml)
    results = runner.override_params({"y": 999}).run()

    assert "step1" in results
    assert "step2" in results
    assert results["step1"]["params"] == {"x": 1}
    assert results["step2"]["params"] == {"y": 999}
    assert results["step2"]["input"] == results["step1"]

def test_from_yaml_missing_pipeline_section(tmp_path):
    yaml_path = tmp_path / "invalid_pipeline.yaml"
    yaml_path.write_text("not_pipeline: []")

    with pytest.raises(ValueError, match="does not contain 'pipeline' section"):
        PipelineRunner.from_yaml(str(yaml_path))

def test_step_missing_operator_and_datasource():
    pipeline_def = [
        {"id": "step1"}
    ]
    runner = PipelineRunner(pipeline_def)
    with pytest.raises(ValueError, match="must have either 'operator' or 'datasource'"):
        runner.run()

def test_datasource_with_depends_on_should_fail():
    pipeline_def = [
        {"id": "step1", "datasource": "dummy", "depends_on": "something"}
    ]
    runner = PipelineRunner(pipeline_def)
    with pytest.raises(ValueError, match="Datasource step cannot depend on another step."):
        runner.run()