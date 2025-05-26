from helpers.config_helper import ConfigHelper
from helpers.llm_info_provider import LLMInfoProvider
from py_models.weather.model import WeatherModel
from py_models.file_analysis.model import FileAnalysisModel
from helpers.test_helpers_utils import test_weather, test_file_analysis

"""
This script will run through all models and test the tool calling, marking non-working ones to config.
"""
def flag_non_working_models(report_file_path: str = 'logs/tool_call_errors.txt'):
    info_provider = LLMInfoProvider()
    config_helper = ConfigHelper()

    models = info_provider.get_models()
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
            with open(report_file_path, 'a') as f:
                f.write(f"Model: {model} Error: {e}\n")
            continue

        try:
            if not isinstance(result, WeatherModel):
                print(f"Model {model} did not return a valid WeatherModel instance.")
                config_helper.append_config_list('excluded_models', model)
                with open(report_file_path, 'w') as f:
                    f.write(f"Model: {model} did not return a valid WeatherModel instance\n")
                continue

            if 'Sofia' not in result.haiku or 'Sofia' not in result.report:
                print(f"Model {model} did not return expected location in haiku or result: {result.haiku}")
                config_helper.append_config_list('excluded_models', model)
                with open(report_file_path, 'w') as f:
                    f.write(f"Incomplete response from {model}\n")
        except Exception as e:
            print(f"Error processing model {model}: {e}")
            config_helper.append_config_list('excluded_models', model)
            with open(report_file_path, 'w') as f:
                f.write(f"Model: {model} Error: {e}\n")
            continue


def flag_file_capable_models(report_file_path: str = 'logs/file_capability_results.txt'):
    info_provider = LLMInfoProvider()
    config_helper = ConfigHelper()

    models = info_provider.get_models()

    for model in models:
        try:
            result, report = test_file_analysis(model_name=model, provider='open_router')
            print(f"Testing model: {model}")
            print(result.model_dump_json(indent=4))
            print(report.model_dump_json(indent=4))
        except Exception as e:
            print(f"Error with model {model}: {e}")
            with open(report_file_path, 'a') as f:
                f.write(f"Model: {model} Error: {e}\n")
            continue

        try:
            if not isinstance(result, FileAnalysisModel):
                print(f"Model {model} did not return a valid FileAnalysisModel instance.")
                with open(report_file_path, 'a') as f:
                    f.write(f"Model: {model} did not return a valid FileAnalysisModel instance\n")
                continue

            if result.key == 'dog' and result.value == 'Roger':
                print(f"Model {model} successfully extracted key='dog' and value='Roger' - adding to file_capable_models")
                config_helper.append_config_list('file_capable_models', model)
                with open(report_file_path, 'a') as f:
                    f.write(f"SUCCESS: Model {model} extracted key='{result.key}' value='{result.value}'\n")
            else:
                print(f"Model {model} did not extract correct key/value: key='{result.key}' value='{result.value}'")
                with open(report_file_path, 'a') as f:
                    f.write(f"FAILED: Model {model} extracted key='{result.key}' value='{result.value}'\n")
        except Exception as e:
            print(f"Error processing model {model}: {e}")
            with open(report_file_path, 'a') as f:
                f.write(f"Model: {model} Error: {e}\n")
            continue
