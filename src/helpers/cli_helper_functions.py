from helpers.config_helper import ConfigHelper
from helpers.llm_info_provider import LLMInfoProvider
from py_models.weather.model import WeatherModel
from tests.helpers import test_weather

"""
This script will run through all models and test the tool calling, marking non-working ones to config.
"""
def flag_non_working_models():
    info_provider = LLMInfoProvider()
    config_helper = ConfigHelper()

    models = info_provider.get_models()
    report_file = 'tool_call_errors.txt'
    started = False

    for model in models:

        if model == 'openai/o4-mini-high':
            started = True

        if not started:
            continue

        try:
            result, report = test_weather(model_name=model, provider='open_router')
            print(result.model_dump_json(indent=4))
            print(report.model_dump_json(indent=4))
        except Exception as e:
            print(f"Error with model {model}: {e}")
            config_helper.append_config_list('excluded_models', model)
            with open(report_file, 'a') as f:
                f.write(f"Model: {model} Error: {e}\n")
            continue

        try:
            if not isinstance(result, WeatherModel):
                print(f"Model {model} did not return a valid WeatherModel instance.")
                config_helper.append_config_list('excluded_models', model)
                with open(report_file, 'w') as f:
                    f.write(f"Model: {model} did not return a valid WeatherModel instance\n")
                continue

            if 'Sofia' not in result.haiku or 'Sofia' not in result.report:
                print(f"Model {model} did not return expected location in haiku or result: {result.haiku}")
                config_helper.append_config_list('excluded_models', model)
                with open(report_file, 'w') as f:
                    f.write(f"Incomplete response from {model}\n")
        except Exception as e:
            print(f"Error processing model {model}: {e}")
            config_helper.append_config_list('excluded_models', model)
            with open(report_file, 'w') as f:
                f.write(f"Model: {model} Error: {e}\n")
            continue
