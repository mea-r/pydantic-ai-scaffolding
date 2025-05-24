"""
Testing suite for the AIHelper class.
"""
from ai_helper import AiHelper

base = AiHelper()
base.info_provider.print_price_list()
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
