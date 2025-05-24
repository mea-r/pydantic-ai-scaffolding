"""
Testing suite for the AIHelper class.
"""
import argparse
from pydantic.v1.typing import get_args

from ai_helper import AiHelper
from helpers.cli_helper_functions import flag_non_working_models
from helpers.config_helper import ConfigHelper
from helpers.llm_info_provider import LLMInfoProvider
from tests.helpers import test_hello_world, test_weather

# check command line flags
parser = argparse.ArgumentParser()
parser.add_argument('--update_non_working', nargs='*', help='Updates non-working models in the config file')
parser.add_argument('--simple_test', nargs='*', help='Updates non-working models in the config file')
args = parser.parse_args()

if args.update_non_working is not None:
    # if the flag is set, we will update the non-working models in the config file
    print("Updating non-working models in the config file...")
    flag_non_working_models()

if args.simple_test is not None:
    ## test case with tool calling
    result, report = test_weather()
    print(result.model_dump_json(indent=4))
    print(report.model_dump_json(indent=4))


### most simple test case - fails
# try:
#     result, report = test_hello_world(model_name='deepseek/deepseek-prover-v2:free', provider='open_router')
#     print(result.model_dump_json(indent=4))
#     print(report.model_dump_json(indent=4))
# except Exception as e:
#     # Expected to fail with a 404 error since the model is not available
#     print(f"Error: {e}")
#
# ### most simple test case - runs
# result, report = test_hello_world(model_name='google/gemini-2.0-flash-lite-001', provider='google')
# print(result.model_dump_json(indent=4))
# print(report.model_dump_json(indent=4))


### test case with tool calling
# result, report = test_weather()
# print(result.model_dump_json(indent=4))
# print(report.model_dump_json(indent=4))



# write errors to file




# weather = get_weather('Sofia, Bulgaria')
# print(weather)



#base = AiHelper()
#base.info_provider.print_price_list()
#result, report = base.test()
#
# print(result.model_dump_json(indent=4))
# print(report.model_dump_json(indent=4))

# models_to_test = [
#     ["google", "google/gemini-2.0-flash-lite-001"],  # provider first, model second
#     ["open_router", "deepseek/deepseek-prover-v2:free"],
#     ["open_router", "anthropic/claude-3-haiku"],
#     ["anthropic", "anthropic/claude-3-haiku-20240307"],
#     ["openai", "openai/gpt-4"],
#
#     # these two are supposed to throw an error
#     ["openai", "error"],
#     ["openai", "openai/errormodel"],
# ]
#
# for provider,model in models_to_test:
#
#     print(f"Testing model: {model} with provider: {provider}")
#
#     try:
#         base = AiHelper()
#         result, report = base.test(model_name=model, provider=provider)
#     except Exception as e:
#         print(f"Error with model {model} and provider {provider}: {e}")
#         continue
#
#     print(result.model_dump_json(indent=4))
#     print(report.model_dump_json(indent=4))
#
#
#


# cost_tracker = LLMInfoProvider()
# result = cost_tracker.get_cost_info('google/gemini-2.5-flash-preview-05-20', 1000, 2000)
# print(result)


# from py_models.general_example_model import GeneralExampleModel
# from py_models.weather_model import WeatherModel
#
# ai_helper = AIHelper('openrouter:openai/gpt-3.5-turbo')
# ai_helper.add_tool("calculator", "A simple calculator that can add, subtract, multiply, and divide.")
# ai_helper.add_tool("weather", "A tool to get the current weather information.")
# result = ai_helper.ask("What is the weather like today?", tools=["weather"], model=WeatherModel)
#
# # result should be a WeatherModel object
# print(result)
#
#
# """
# All these three variations should give the same result. Add a test that checks for that also.
# """
#
# models_to_test = [
#     'google:gemini-2.5-flash-preview-05-20',
#     'openrouter:google/gemini-2.5-flash-preview-05-20',
#     'anthropic:claude-3',
#     'openrouter:anthropic/claude-3',
#     'openai:gpt-4',
#     'openrouter:openai/gpt-4',
#     ]
#
# for model in models_to_test:
#     ai_helper = AIHelper(model)
#     result = ai_helper.ask("Please read this PDF and summarize it.", model=GeneralExampleModel, file="files/example.pdf")
#     # result should be a GeneralExampleModel object
#     print(result)
#
#     # anthropic models don't support file reading
#     if 'anthropic' not in model:
#         ai_helper = AIHelper(model)
#         result = ai_helper.ask("Please read this PDF and summarize it.", model=GeneralExampleModel, file="files/example.png")
#         # result should be a GeneralExampleModel object
#         print(result)
#
#     ai_helper = AIHelper(model)
#     result = ai_helper.ask("This is the test file we use. Key is 'dog' and value for that is 'Roger'", model=GeneralExampleModel)
#     # result should be a GeneralExampleModel object
#     print(result)
#
