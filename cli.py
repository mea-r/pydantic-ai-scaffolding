"""
Testing suite for the AIHelper class.
"""
import argparse
from pydantic.v1.typing import get_args

from ai_helper import AiHelper
from helpers.cli_helper_functions import flag_non_working_models
from helpers.config_helper import ConfigHelper
from helpers.llm_info_provider import LLMInfoProvider
from helpers.usage_tracker import UsageTracker, format_usage_data
from tests.helpers import test_hello_world, test_weather

# check command line flags
parser = argparse.ArgumentParser()
parser.add_argument('--update_non_working', nargs='*', help='Updates non-working models in the config file')
parser.add_argument('--simple_test', nargs='*', help='Run a simple test case without tool calling')
parser.add_argument('--test_tools', nargs='*', help='Run a test case with tool calling')
parser.add_argument('--prices', nargs='*', help='Outputs price information for LLM models')
parser.add_argument('--prices_save', nargs='*', help='Saves price information for LLM models')
parser.add_argument('--custom', nargs='*', help='Run your custom code')
parser.add_argument('--usage', nargs='*', help='Print the usage report')
parser.add_argument('--usage_save', nargs='*', help='Save the sousage report')
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

if args.usage is not None:
    usage_tracker = UsageTracker()
    summary = usage_tracker.get_usage_summary()
    print(format_usage_data(summary))

if args.usage_save is not None:
    usage_tracker = UsageTracker()
    summary = usage_tracker.get_usage_summary()
    # Save the usage data to a file
    file = 'usage_report.txt'
    with open(file, 'w') as f:
        f.write(format_usage_data(summary))

if args.prices is not None:
    # if the flag is set, we will update the prices for the models
    print("Updating prices for the models...")
    info_provider = LLMInfoProvider()
    print(info_provider.format_price_list())

if args.prices_save is not None:
    # if the flag is set, we will update the prices for the models
    print("Updating prices for the models...")
    info_provider = LLMInfoProvider()
    file = 'llm_prices.txt'
    with open(file, 'w') as f:
        f.write(info_provider.format_price_list())

if args.custom is not None:
    pass
