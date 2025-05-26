import unittest
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Assuming the UsageTracker and related classes are in src/helpers/usage_tracker.py
from src.helpers.usage_tracker import UsageTracker, HelperUsage, UsageItem, ToolUsageItem, FillPercentageStats, format_usage_data, print_usage_report, format_usage_from_file
from src.py_models.base import LLMReport
from pydantic_ai.usage import Usage
from pydantic import BaseModel # Needed for LLMReport

# Define a dummy usage file path for testing
TEST_USAGE_FILE_PATH = Path(__file__).parent / 'logs/test_usage.json'

# Initial content for the dummy usage file (empty structure)
INITIAL_USAGE_CONTENT = {
    "usage_today": 0.0,
    "usage_this_month": 0.0,
    "daily_usage": [],
    "daily_tool_usage": [],
    "fill_percentage_by_pydantic_model": {},
    "fill_percentage_by_llm_model": {}
}

class TestUsageTracker(unittest.TestCase):

    def setUp(self):
        # Create a dummy usage file before each test
        os.makedirs(TEST_USAGE_FILE_PATH.parent, exist_ok=True)
        with open(TEST_USAGE_FILE_PATH, 'w') as f:
            json.dump(INITIAL_USAGE_CONTENT, f, indent=4)

        # Patch the os.path.join to use the dummy file path
        # This is necessary to prevent it from trying to load/save the actual usage.json
        patcher_os_path_join = patch('src.helpers.usage_tracker.os.path.join', return_value=str(TEST_USAGE_FILE_PATH))
        self.mock_os_path_join = patcher_os_path_join.start()

        # Patch datetime.now to control the current date/time for testing
        patcher_datetime_now = patch('src.helpers.usage_tracker.datetime')
        self.mock_datetime = patcher_datetime_now.start()
        self.mock_datetime.now.return_value = datetime(2023, 10, 26, 12, 0, 0) # Set a fixed date/time
        self.mock_datetime.strftime = datetime.strftime # Allow strftime to work on the mock
        self.mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw) # Allow datetime() calls


    def tearDown(self):
        # Clean up the dummy usage file after each test
        if os.path.exists(TEST_USAGE_FILE_PATH):
            os.remove(TEST_USAGE_FILE_PATH)

        # Stop all patches
        patch.stopall()

    def test_init_loads_existing_file(self):
        tracker = UsageTracker()
        self.assertIsInstance(tracker.usage_data, HelperUsage)
        self.assertEqual(tracker.usage_data.usage_today, 0.0)
        self.assertEqual(tracker.usage_data.daily_usage, [])

    def test_init_creates_empty_file_if_not_exists(self):
        # Remove the dummy file to simulate file not found
        if os.path.exists(TEST_USAGE_FILE_PATH):
            os.remove(TEST_USAGE_FILE_PATH)

        tracker = UsageTracker()
        self.assertIsInstance(tracker.usage_data, HelperUsage)
        self.assertTrue(os.path.exists(TEST_USAGE_FILE_PATH))
        with open(TEST_USAGE_FILE_PATH, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['usage_today'], 0.0)
            self.assertEqual(data['daily_usage'], [])

    def test_add_usage_llm(self):
        tracker = UsageTracker()
        report = LLMReport(
            model_name='test_model',
            usage=Usage(request_tokens=10, response_tokens=20, total_tokens=30, requests=1),
            cost=0.0001,
            fill_percentage=80
        )
        tracker.add_usage(report, model_name='test_model', service='test_service', pydantic_model_name='TestModel')

        # Verify in memory
        self.assertEqual(len(tracker.usage_data.daily_usage), 1)
        item = tracker.usage_data.daily_usage[0]
        self.assertEqual(item.day, '2023-10-26')
        self.assertEqual(item.model, 'test_model')
        self.assertEqual(item.service, 'test_service')
        self.assertEqual(item.pydantic_model_name, 'TestModel')
        self.assertEqual(item.input_tokens, 10)
        self.assertEqual(item.output_tokens, 20)
        self.assertEqual(item.total_tokens, 30)
        self.assertEqual(item.requests, 1)
        self.assertAlmostEqual(item.cost, 0.0001)
        self.assertAlmostEqual(tracker.usage_data.usage_today, 0.0001)
        self.assertAlmostEqual(tracker.usage_data.usage_this_month, 0.0001)

        # Verify fill percentage stats
        self.assertIn('TestModel', tracker.usage_data.fill_percentage_by_pydantic_model)
        self.assertEqual(tracker.usage_data.fill_percentage_by_pydantic_model['TestModel'].average, 80.0)
        self.assertEqual(tracker.usage_data.fill_percentage_by_pydantic_model['TestModel'].count, 1)
        self.assertIn('test_model', tracker.usage_data.fill_percentage_by_llm_model)
        self.assertEqual(tracker.usage_data.fill_percentage_by_llm_model['test_model'].average, 80.0)
        self.assertEqual(tracker.usage_data.fill_percentage_by_llm_model['test_model'].count, 1)


        # Verify in file
        with open(TEST_USAGE_FILE_PATH, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data['daily_usage']), 1)
            file_item = data['daily_usage'][0]
            self.assertEqual(file_item['day'], '2023-10-26')
            self.assertEqual(file_item['model'], 'test_model')
            self.assertEqual(file_item['pydantic_model_name'], 'TestModel')
            self.assertAlmostEqual(data['usage_today'], 0.0001)
            self.assertAlmostEqual(data['usage_this_month'], 0.0001)
            self.assertIn('TestModel', data['fill_percentage_by_pydantic_model'])
            self.assertAlmostEqual(data['fill_percentage_by_pydantic_model']['TestModel']['average'], 80.0)
            self.assertIn('test_model', data['fill_percentage_by_llm_model'])
            self.assertAlmostEqual(data['fill_percentage_by_llm_model']['test_model']['average'], 80.0)


    def test_add_usage_llm_aggregate_same_day(self):
        tracker = UsageTracker()
        report1 = LLMReport(
            model_name='test_model',
            usage=Usage(request_tokens=10, response_tokens=20, total_tokens=30, requests=1),
            cost=0.0001,
            fill_percentage=80
        )
        report2 = LLMReport(
            model_name='test_model',
            usage=Usage(request_tokens=15, response_tokens=25, total_tokens=40, requests=1),
            cost=0.00015,
            fill_percentage=90
        )
        tracker.add_usage(report1, model_name='test_model', service='test_service', pydantic_model_name='TestModel')
        tracker.add_usage(report2, model_name='test_model', service='test_service', pydantic_model_name='TestModel')

        # Verify in memory
        self.assertEqual(len(tracker.usage_data.daily_usage), 1) # Should aggregate
        item = tracker.usage_data.daily_usage[0]
        self.assertEqual(item.input_tokens, 25) # 10 + 15
        self.assertEqual(item.output_tokens, 45) # 20 + 25
        self.assertEqual(item.total_tokens, 70) # 30 + 40
        self.assertEqual(item.requests, 2) # 1 + 1
        self.assertAlmostEqual(item.cost, 0.00025) # 0.0001 + 0.00015
        self.assertAlmostEqual(tracker.usage_data.usage_today, 0.00025)
        self.assertAlmostEqual(tracker.usage_data.usage_this_month, 0.00025)

        # Verify fill percentage stats
        self.assertIn('TestModel', tracker.usage_data.fill_percentage_by_pydantic_model)
        # Average should be (80 + 90) / 2 = 85
        self.assertAlmostEqual(tracker.usage_data.fill_percentage_by_pydantic_model['TestModel'].average, 85.0)
        self.assertEqual(tracker.usage_data.fill_percentage_by_pydantic_model['TestModel'].count, 2)
        self.assertIn('test_model', tracker.usage_data.fill_percentage_by_llm_model)
        # Average should be (80 + 90) / 2 = 85
        self.assertAlmostEqual(tracker.usage_data.fill_percentage_by_llm_model['test_model'].average, 85.0)
        self.assertEqual(tracker.usage_data.fill_percentage_by_llm_model['test_model'].count, 2)


    def test_add_usage_tool(self):
        tracker = UsageTracker()
        report = LLMReport(model_name='test_model', usage=Usage(), cost=0.0) # Tool usage doesn't have LLM cost/usage directly
        tracker.add_usage(report, model_name='test_model', service='test_service', tool_names_called=['tool_a'])

        # Verify in memory
        self.assertEqual(len(tracker.usage_data.daily_tool_usage), 1)
        item = tracker.usage_data.daily_tool_usage[0]
        self.assertEqual(item.day, '2023-10-26')
        self.assertEqual(item.tool_name, 'tool_a')
        self.assertEqual(item.calls, 1)

        # Verify in file
        with open(TEST_USAGE_FILE_PATH, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data['daily_tool_usage']), 1)
            file_item = data['daily_tool_usage'][0]
            self.assertEqual(file_item['day'], '2023-10-26')
            self.assertEqual(file_item['tool_name'], 'tool_a')
            self.assertEqual(file_item['calls'], 1)

    def test_add_usage_tool_aggregate_same_day(self):
        tracker = UsageTracker()
        report = LLMReport(model_name='test_model', usage=Usage(), cost=0.0)
        tracker.add_usage(report, model_name='test_model', service='test_service', tool_names_called=['tool_a'])
        tracker.add_usage(report, model_name='test_model', service='test_service', tool_names_called=['tool_a', 'tool_b']) # Call tool_a again and tool_b

        # Verify in memory
        self.assertEqual(len(tracker.usage_data.daily_tool_usage), 2) # Should have two distinct tool entries
        tool_a_item = next(item for item in tracker.usage_data.daily_tool_usage if item.tool_name == 'tool_a')
        tool_b_item = next(item for item in tracker.usage_data.daily_tool_usage if item.tool_name == 'tool_b')

        self.assertEqual(tool_a_item.calls, 2) # Called twice
        self.assertEqual(tool_b_item.calls, 1) # Called once

    def test_calculate_usage_today(self):
        tracker = UsageTracker()
        # Add usage for today
        report_today1 = LLMReport(model_name='model1', usage=Usage(), cost=0.0001)
        report_today2 = LLMReport(model_name='model2', usage=Usage(), cost=0.0002)
        tracker.add_usage(report_today1, model_name='model1', service='s1', pydantic_model_name='P1')
        tracker.add_usage(report_today2, model_name='model2', service='s2', pydantic_model_name='P2')

        # Add usage for a different day
        self.mock_datetime.now.return_value = datetime(2023, 10, 25, 12, 0, 0)
        report_yesterday = LLMReport(model_name='model3', usage=Usage(), cost=0.0003)
        tracker.add_usage(report_yesterday, model_name='model3', service='s3', pydantic_model_name='P3')

        # Reset datetime to today for calculation
        self.mock_datetime.now.return_value = datetime(2023, 10, 26, 12, 0, 0)

        self.assertAlmostEqual(tracker.get_usage_today(), 0.0003) # Sum of today's costs

    def test_calculate_usage_this_month(self):
        tracker = UsageTracker()
        # Add usage for this month (October 2023)
        report_oct1 = LLMReport(model_name='model1', usage=Usage(), cost=0.0001)
        report_oct2 = LLMReport(model_name='model2', usage=Usage(), cost=0.0002)
        tracker.add_usage(report_oct1, model_name='model1', service='s1', pydantic_model_name='P1')
        tracker.add_usage(report_oct2, model_name='model2', service='s2', pydantic_model_name='P2')

        # Add usage for a different month (September 2023)
        self.mock_datetime.now.return_value = datetime(2023, 9, 26, 12, 0, 0)
        report_sep = LLMReport(model_name='model3', usage=Usage(), cost=0.0003)
        tracker.add_usage(report_sep, model_name='model3', service='s3', pydantic_model_name='P3')

        # Reset datetime to this month for calculation
        self.mock_datetime.now.return_value = datetime(2023, 10, 26, 12, 0, 0)

        self.assertAlmostEqual(tracker.get_usage_this_month(), 0.0003) # Sum of this month's costs

    def test_get_usage_summary(self):
        tracker = UsageTracker()
        # Add some usage data
        report1 = LLMReport(model_name='model_a', usage=Usage(request_tokens=10, response_tokens=20, total_tokens=30, requests=1), cost=0.0001, fill_percentage=80)
        report2 = LLMReport(model_name='model_b', usage=Usage(request_tokens=15, response_tokens=25, total_tokens=40, requests=1), cost=0.00015, fill_percentage=90)
        report3 = LLMReport(model_name='model_a', usage=Usage(request_tokens=5, response_tokens=10, total_tokens=15, requests=1), cost=0.00005, fill_percentage=70) # Same model, same day
        tracker.add_usage(report1, model_name='model_a', service='service_x', pydantic_model_name='ModelA')
        tracker.add_usage(report2, model_name='model_b', service='service_y', pydantic_model_name='ModelB')
        tracker.add_usage(report3, model_name='model_a', service='service_x', pydantic_model_name='ModelA')

        # Add tool usage
        report_tool = LLMReport(model_name='model_a', usage=Usage(), cost=0.0)
        tracker.add_usage(report_tool, model_name='model_a', service='service_x', tool_names_called=['tool_calc'])
        tracker.add_usage(report_tool, model_name='model_a', service='service_x', tool_names_called=['tool_date'])
        tracker.add_usage(report_tool, model_name='model_b', service='service_y', tool_names_called=['tool_calc']) # Different model, same tool

        summary = tracker.get_usage_summary()

        self.assertAlmostEqual(summary['usage_today'], 0.0003) # 0.0001 + 0.00015 + 0.00005
        self.assertAlmostEqual(summary['usage_this_month'], 0.0003)

        # Check daily usage
        self.assertEqual(len(summary['daily_usage']), 2) # model_a (aggregated) and model_b
        model_a_daily = next(item for item in summary['daily_usage'] if item['model'] == 'model_a')
        self.assertEqual(model_a_daily['requests'], 2)
        self.assertEqual(model_a_daily['total_tokens'], 45) # 30 + 15
        self.assertAlmostEqual(model_a_daily['cost'], 0.00015) # 0.0001 + 0.00005

        # Check daily tool usage
        self.assertEqual(len(summary['daily_tool_usage']), 2) # tool_calc and tool_date
        tool_calc_daily = next(item for item in summary['daily_tool_usage'] if item['tool_name'] == 'tool_calc')
        self.assertEqual(tool_calc_daily['calls'], 2) # Called twice
        tool_date_daily = next(item for item in summary['daily_tool_usage'] if item['tool_name'] == 'tool_date')
        self.assertEqual(tool_date_daily['calls'], 1) # Called once

        # Check monthly LLM summary
        month_key = '2023-10'
        self.assertIn(month_key, summary['monthly_llm_summary'])
        self.assertEqual(summary['monthly_llm_summary'][month_key]['requests'], 3) # 2 for model_a + 1 for model_b
        self.assertEqual(summary['monthly_llm_summary'][month_key]['total_tokens'], 85) # 45 + 40
        self.assertAlmostEqual(summary['monthly_llm_summary'][month_key]['cost'], 0.0003)

        # Check monthly tool summary
        self.assertIn(month_key, summary['monthly_tool_summary'])
        self.assertEqual(summary['monthly_tool_summary'][month_key]['total_calls'], 3) # 2 for tool_calc + 1 for tool_date

        # Check all-time by model
        self.assertIn('model_a', summary['by_model'])
        self.assertEqual(summary['by_model']['model_a']['requests'], 2)
        self.assertEqual(summary['by_model']['model_a']['total_tokens'], 45)
        self.assertAlmostEqual(summary['by_model']['model_a']['cost'], 0.00015)
        self.assertIn('model_b', summary['by_model'])
        self.assertEqual(summary['by_model']['model_b']['requests'], 1)
        self.assertEqual(summary['by_model']['model_b']['total_tokens'], 40)
        self.assertAlmostEqual(summary['by_model']['model_b']['cost'], 0.00015)

        # Check all-time by service
        self.assertIn('service_x', summary['by_service'])
        self.assertEqual(summary['by_service']['service_x']['requests'], 2)
        self.assertAlmostEqual(summary['by_service']['service_x']['cost'], 0.00015)
        self.assertIn('service_y', summary['by_service'])
        self.assertEqual(summary['by_service']['service_y']['requests'], 1)
        self.assertAlmostEqual(summary['by_service']['service_y']['cost'], 0.00015)

        # Check all-time by pydantic model
        self.assertIn('ModelA', summary['usage_by_pydantic_model'])
        self.assertEqual(summary['usage_by_pydantic_model']['ModelA']['requests'], 2)
        self.assertAlmostEqual(summary['usage_by_pydantic_model']['ModelA']['cost'], 0.00015)
        self.assertIn('ModelB', summary['usage_by_pydantic_model'])
        self.assertEqual(summary['usage_by_pydantic_model']['ModelB']['requests'], 1)
        self.assertAlmostEqual(summary['usage_by_pydantic_model']['ModelB']['cost'], 0.00015)

        # Check all-time by tool
        self.assertIn('tool_calc', summary['by_tool'])
        self.assertEqual(summary['by_tool']['tool_calc']['calls'], 2)
        self.assertIn('tool_date', summary['by_tool'])
        self.assertEqual(summary['by_tool']['tool_date']['calls'], 1)

        # Check fill percentage stats in summary (should be the actual objects)
        self.assertIsInstance(summary['fill_percentage_by_pydantic_model']['ModelA'], FillPercentageStats)
        self.assertAlmostEqual(summary['fill_percentage_by_pydantic_model']['ModelA'].average, (80 + 70) / 2)
        self.assertEqual(summary['fill_percentage_by_pydantic_model']['ModelA'].count, 2)
        self.assertIsInstance(summary['fill_percentage_by_llm_model']['model_a'], FillPercentageStats)
        self.assertAlmostEqual(summary['fill_percentage_by_llm_model']['model_a'].average, (80 + 70) / 2)
        self.assertEqual(summary['fill_percentage_by_llm_model']['model_a'].count, 2)


    def test_format_usage_data(self):
        # Create a sample data dictionary that mimics the output of get_usage_summary
        sample_data = {
            "usage_today": 0.0003,
            "usage_this_month": 0.0003,
            "daily_usage": [
                {"day": "2023-10-26", "model": "model_a", "service": "service_x", "pydantic_model_name": "ModelA", "input_tokens": 15, "output_tokens": 30, "total_tokens": 45, "requests": 2, "cost": 0.00015},
                {"day": "2023-10-26", "model": "model_b", "service": "service_y", "pydantic_model_name": "ModelB", "input_tokens": 15, "output_tokens": 25, "total_tokens": 40, "requests": 1, "cost": 0.00015}
            ],
             "daily_tool_usage": [
                {"day": "2023-10-26", "tool_name": "tool_calc", "calls": 2},
                {"day": "2023-10-26", "tool_name": "tool_date", "calls": 1}
            ],
            "monthly_llm_summary": {
                "2023-10": {"requests": 3, "input_tokens": 30, "output_tokens": 55, "total_tokens": 85, "cost": 0.0003}
            },
             "monthly_tool_summary": {
                "2023-10": {"total_calls": 3}
            },
            "by_model": {
                "model_a": {"requests": 2, "input_tokens": 15, "output_tokens": 30, "total_tokens": 45, "cost": 0.00015},
                "model_b": {"requests": 1, "input_tokens": 15, "output_tokens": 25, "total_tokens": 40, "cost": 0.00015}
            },
            "by_service": {
                "service_x": {"requests": 2, "input_tokens": 15, "output_tokens": 30, "total_tokens": 45, "cost": 0.00015},
                "service_y": {"requests": 1, "input_tokens": 15, "output_tokens": 25, "total_tokens": 40, "cost": 0.00015}
            },
             "usage_by_pydantic_model": {
                "ModelA": {"requests": 2, "input_tokens": 15, "output_tokens": 30, "total_tokens": 45, "cost": 0.00015},
                "ModelB": {"requests": 1, "input_tokens": 15, "output_tokens": 25, "total_tokens": 40, "cost": 0.00015}
            },
            "by_tool": {
                "tool_calc": {"calls": 2},
                "tool_date": {"calls": 1}
            },
            "fill_percentage_by_pydantic_model": {
                 "ModelA": FillPercentageStats(average=75.0, count=2, sum_total=150.0),
                 "ModelB": FillPercentageStats(average=90.0, count=1, sum_total=90.0)
            },
            "fill_percentage_by_llm_model": {
                 "model_a": FillPercentageStats(average=75.0, count=2, sum_total=150.0),
                 "model_b": FillPercentageStats(average=90.0, count=1, sum_total=90.0)
            }
        }

        formatted_output = format_usage_data(sample_data)

        self.assertIsInstance(formatted_output, str)
        self.assertIn("OVERALL USAGE SUMMARY (COSTS)", formatted_output)
        self.assertIn("DAILY LLM USAGE BREAKDOWN", formatted_output)
        self.assertIn("DAILY TOOL USAGE BREAKDOWN", formatted_output)
        self.assertIn("MONTHLY LLM USAGE SUMMARY", formatted_output)
        self.assertIn("MONTHLY TOOL USAGE SUMMARY", formatted_output)
        self.assertIn("LLM USAGE BY LLM MODEL (ALL TIME)", formatted_output)
        self.assertIn("LLM USAGE BY SERVICE (ALL TIME)", formatted_output)
        self.assertIn("LLM USAGE BY PYDANTIC MODEL (ALL TIME)", formatted_output)
        self.assertIn("TOOL USAGE BY NAME (ALL TIME)", formatted_output)
        self.assertIn("FILL PERCENTAGE BY PYDANTIC MODEL", formatted_output)
        self.assertIn("FILL PERCENTAGE BY LLM MODEL", formatted_output)

        # Check some specific values in the formatted output
        self.assertIn("$0.000300", formatted_output) # usage_today and usage_this_month
        self.assertIn("model_a", formatted_output)
        self.assertIn("tool_calc", formatted_output)
        self.assertIn("75.00%", formatted_output) # Avg fill percentage

    @patch('builtins.print')
    def test_print_usage_report(self, mock_print):
        # Just test that it calls format_usage_data and prints the result
        sample_data = {"usage_today": 0.1} # Minimal data
        with patch('src.helpers.usage_tracker.format_usage_data', return_value="Formatted Report") as mock_format:
            print_usage_report(sample_data)
            mock_format.assert_called_once_with(sample_data)
            mock_print.assert_called_once_with("Formatted Report")

    def test_format_usage_from_file(self):
        # Test loading and formatting from the dummy file
        formatted_output = format_usage_from_file(str(TEST_USAGE_FILE_PATH))
        self.assertIsInstance(formatted_output, str)
        # Check for elements expected from the initial empty content formatted
        self.assertIn("OVERALL USAGE SUMMARY (COSTS)", formatted_output)
        self.assertIn("$0.000000", formatted_output) # Initial costs are 0

    def test_format_usage_from_file_not_found(self):
        # Remove the dummy file to simulate file not found
        if os.path.exists(TEST_USAGE_FILE_PATH):
            os.remove(TEST_USAGE_FILE_PATH)

        with patch('builtins.print') as mock_print:
            formatted_output = format_usage_from_file(str(TEST_USAGE_FILE_PATH))
            self.assertIsInstance(formatted_output, str)
            mock_print.assert_called_once_with(f"Warning: Usage file {TEST_USAGE_FILE_PATH} not found. Displaying empty report structure.")
            # Should return formatted output for an empty HelperUsage object
            self.assertIn("OVERALL USAGE SUMMARY (COSTS)", formatted_output)

    def test_format_usage_from_file_corrupted_json(self):
        # Write corrupted JSON to the dummy file
        with open(TEST_USAGE_FILE_PATH, 'w') as f:
            f.write("{invalid json")

        with patch('builtins.print') as mock_print:
            formatted_output = format_usage_from_file(str(TEST_USAGE_FILE_PATH))
            self.assertIsInstance(formatted_output, str)
            mock_print.assert_called_once_with(f"Error: Could not decode JSON from {TEST_USAGE_FILE_PATH}. File might be corrupted or empty.")
            # Should return formatted output for an empty HelperUsage object
            self.assertIn("OVERALL USAGE SUMMARY (COSTS)", formatted_output)


if __name__ == '__main__':
    unittest.main()
