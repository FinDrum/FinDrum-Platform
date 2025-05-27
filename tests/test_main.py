import pytest
import sys
from unittest.mock import patch, MagicMock
import findrum.__main__ as main_module

@patch("findrum.__main__.Platform")
def test_main_execution(mock_platform_class):
    test_args = ["prog", "pipeline.yaml", "--config=config.yaml", "--verbose"]

    with patch.object(sys, "argv", test_args):
        mock_platform = MagicMock()
        mock_platform_class.return_value = mock_platform

        main_module.main()

        mock_platform_class.assert_called_once_with("config.yaml")
        mock_platform.register_pipeline.assert_called_once_with("pipeline.yaml")
        mock_platform.start.assert_called_once()