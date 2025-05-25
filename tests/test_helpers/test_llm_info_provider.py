import unittest
import os
import json
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

# Assuming the LLMInfoProvider class is in src/helpers/llm_info_provider.py
from src.helpers.llm_info_provider import LLMInfoProvider
from src.helpers.config_helper import ConfigHelper
from pydantic_ai.usage import Usage

# Define dummy file paths for testing
TEST_MODELS_JSON_PATH = Path(__file__).parent / 'test_models.json'
TEST_MODEL_MAPPINGS_JSON_PATH = Path(__file__).parent / 'test_model_mappings.json'
TEST_CONFIG_PATH = Path(__file__).parent / 'test_llm_info_provider_config.json'


# Dummy data for models.json
DUMMY_MODELS_DATA = {
    "timestamp": time.time(),
    "data": [
        {
            "id": "provider1/model_cheap",
            "pricing": {"prompt": "0.0000001", "completion": "0.0000002"},
            "supported_parameters": ["tools"]
        },
        {
            "id": "provider2/model_medium",
            "pricing": {"prompt": "0.0000003", "completion": "0.0000005"},
            "supported_parameters": ["tools"]
        },
        {
            "id": "provider3/model_expensive",
            "pricing": {"prompt": "0.0000006", "completion": "0.0000008"},
            "supported_parameters": ["tools"]
        },
        {
            "id": "provider4/model_no_tools",
            "pricing": {"prompt": "0.0000001", "completion": "0.0000002"},
            "supported_parameters": [] # No tools
        },
         {
            "id": "provider5/model_no_pricing",
            "pricing": {}, # No pricing
            "supported_parameters": ["tools"]
        }
    ]
}

# Dummy data for model_mappings.json
DUMMY_MODEL_MAPPINGS_DATA = {
    "alias_for_cheap": "provider1/model_cheap"
}

# Dummy data for config.json
DUMMY_CONFIG_CONTENT = {
    "defaults": {"model": "some_model"},
    "daily_limits": {},
    "monthly_limits": {},
    "model_mappings": {}, # This will be overridden by the dummy file
    "excluded_models": ["provider2/model_medium"], # Exclude one model
    "mode": "strict"
}


class TestLLMInfoProvider(unittest.TestCase):

    def setUp(self):
        # Create dummy files before each test
        os.makedirs(TEST_MODELS_JSON_PATH.parent, exist_ok=True)
        with open(TEST_MODELS_JSON_PATH, 'w') as f:
            json.dump(DUMMY_MODELS_DATA, f, indent=4)

        os.makedirs(TEST_MODEL_MAPPINGS_JSON_PATH.parent, exist_ok=True)
        with open(TEST_MODEL_MAPPINGS_JSON_PATH, 'w') as f:
            json.dump(DUMMY_MODEL_MAPPINGS_DATA, f, indent=4)

        os.makedirs(TEST_CONFIG_PATH.parent, exist_ok=True)
        with open(TEST_CONFIG_PATH, 'w') as f:
            json.dump(DUMMY_CONFIG_CONTENT, f, indent=4)


        # Patch file paths and requests.get to avoid external dependencies
        patcher_models_json_path = patch('src.helpers.llm_info_provider.cache_file', new=str(TEST_MODELS_JSON_PATH))
        self.mock_models_json_path = patcher_models_json_path.start()

        patcher_model_mappings_path = patch('src.helpers.llm_info_provider.path', new=str(TEST_MODEL_MAPPINGS_JSON_PATH.parent))
        self.mock_model_mappings_path = patcher_model_mappings_path.start()

        patcher_config_helper_path = patch('src.helpers.config_helper.ConfigHelper.config_path', new=str(TEST_CONFIG_PATH))
        self.mock_config_helper_path = patcher_config_helper_path.start()


        # Patch requests.get to prevent actual API calls
        patcher_requests_get = patch('src.helpers.llm_info_provider.requests.get')
        self.mock_requests_get = patcher_requests_get.start()
        # Configure the mock to return dummy data if called
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = DUMMY_MODELS_DATA
        self.mock_requests_get.return_value = mock_response


        # Patch time.time() to control caching behavior
        patcher_time = patch('src.helpers.llm_info_provider.time.time')
        self.mock_time = patcher_time.start()
        self.mock_time.return_value = time.time() # Return current time by default


    def tearDown(self):
        # Clean up dummy files after each test
        if os.path.exists(TEST_MODELS_JSON_PATH):
            os.remove(TEST_MODELS_JSON_PATH)
        if os.path.exists(TEST_MODEL_MAPPINGS_JSON_PATH):
            os.remove(TEST_MODEL_MAPPINGS_JSON_PATH)
        if os.path.exists(TEST_CONFIG_PATH):
            os.remove(TEST_CONFIG_PATH)

        # Stop all patches
        patch.stopall()

    def test_init_cost_info_loads_from_cache(self):
        # Ensure cache is recent
        self.mock_time.return_value = time.time()

        provider = LLMInfoProvider()
        # Should not call requests.get if cache is valid
        self.mock_requests_get.assert_not_called()
        self.assertEqual(len(provider._cost_info['model_data']), len(DUMMY_MODELS_DATA['data']))

    def test_init_cost_info_fetches_if_no_cache(self):
        # Remove cache file to force fetch
        if os.path.exists(TEST_MODELS_JSON_PATH):
            os.remove(TEST_MODELS_JSON_PATH)

        provider = LLMInfoProvider()
        # Should call requests.get
        self.mock_requests_get.assert_called_once()
        self.assertEqual(len(provider._cost_info['model_data']), len([m for m in DUMMY_MODELS_DATA['data'] if 'tools' in m.get('supported_parameters', [])])) # Only models with tools

        # Check if cache file was created
        self.assertTrue(os.path.exists(TEST_MODELS_JSON_PATH))

    def test_init_cost_info_fetches_if_cache_expired(self):
        # Set cache time to be old
        self.mock_time.return_value = time.time() + 86401 # 1 day + 1 second

        provider = LLMInfoProvider()
        # Should call requests.get
        self.mock_requests_get.assert_called_once()
        self.assertEqual(len(provider._cost_info['model_data']), len([m for m in DUMMY_MODELS_DATA['data'] if 'tools' in m.get('supported_parameters', [])]))

    def test_get_models(self):
        provider = LLMInfoProvider()
        models = provider.get_models()
        # Should exclude the model in excluded_models and models without tools
        expected_models = [
            'provider1/model_cheap',
            'provider3/model_expensive'
        ]
        self.assertCountEqual(models, expected_models)

    def test_get_models_include_excluded(self):
        provider = LLMInfoProvider()
        models = provider.get_models(include_excluded=True)
        # Should include all models from dummy data except those without tools
        expected_models = [
            'provider1/model_cheap',
            'provider2/model_medium',
            'provider3/model_expensive',
            'provider5/model_no_pricing'
        ]
        self.assertCountEqual(models, expected_models)


    def test_get_price_list(self):
        provider = LLMInfoProvider()
        price_list = provider.get_price_list()

        # Check if excluded models are not in the price list
        self.assertNotIn('provider2/model_medium', price_list)
        self.assertNotIn('provider4/model_no_tools', price_list)

        # Check if models without pricing are not in the price list
        self.assertNotIn('provider5/model_no_pricing', price_list)

        # Check sorting (cheapest to most expensive by completion price)
        model_ids = list(price_list.keys())
        self.assertEqual(model_ids[0], 'provider1/model_cheap')
        self.assertEqual(model_ids[1], 'provider3/model_expensive') # Medium is excluded

        # Check pricing values (multiplied by 1,000,000 and rounded)
        self.assertEqual(price_list['provider1/model_cheap']['prompt'], 0.1)
        self.assertEqual(price_list['provider1/model_cheap']['completion'], 0.2)
        self.assertEqual(price_list['provider3/model_expensive']['prompt'], 0.6)
        self.assertEqual(price_list['provider3/model_expensive']['completion'], 0.8)


    def test_format_price_list(self):
        provider = LLMInfoProvider()
        formatted_list = provider.format_price_list()

        self.assertIsInstance(formatted_list, str)
        self.assertIn("Model ID", formatted_list)
        self.assertIn("Price Category", formatted_list)
        self.assertIn("provider1/model_cheap", formatted_list)
        self.assertIn("provider3/model_expensive", formatted_list)
        self.assertNotIn("provider2/model_medium", formatted_list) # Excluded
        self.assertNotIn("provider4/model_no_tools", formatted_list) # No tools
        self.assertNotIn("provider5/model_no_pricing", formatted_list) # No pricing

        # Check summary lines
        self.assertIn("Total models: 5", formatted_list) # All models in dummy data
        self.assertIn("Excluded due to poor tool usage: 2", formatted_list) # medium (excluded) + no_tools
        self.assertIn("Usable models: 2", formatted_list) # cheap + expensive

    def test_get_cheapest_model(self):
        provider = LLMInfoProvider()
        cheapest_model = provider.get_cheapest_model()
        # Should return the cheapest model that is not excluded and has pricing
        self.assertEqual(cheapest_model, 'provider1/model_cheap')

    def test_get_model_info(self):
        provider = LLMInfoProvider()
        info = provider.get_model_info('provider1/model_cheap')
        self.assertIsNotNone(info)
        self.assertEqual(info['id'], 'provider1/model_cheap')

        info_excluded = provider.get_model_info('provider2/model_medium')
        # get_model_info should return info even if the model is excluded
        self.assertIsNotNone(info_excluded)
        self.assertEqual(info_excluded['id'], 'provider2/model_medium')

        info_non_existent = provider.get_model_info('non_existent_model')
        self.assertIsNone(info_non_existent)

    def test_get_model_info_with_mapping(self):
        provider = LLMInfoProvider()
        info = provider.get_model_info('alias_for_cheap')
        self.assertIsNotNone(info)
        self.assertEqual(info['id'], 'provider1/model_cheap') # Should resolve the alias

    def test_get_cost_info(self):
        provider = LLMInfoProvider()
        usage = Usage(request_tokens=100, response_tokens=200)
        cost = provider.get_cost_info('provider1/model_cheap', usage)
        # Cost = (100 * 0.0000001) + (200 * 0.0000002) = 0.00001 + 0.00004 = 0.00005
        self.assertAlmostEqual(cost, 0.00005, places=10)

        cost_expensive = provider.get_cost_info('provider3/model_expensive', usage)
        # Cost = (100 * 0.0000006) + (200 * 0.0000008) = 0.00006 + 0.00016 = 0.00022
        self.assertAlmostEqual(cost_expensive, 0.00022, places=10)

        cost_no_pricing = provider.get_cost_info('provider5/model_no_pricing', usage)
        self.assertEqual(cost_no_pricing, 0.0)

        cost_non_existent = provider.get_cost_info('non_existent_model', usage)
        self.assertEqual(cost_non_existent, 0.0)


if __name__ == '__main__':
    unittest.main()
