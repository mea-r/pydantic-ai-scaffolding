import unittest
import os
import json
from pathlib import Path
from unittest.mock import patch

# Assuming the ConfigHelper class is in src/helpers/config_helper.py
from helpers.config_helper import ConfigHelper, Config, Defaults, LimitConfig

# Define a dummy config file path for testing
TEST_CONFIG_PATH = Path(__file__).parent / 'test_config_helper_config.json'

# Initial content for the dummy config file
INITIAL_CONFIG_CONTENT = {
    "defaults": {"model": "default_model_1"},
    "daily_limits": {"per_model": {"model_a": 100}, "per_service": {"service_x": 500}},
    "monthly_limits": {"per_model": {"model_b": 1000}, "per_service": {"service_y": 5000}},
    "model_mappings": {"alias_a": "model_a"},
    "excluded_models": ["model_c"],
    "mode": "strict"
}

class TestConfigHelper(unittest.TestCase):

    def setUp(self):
        # Create a dummy config file before each test
        os.makedirs(TEST_CONFIG_PATH.parent, exist_ok=True)
        with open(TEST_CONFIG_PATH, 'w') as f:
            json.dump(INITIAL_CONFIG_CONTENT, f, indent=4)

        # Patch the ConfigHelper to use the dummy config file path
        # This is necessary to prevent the ConfigHelper from trying to load
        # the actual config.json in the project root during testing.
        patcher_config_path = patch('helpers.config_helper.ConfigHelper.config_path', new=str(TEST_CONFIG_PATH))
        self.mock_config_path = patcher_config_path.start()


    def tearDown(self):
        # Clean up the dummy config file after each test
        if os.path.exists(TEST_CONFIG_PATH):
            os.remove(TEST_CONFIG_PATH)

        # Stop all patches
        patch.stopall()

    def test_load_config(self):
        config_helper = ConfigHelper()
        self.assertIsInstance(config_helper.configuration, Config)
        self.assertEqual(config_helper.configuration.defaults.model, "default_model_1")
        self.assertEqual(config_helper.configuration.daily_limits.per_model, {"model_a": 100})
        self.assertIn("model_c", config_helper.configuration.excluded_models)
        self.assertEqual(config_helper.configuration.mode, "strict")

    def test_get_config(self):
        config_helper = ConfigHelper()
        self.assertEqual(config_helper.get_config('mode'), "strict")
        self.assertEqual(config_helper.get_config('excluded_models'), ["model_c"])
        self.assertIsNone(config_helper.get_config('non_existent_key'))

    def test_append_config(self):
        config_helper = ConfigHelper()
        config_helper.append_config('mode', 'loose')
        config_helper.append_config('defaults', Defaults(model='new_default'))

        # Verify in memory
        self.assertEqual(config_helper.configuration.mode, 'loose')
        self.assertEqual(config_helper.configuration.defaults.model, 'new_default')

        # Verify in file
        with open(TEST_CONFIG_PATH, 'r') as f:
            updated_config = json.load(f)
        self.assertEqual(updated_config['mode'], 'loose')
        self.assertEqual(updated_config['defaults']['model'], 'new_default')

    def test_append_config_list(self):
        config_helper = ConfigHelper()
        config_helper.append_config_list('excluded_models', 'model_d')
        config_helper.append_config_list('excluded_models', 'model_e')

        # Verify in memory
        self.assertIn('model_d', config_helper.configuration.excluded_models)
        self.assertIn('model_e', config_helper.configuration.excluded_models)
        self.assertEqual(len(config_helper.configuration.excluded_models), 3) # model_c + model_d + model_e

        # Verify in file
        with open(TEST_CONFIG_PATH, 'r') as f:
            updated_config = json.load(f)
        self.assertIn('model_d', updated_config['excluded_models'])
        self.assertIn('model_e', updated_config['excluded_models'])
        self.assertEqual(len(updated_config['excluded_models']), 3)

    def test_append_config_list_non_list(self):
        config_helper = ConfigHelper()
        with self.assertRaises(ValueError) as cm:
            config_helper.append_config_list('mode', 'new_mode')
        self.assertIn("Key 'mode' is not a list. Cannot append value.", str(cm.exception))

    def test_config_property(self):
        config_helper = ConfigHelper()
        config_obj = config_helper.config
        self.assertIsInstance(config_obj, Config)
        self.assertEqual(config_obj.mode, "strict")

    def test_file_not_found(self):
        # Remove the dummy file to simulate file not found
        if os.path.exists(TEST_CONFIG_PATH):
            os.remove(TEST_CONFIG_PATH)

        with self.assertRaises(FileNotFoundError):
            ConfigHelper()

if __name__ == '__main__':
    unittest.main()
