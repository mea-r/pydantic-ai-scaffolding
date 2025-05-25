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
parser.add_argument('--simple_test', nargs='*', help='Run a simple test case without tool calling')
parser.add_argument('--test_tools', nargs='*', help='Run a test case with tool calling')
parser.add_argument('--prices', nargs='*', help='Updates non-working models in the config file')
parser.add_argument('--custom', nargs='*', help='Run your custom code')
args = parser.parse_args()

if args.update_non_working is not None:
    # if the flag is set, we will update the non-working models in the config file
    print("Updating non-working models in the config file...")
    flag_non_working_models()

if args.simple_test is not None:
    ## test case with tool calling
    result, report = test_hello_world()
    print(result.model_dump_json(indent=4))
    print(report.model_dump_json(indent=4))

if args.test_tools is not None:
    result, report = test_weather()
    print(result.model_dump_json(indent=4))
    print(report.model_dump_json(indent=4))

if args.prices is not None:
    # if the flag is set, we will update the prices for the models
    print("Updating prices for the models...")
    info_provider = LLMInfoProvider()
    info_provider.print_price_list()

if args.custom is not None:
    pass
