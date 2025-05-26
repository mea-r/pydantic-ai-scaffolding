import unittest
import os
import json
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

# Assuming the LLMInfoProvider class is in src/helpers/llm_info_provider.py
from src.helpers.llm_info_provider import LLMInfoProvider
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

        # Patch the cache file path to use our test file
        self.cache_file_patcher = patch('src.helpers.llm_info_provider.LLMInfoProvider._init_cost_info')
        self.mock_init_cost_info = self.cache_file_patcher.start()
        
        # Patch ConfigHelper to use our test config
        self.config_patcher = patch('src.helpers.llm_info_provider.ConfigHelper')
        self.mock_config_class = self.config_patcher.start()
        self.mock_config = MagicMock()
        self.mock_config.get_config.return_value = DUMMY_CONFIG_CONTENT["excluded_models"]
        self.mock_config_class.return_value = self.mock_config

        # Patch requests.get to prevent actual API calls
        self.requests_patcher = patch('src.helpers.llm_info_provider.requests.get')
        self.mock_requests_get = self.requests_patcher.start()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = DUMMY_MODELS_DATA
        self.mock_requests_get.return_value = mock_response

        # Patch os.path.exists and open to use our test files
        self.exists_patcher = patch('src.helpers.llm_info_provider.os.path.exists')
        self.mock_exists = self.exists_patcher.start()
        self.mock_exists.return_value = True

        self.open_patcher = patch('src.helpers.llm_info_provider.open')
        self.mock_open = self.open_patcher.start()
        
        def mock_open_func(path, mode='r'):
            if 'models.json' in path:
                return open(str(TEST_MODELS_JSON_PATH), mode)
            elif 'model_mappings.json' in path:
                return open(str(TEST_MODEL_MAPPINGS_JSON_PATH), mode)
            else:
                return open(path, mode)
        
        self.mock_open.side_effect = mock_open_func

        # Patch os.path.dirname
        self.dirname_patcher = patch('src.helpers.llm_info_provider.os.path.dirname')
        self.mock_dirname = self.dirname_patcher.start()
        self.mock_dirname.return_value = str(TEST_MODEL_MAPPINGS_JSON_PATH.parent)

    def tearDown(self):
        # Clean up dummy files after each test
        if os.path.exists(TEST_MODELS_JSON_PATH):
             os.remove(TEST_MODELS_JSON_PATH)
        if os.path.exists(TEST_MODEL_MAPPINGS_JSON_PATH):
             os.remove(TEST_MODEL_MAPPINGS_JSON_PATH)
        if os.path.exists(TEST_CONFIG_PATH):
             os.remove(TEST_CONFIG_PATH)

        # Stop all patches
        self.cache_file_patcher.stop()
        self.config_patcher.stop()
        self.requests_patcher.stop()
        self.exists_patcher.stop()
        self.open_patcher.stop()
        self.dirname_patcher.stop()

    def test_init_cost_info_loads_from_cache(self):
        provider = LLMInfoProvider()
        # Manually set the cost info to simulate loaded cache
        provider._cost_info = {
            "pydantic_model_cost": {},
            "llm_model_cost": {},
            "total_cost": {"total": 0},
            "model_data": DUMMY_MODELS_DATA['data']
        }
        
        # Should not call requests.get if cache is valid
        self.mock_requests_get.assert_not_called()
        self.assertEqual(len(provider._cost_info['model_data']), len(DUMMY_MODELS_DATA['data']))

    def test_init_cost_info_fetches_if_no_cache(self):
        self.mock_exists.return_value = False
        
        provider = LLMInfoProvider()
        # Manually set the cost info to simulate API fetch
        provider._cost_info = {
            "pydantic_model_cost": {},
            "llm_model_cost": {},
            "total_cost": {"total": 0},
            "model_data": [m for m in DUMMY_MODELS_DATA['data'] if 'tools' in m.get('supported_parameters', [])]
        }
        
        self.assertEqual(len(provider._cost_info['model_data']), 4) # Only models with tools

    def test_get_models(self):
        provider = LLMInfoProvider()
        # Manually set the cost info
        provider._cost_info = {
            "pydantic_model_cost": {},
            "llm_model_cost": {},
            "total_cost": {"total": 0},
            "model_data": DUMMY_MODELS_DATA['data']
        }
        
        models = provider.get_models()
        # Should exclude the model in excluded_models and models without tools
        expected_models = [
            'provider1/model_cheap',
            'provider3/model_expensive',
            'provider4/model_no_tools',
            'provider5/model_no_pricing'
        ]
        self.assertCountEqual(models, expected_models)

    def test_get_price_list(self):
        provider = LLMInfoProvider()
        # Manually set the cost info
        provider._cost_info = {
            "pydantic_model_cost": {},
            "llm_model_cost": {},
            "total_cost": {"total": 0},
            "model_data": DUMMY_MODELS_DATA['data']
        }
        
        price_list = provider.get_price_list()

        # Check if excluded models are not in the price list
        self.assertNotIn('provider2/model_medium', price_list)

        # Check sorting (cheapest to most expensive by completion price)
        model_ids = list(price_list.keys())
        self.assertEqual(model_ids[0], 'provider1/model_cheap')
        self.assertEqual(model_ids[1], 'provider4/model_no_tools')
        self.assertEqual(model_ids[2], 'provider3/model_expensive')

        # Check pricing values (multiplied by 1,000,000 and rounded)
        self.assertEqual(price_list['provider1/model_cheap']['prompt'], 0.1)
        self.assertEqual(price_list['provider1/model_cheap']['completion'], 0.2)
        self.assertEqual(price_list['provider3/model_expensive']['prompt'], 0.6)
        self.assertEqual(price_list['provider3/model_expensive']['completion'], 0.8)

    def test_format_price_list(self):
        provider = LLMInfoProvider()
        # Manually set the cost info
        provider._cost_info = {
            "pydantic_model_cost": {},
            "llm_model_cost": {},
            "total_cost": {"total": 0},
            "model_data": DUMMY_MODELS_DATA['data']
        }
        
        formatted_list = provider.format_price_list()

        self.assertIsInstance(formatted_list, str)
        self.assertIn("Model ID", formatted_list)
        self.assertIn("Price Category", formatted_list)
        self.assertIn("provider1/model_cheap", formatted_list)
        self.assertIn("provider3/model_expensive", formatted_list)
        self.assertNotIn("provider2/model_medium", formatted_list) # Excluded

        # Check summary lines
        self.assertIn("Total models: 5", formatted_list) # All models in dummy data

    def test_get_cheapest_model(self):
        provider = LLMInfoProvider()
        # Manually set the cost info
        provider._cost_info = {
            "pydantic_model_cost": {},
            "llm_model_cost": {},
            "total_cost": {"total": 0},
            "model_data": DUMMY_MODELS_DATA['data']
        }
        
        cheapest_model = provider.get_cheapest_model()
        # Should return the cheapest model that is not excluded and has pricing
        self.assertEqual(cheapest_model, 'provider1/model_cheap')


    def test_get_model_info_with_mapping(self):
        provider = LLMInfoProvider()
        # Manually set the cost info
        provider._cost_info = {
            "pydantic_model_cost": {},
            "llm_model_cost": {},
            "total_cost": {"total": 0},
            "model_data": DUMMY_MODELS_DATA['data']
        }
        
        info = provider.get_model_info('alias_for_cheap')
        self.assertIsNotNone(info)
        self.assertEqual(info['id'], 'provider1/model_cheap') # Should resolve the alias

    def test_get_cost_info(self):
        provider = LLMInfoProvider()
        # Manually set the cost info
        provider._cost_info = {
            "pydantic_model_cost": {},
            "llm_model_cost": {},
            "total_cost": {"total": 0},
            "model_data": DUMMY_MODELS_DATA['data']
        }
        
        usage = Usage(request_tokens=100, response_tokens=200)
        cost = provider.get_cost_info('provider1/model_cheap', usage)
        # Cost = (100 * 0.0000001) + (200 * 0.0000002) = 0.00001 + 0.00004 = 0.00005
        self.assertAlmostEqual(cost, 0.00005, places=10)

        cost_expensive = provider.get_cost_info('provider3/model_expensive', usage)
        # Cost = (100 * 0.0000006) + (200 * 0.0000008) = 0.00006 + 0.00016 = 0.00022
        self.assertAlmostEqual(cost_expensive, 0.00022, places=10)

        cost_non_existent = provider.get_cost_info('non_existent_model', usage)
        self.assertEqual(cost_non_existent, 0.0)


if __name__ == '__main__':
    unittest.main()
