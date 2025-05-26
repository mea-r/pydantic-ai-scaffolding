import unittest
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

# Assuming the cli_helper_functions is in src/helpers/cli_helper_functions.py
from helpers.cli_helper_functions import flag_non_working_models
from helpers.config_helper import ConfigHelper
from py_models.weather.model import WeatherModel
from py_models.base import LLMReport
from pydantic_ai.usage import Usage

# Define a dummy config file path for testing
TEST_CONFIG_PATH = Path(__file__).parent / 'test_config.json'
TEST_REPORT_FILE = Path(__file__).parent / 'logs/test_tool_call_errors.txt'

# Initial content for the dummy config file
INITIAL_CONFIG_CONTENT = {
    "defaults": {"model": "some_model"},
    "daily_limits": {},
    "monthly_limits": {},
    "model_mappings": {},
    "excluded_models": [],
    "mode": "strict"
}

class TestCliHelperFunctions(unittest.TestCase):

    def setUp(self):
        # Create a dummy config file before each test
        with open(TEST_CONFIG_PATH, 'w') as f:
            json.dump(INITIAL_CONFIG_CONTENT, f, indent=4)

        # Patch the ConfigHelper to use the dummy config file
        # This is a necessary mock to control the config file used by the function
        # without modifying the actual config.json.
        patcher_config_helper_path = patch('helpers.config_helper.ConfigHelper.__init__', return_value=None)
        self.mock_config_helper_init = patcher_config_helper_path.start()
        self.mock_config_helper_init.side_effect = lambda self: setattr(self, 'config_path', str(TEST_CONFIG_PATH))

        patcher_config_helper_load = patch('helpers.config_helper.ConfigHelper._load')
        self.mock_config_helper_load = patcher_config_helper_load.start()
        self.mock_config_helper_load.side_effect = lambda: ConfigHelper(base_path=str(TEST_CONFIG_PATH.parent))._load()

        patcher_config_helper_save = patch('helpers.config_helper.ConfigHelper._save')
        self.mock_config_helper_save = patcher_config_helper_save.start()
        self.mock_config_helper_save.side_effect = lambda self: ConfigHelper(base_path=str(TEST_CONFIG_PATH.parent))._save()

        patcher_config_helper_get_config = patch('helpers.config_helper.ConfigHelper.get_config')
        self.mock_config_helper_get_config = patcher_config_helper_get_config.start()
        self.mock_config_helper_get_config.side_effect = lambda key: ConfigHelper(base_path=str(TEST_CONFIG_PATH.parent)).get_config(key)

        patcher_config_helper_append_config_list = patch('helpers.config_helper.ConfigHelper.append_config_list')
        self.mock_config_helper_append_config_list = patcher_config_helper_append_config_list.start()
        self.mock_config_helper_append_config_list.side_effect = lambda key, value: ConfigHelper(base_path=str(TEST_CONFIG_PATH.parent)).append_config_list(key, value)


        # Patch LLMInfoProvider to return a predictable list of models
        patcher_info_provider = patch('helpers.cli_helper_functions.LLMInfoProvider')
        self.mock_info_provider_class = patcher_info_provider.start()
        self.mock_info_provider_instance = MagicMock()
        self.mock_info_provider_class.return_value = self.mock_info_provider_instance
        self.mock_info_provider_instance.get_models.return_value = [
            'provider1/model_working',
            'provider2/model_failing_weather_model',
            'provider3/model_failing_haiku_report',
            'provider4/model_raising_exception',
            'openai/o4-mini-high' # Model to start from
        ]

        # Patch print to capture output
        patcher_print = patch('builtins.print')
        self.mock_print = patcher_print.start()

        # Patch test_weather - This is the core function being tested indirectly.
        # To test flag_non_working_models without mocking test_weather, we would need
        # a real test_weather function that interacts with real LLMs, which is not feasible.
        # Therefore, I will simulate the behavior of test_weather.
        patcher_test_weather = patch('helpers.cli_helper_functions.test_weather')
        self.mock_test_weather = patcher_test_weather.start()

        # Configure the mock test_weather to simulate different outcomes
        def mock_test_weather_side_effect(model_name, provider):
            if model_name == 'provider1/model_working':
                # Simulate a successful run
                weather_model = WeatherModel(tool_results={}, haiku="A haiku about Sofia", report="Weather report for Sofia")
                report = LLMReport(model_name=model_name, usage=Usage(), cost=0.01)
                return weather_model, report
            elif model_name == 'provider2/model_failing_weather_model':
                # Simulate returning something not a WeatherModel
                report = LLMReport(model_name=model_name, usage=Usage(), cost=0.01)
                return "Not a WeatherModel", report
            elif model_name == 'provider3/model_failing_haiku_report':
                # Simulate returning a WeatherModel without 'Sofia' in haiku/report
                weather_model = WeatherModel(tool_results={}, haiku="A haiku about London", report="Weather report for London")
                report = LLMReport(model_name=model_name, usage=Usage(), cost=0.01)
                return weather_model, report
            elif model_name == 'provider4/model_raising_exception':
                # Simulate an exception during test_weather call
                raise Exception("Simulated LLM error")
            elif model_name == 'openai/o4-mini-high':
                 # Simulate a successful run for the starting model
                weather_model = WeatherModel(tool_results={}, haiku="A haiku about Sofia", report="Weather report for Sofia")
                report = LLMReport(model_name=model_name, usage=Usage(), cost=0.01)
                return weather_model, report
            else:
                # Default for unexpected models
                return None, None

        self.mock_test_weather.side_effect = mock_test_weather_side_effect


    def tearDown(self):
        # Clean up the dummy config file and report file
        if os.path.exists(TEST_CONFIG_PATH):
            os.remove(TEST_CONFIG_PATH)
        if os.path.exists(TEST_REPORT_FILE):
            os.remove(TEST_REPORT_FILE)

        # Stop all patches
        patch.stopall()

    def test_flag_non_working_models(self):
        # Run the function, passing the test report file path
        flag_non_working_models(report_file_path=str(TEST_REPORT_FILE))

        # Assertions

        # Check if test_weather was called for the expected models (starting from 'openai/o4-mini-high')
        expected_calls = [
            unittest.mock.call(model_name='openai/o4-mini-high', provider='open_router'),
            unittest.mock.call(model_name='provider1/model_working', provider='open_router'),
            unittest.mock.call(model_name='provider2/model_failing_weather_model', provider='open_router'),
            unittest.mock.call(model_name='provider3/model_failing_haiku_report', provider='open_router'),
            unittest.mock.call(model_name='provider4/model_raising_exception', provider='open_router'),
        ]
        self.mock_test_weather.assert_has_calls(expected_calls, any_order=False)


        # Check if excluded_models in the config file were updated correctly
        config_helper = ConfigHelper(base_path=str(TEST_CONFIG_PATH.parent))
        excluded_models = config_helper.get_config('excluded_models')

        # The models that should be excluded are:
        # provider2/model_failing_weather_model (returns wrong type)
        # provider3/model_failing_haiku_report (missing 'Sofia')
        # provider4/model_raising_exception (raises exception)
        expected_excluded = [
            'provider2/model_failing_weather_model',
            'provider3/model_failing_haiku_report',
            'provider4/model_raising_exception'
        ]
        self.assertCountEqual(excluded_models, expected_excluded)

        # Check if the report file was written for failing models
        with open(TEST_REPORT_FILE, 'r') as f:
            report_content = f.read()

        self.assertIn("Model: provider4/model_raising_exception Error: Simulated LLM error", report_content)
        self.assertIn("Model: provider2/model_failing_weather_model did not return a valid WeatherModel instance", report_content)
        self.assertIn("Incomplete response from provider3/model_failing_haiku_report", report_content)
        # Ensure the working model is not in the report file
        self.assertNotIn("Model: provider1/model_working", report_content)
        self.assertNotIn("Model: openai/o4-mini-high", report_content)


if __name__ == '__main__':
    unittest.main()
