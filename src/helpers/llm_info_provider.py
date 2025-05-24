import json
import os
import time
import requests
from pydantic_ai.usage import Usage


class LLMInfoProvider:
    def __init__(self):
        self._total_cost = 0
        self._cost_info = {}
        self._init_cost_info()

    """
    FORMAT:
    
    {
      "id": "google/gemini-2.5-flash-preview-05-20:thinking",
      "hugging_face_id": "",
      "name": "Google: Gemini 2.5 Flash Preview 05-20 (thinking)",
      "created": 1747761924,
      "description": "Gemini 2.5 Flash May 20th Checkpoint is Google's state-of-the-art workhorse model, specifically designed for advanced reasoning, coding, mathematics, and scientific tasks. It includes built-in \"thinking\" capabilities, enabling it to provide responses with greater accuracy and nuanced context handling. \n\nNote: This model is available in two variants: thinking and non-thinking. The output pricing varies significantly depending on whether the thinking capability is active. If you select the standard variant (without the \":thinking\" suffix), the model will explicitly avoid generating thinking tokens. \n\nTo utilize the thinking capability and receive thinking tokens, you must choose the \":thinking\" variant, which will then incur the higher thinking-output pricing. \n\nAdditionally, Gemini 2.5 Flash is configurable through the \"max tokens for reasoning\" parameter, as described in the documentation (https://openrouter.ai/docs/use-cases/reasoning-tokens#max-tokens-for-reasoning).",
      "context_length": 1048576,
      "architecture": {
        "modality": "text+image->text",
        "input_modalities": [
          "image",
          "text",
          "file"
        ],
        "output_modalities": [
          "text"
        ],
        "tokenizer": "Gemini",
        "instruct_type": null
      },
      "pricing": {
        "prompt": "0.00000015",
        "completion": "0.0000035",
        "request": "0",
        "image": "0.0006192",
        "web_search": "0",
        "internal_reasoning": "0",
        "input_cache_read": "0.0000000375",
        "input_cache_write": "0.0000002333"
      },
      "top_provider": {
        "context_length": 1048576,
        "max_completion_tokens": 65535,
        "is_moderated": false
      },
      "per_request_limits": null,
      "supported_parameters": [
        "tools",
        "tool_choice",
        "max_tokens",
        "temperature",
        "top_p",
        "reasoning",
        "include_reasoning",
        "structured_outputs",
        "response_format",
        "stop",
        "frequency_penalty",
        "presence_penalty",
        "seed"
      ]
    },
    
    """

    def _get_models_data(self) -> list:
        cache_file = "models.json"
        if not os.path.exists(cache_file):
            self._init_cost_info()

        with open(cache_file, 'r') as f:
            data = json.load(f)

        return data['data']

    def get_models(self) -> list:
        """
        Returns a list of all available models.
        """
        models = self._get_models_data()
        return [model['id'] for model in models]

    def get_price_list(self) -> dict:
        models = self._get_models_data()
        price_list = {}

        for model in models:
            pricing = model.get("pricing", {})
            model_id = model.get("id", "")
            comparison_price = float(pricing.get("completion", 0))*1000000

            if comparison_price < 1:
                price_category = "cheap"
            elif comparison_price < 4:
                price_category = "medium"
            else:
                price_category = "expensive"

            price_list[model_id] = {
                "price_category": price_category,
                "prompt": round(float(pricing.get("prompt", 0))*1000000,2),
                "completion": round(float(pricing.get("completion", 0))*1000000,2),
                "request": round(float(pricing.get("request", 0))*1000000,2),
                "image": round(float(pricing.get("image", 0))*1000000,2),
                "web_search": round(float(pricing.get("web_search", 0))*1000000,2),
                "internal_reasoning": round(float(pricing.get("internal_reasoning", 0))*1000000,2),
                "input_cache_read": round(float(pricing.get("input_cache_read", 0)),2),
                "input_cache_write": round(float(pricing.get("input_cache_write", 0)),2)
            }


        # sort from cheapest to most expensive
        price_list = dict(sorted(price_list.items(), key=lambda item: item[1]['completion']))
        return price_list

    def print_price_list(self):
        # print a table
        price_list = self.get_price_list()
        # titles
        print(f"{'Model ID':<60} {'Price':<15} {'Prompt $M/t':<20} {'Completion $M/t':<20} {'Request $M/t':<20} {'Image $M/t':<20} {'Web Search $M/t':<20} {'Internal Reasoning $M/t':<20} {'Input Cache Read':<20} {'Input Cache Write':<20}")

        for model_id, prices in price_list.items():
            # determine color based on price category
            if prices['price_category'] == 'cheap':
                color = "\033[92m"
            elif prices['price_category'] == 'medium':
                color = "\033[93m"
            else:
                color = "\033[91m"
            # print the model id and prices
            print(f"{color}{model_id:<60}\033[0m {prices['price_category']:<15} {prices['prompt']:<20} {prices['completion']:<20} {prices['request']:<20} {prices['image']:<20} {prices['web_search']:<20} {prices['internal_reasoning']:<20} {prices['input_cache_read']:<20} {prices['input_cache_write']:<20}")


    def get_cheapest_model(self) -> str:
        start = 10
        models = self._get_models_data()
        cheapest_model = None

        for model in models:
            pricing = model.get("pricing", {})

            if 'completion' in pricing and float(pricing['completion']) > 0:
                cost = float(pricing['completion'])
                if cost < start:
                    start = cost
                    cheapest_model = model['id']

        return cheapest_model

    def get_model_info(self, model: str) -> dict | None:
        models = self._get_models_data()

        # read the model_mappings.json
        path = os.path.dirname(__file__)
        model_mappings_file = path+"/model_mappings.json"


        if os.path.exists(model_mappings_file):
            with open(model_mappings_file, 'r') as f:
                model_mappings = json.load(f)
            # check if model is in mappings
            if model in model_mappings:
                model = model_mappings[model]

        result = list(filter(lambda x: x["id"] == model, models))

        if not result:
            return None

        return result[0]

    def get_cost_info(self, model: str, usage: Usage) -> int:
        model_info = self.get_model_info(model)
        if not model_info:
            return 0

        pricing = model_info.get("pricing", {})
        total_cost = 0

        if 'prompt' in pricing and usage.request_tokens > 0:
            total_cost += float(pricing['prompt']) * usage.request_tokens

        if 'completion' in pricing and usage.response_tokens > 0:
            total_cost += float(pricing['completion']) * usage.response_tokens

        return round(total_cost, 10)


    """
    1) pull cost information from https://openrouter.ai/api/v1/models (no auth required)
    2) save and cache for 1 day. models.json
    """
    def _init_cost_info(self):

        cache_file = "models.json"
        cache_duration = 86400  # 1 day in seconds

        # Check if cached data exists and is recent
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                cache_time = cache_data.get("timestamp", 0)
                if time.time() - cache_time < cache_duration:
                    self._cost_info = {
                        "pydantic_model_cost": {},
                        "llm_model_cost": {},
                        "total_cost": {"total": 0},
                        "model_data": cache_data.get("data", [])
                    }
                    return

        # Fetch data from OpenRouter API if no valid cache
        try:
            response = requests.get("https://openrouter.ai/api/v1/models")
            response.raise_for_status()
            model_data = response.json().get("data", [])

            # remove models that do not support tools
            model_data = [model for model in model_data if 'tools' in model.get('supported_parameters', [])]

            # Save to cache with timestamp
            cache_data = {
                "timestamp": time.time(),
                "data": model_data
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            self._cost_info = {
                "pydantic_model_cost": {},
                "llm_model_cost": {},
                "total_cost": {"total": 0},
                "model_data": model_data
            }
        except Exception as e:
            # Fallback to empty data if API fetch fails
            self._cost_info = {
                "pydantic_model_cost": {},
                "llm_model_cost": {},
                "total_cost": {"total": 0},
                "model_data": []
            }
            print(f"Failed to fetch cost data from OpenRouter API: {str(e)}")
