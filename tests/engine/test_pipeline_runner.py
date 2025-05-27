import pytest
from findrum.engine.PipelineRunner import PipelineRunner

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