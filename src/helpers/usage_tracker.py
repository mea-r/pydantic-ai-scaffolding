# usage_tracker.py

from os import getenv
from typing import Any, Dict, List, Optional, Union, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import uuid
import os
from pathlib import Path
import json
import mimetypes
from decimal import Decimal
import re
from collections import defaultdict

from pydantic import BaseModel, Field

from src.py_models.base import LLMReport
from pydantic_ai.usage import Usage
from tabulate import tabulate


def format_usage_data(data: Dict[str, Any]) -> str:
    """
    Standalone function to format any usage JSON data into nicely formatted tables.
    Can be used independently of the UsageTracker class.

    Args:
        data: Dictionary containing usage data (can be from JSON file or UsageTracker)

    Returns:
        Formatted string with tables
    """
    output = []

    # Overall Summary section (Today, This Month Costs)
    if 'usage_today' in data or 'usage_this_month' in data:
        output.append("=" * 60)
        output.append("OVERALL USAGE SUMMARY (COSTS)")
        output.append("=" * 60)
        summary_data = []
        if 'usage_today' in data:
            summary_data.append(['Today (LLM Cost)', f"${data['usage_today']:.6f}"])
        if 'usage_this_month' in data:
            summary_data.append(['This Month (LLM Cost)', f"${data['usage_this_month']:.6f}"])
        if summary_data:
            output.append(tabulate(summary_data, headers=['Period', 'Value'], tablefmt='grid'))
            output.append("")

    # Monthly LLM Usage Summary
    if 'monthly_llm_summary' in data and data['monthly_llm_summary']:
        output.append("MONTHLY LLM USAGE SUMMARY")
        output.append("-" * 40)
        monthly_llm_data = []
        # Sort by total_tokens in descending order
        sorted_monthly_models = sorted(data['monthly_llm_summary'].items(), key=lambda item: item[1].get('total_tokens', 0), reverse=True)
        for month, stats in sorted_monthly_models:
            monthly_llm_data.append([
                month,
                stats.get('requests', 0),
                stats.get('input_tokens', 0),
                stats.get('output_tokens', 0),
                stats.get('total_tokens', 0),
                f"${stats.get('cost', 0):.6f}"
            ])
        headers_monthly_llm = ['Month', 'Requests', 'Input Tokens', 'Output Tokens', 'Total Tokens', 'Cost']
        output.append(tabulate(monthly_llm_data, headers=headers_monthly_llm, tablefmt='grid'))
        output.append("")

    # Monthly Tool Usage Summary
    if 'monthly_tool_summary' in data and data['monthly_tool_summary']:
        output.append("MONTHLY TOOL USAGE SUMMARY")
        output.append("-" * 40)
        monthly_tool_data = []
        sorted_months = sorted(data['monthly_tool_summary'].keys())
        for month in sorted_months:
            stats = data['monthly_tool_summary'][month]
            monthly_tool_data.append([
                month,
                stats.get('total_calls', 0)
            ])
        headers_monthly_tool = ['Month', 'Total Tool Calls']
        output.append(tabulate(monthly_tool_data, headers=headers_monthly_tool, tablefmt='grid'))
        output.append("")

    # Daily LLM usage table
    if 'daily_usage' in data and data['daily_usage']:
        output.append("DAILY LLM USAGE BREAKDOWN")
        output.append("-" * 40)
        daily_data = []
        # Sort by total_tokens in descending order
        sorted_daily_usage = sorted(data['daily_usage'], key=lambda item: item.get('total_tokens', 0), reverse=True)
        for item in sorted_daily_usage:
            daily_data.append([
                item.get('day', 'N/A'),
                item.get('model', 'N/A'),  # LLM Model
                item.get('service', 'N/A'),
                item.get('pydantic_model_name', 'N/A'),  # Pydantic Model
                item.get('requests', 0),
                item.get('input_tokens', 0),
                item.get('output_tokens', 0),
                item.get('total_tokens', 0),
                f"${item.get('cost', 0):.6f}"
            ])
        headers_daily_llm = ['Date', 'LLM Model', 'Service', 'Pydantic Model', 'Requests', 'Input Tokens',
                             'Output Tokens', 'Total Tokens', 'Cost']
        output.append(tabulate(daily_data, headers=headers_daily_llm, tablefmt='grid'))
        output.append("")

    # Daily tool usage table
    if 'daily_tool_usage' in data and data['daily_tool_usage']:
        output.append("DAILY TOOL USAGE BREAKDOWN")
        output.append("-" * 40)
        tool_daily_data = []
        for item in data['daily_tool_usage']:
            tool_daily_data.append([
                item.get('day', 'N/A'),
                item.get('tool_name', 'N/A'),
                item.get('calls', 0)
            ])
        tool_headers = ['Date', 'Tool Name', 'Calls']
        output.append(tabulate(tool_daily_data, headers=tool_headers, tablefmt='grid'))
        output.append("")

    # Fill percentage stats - CORRECTED ACCESS
    if 'fill_percentage_by_pydantic_model' in data and data['fill_percentage_by_pydantic_model']:
        output.append("FILL PERCENTAGE BY PYDANTIC MODEL")
        output.append("-" * 40)
        pydantic_data = []
        for model_name, stats_obj in data['fill_percentage_by_pydantic_model'].items():
            pydantic_data.append([
                model_name,
                f"{stats_obj.average:.2f}%" if hasattr(stats_obj, 'average') else "0.00%",  # Accessing object attribute
                stats_obj.count if hasattr(stats_obj, 'count') else 0
            ])
        output.append(tabulate(pydantic_data, headers=['Pydantic Model', 'Avg Fill %', 'Samples'], tablefmt='grid'))
        output.append("")

    if 'fill_percentage_by_llm_model' in data and data['fill_percentage_by_llm_model']:
        output.append("FILL PERCENTAGE BY LLM MODEL")
        output.append("-" * 40)
        llm_data = []
        for model_name, stats_obj in data['fill_percentage_by_llm_model'].items():
            llm_data.append([
                model_name,
                f"{stats_obj.average:.2f}%" if hasattr(stats_obj, 'average') else "0.00%",  # Accessing object attribute
                stats_obj.count if hasattr(stats_obj, 'count') else 0
            ])
        output.append(tabulate(llm_data, headers=['LLM Model', 'Avg Fill %', 'Samples'], tablefmt='grid'))
        output.append("")

    # All time LLM Usage by LLM Model
    if 'by_model' in data:
        output.append("LLM USAGE BY LLM MODEL (ALL TIME)")
        output.append("-" * 40)
        model_data = []
        # Sort by total_tokens in descending order
        sorted_models = sorted(data['by_model'].items(), key=lambda item: item[1].get('total_tokens', 0), reverse=True)
        for model, stats in sorted_models:
            # Get fill percentage for this model
            fill_stats = data.get('fill_percentage_by_llm_model', {}).get(model)
            avg_fill_percentage = f"{fill_stats.average:.2f}%" if fill_stats and hasattr(fill_stats, 'average') else "N/A"

            model_data.append([
                model,
                stats.get('requests', 0),
                stats.get('input_tokens', 0),
                stats.get('output_tokens', 0),
                stats.get('total_tokens', 0),
                f"${stats.get('cost', 0):.6f}",
                avg_fill_percentage  # Add average fill percentage
            ])
        output.append(
            tabulate(model_data,
                     headers=['LLM Model', 'Requests', 'Input Tokens', 'Output Tokens', 'Total Tokens', 'Cost', 'Avg Fill %'], # Updated header
                     tablefmt='grid'))
        output.append("")

    # All time LLM Usage by Pydantic Model
    if 'usage_by_pydantic_model' in data and data['usage_by_pydantic_model']:
        output.append("LLM USAGE BY PYDANTIC MODEL (ALL TIME)")
        output.append("-" * 40)
        pydantic_usage_data = []
        for p_model_name, stats in data['usage_by_pydantic_model'].items():
            pydantic_usage_data.append([
                p_model_name,
                stats.get('requests', 0),
                stats.get('input_tokens', 0),
                stats.get('output_tokens', 0),
                stats.get('total_tokens', 0),
                f"${stats.get('cost', 0):.6f}"
            ])
        output.append(
            tabulate(pydantic_usage_data,
                     headers=['Pydantic Model', 'Requests', 'Input Tokens', 'Output Tokens', 'Total Tokens', 'Cost'],
                     tablefmt='grid'))
        output.append("")

    # Service usage summary
    if 'by_service' in data:
        output.append("LLM USAGE BY SERVICE (ALL TIME)")
        output.append("-" * 40)
        service_data = []
        for service, stats in data['by_service'].items():
            service_data.append([
                service,
                stats.get('requests', 0),
                stats.get('input_tokens', 0),
                stats.get('output_tokens', 0),
                stats.get('total_tokens', 0),
                f"${stats.get('cost', 0):.6f}"
            ])
        output.append(tabulate(service_data,
                               headers=['Service', 'Requests', 'Input Tokens', 'Output Tokens', 'Total Tokens', 'Cost'],
                               tablefmt='grid'))
        output.append("")

    # Tool usage summary
    if 'by_tool' in data:
        output.append("TOOL USAGE BY NAME (ALL TIME)")
        output.append("-" * 40)
        tool_summary_data = []
        for tool_name, stats in data['by_tool'].items():
            tool_summary_data.append([
                tool_name,
                stats.get('calls', 0)
            ])
        output.append(tabulate(tool_summary_data, headers=['Tool Name', 'Total Calls'], tablefmt='grid'))
        output.append("")

    return "\n".join(output)


def print_usage_report(data: Dict[str, Any]):
    print(format_usage_data(data))


def format_usage_from_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        print(f"Warning: Usage file {file_path} not found. Displaying empty report structure.")
        empty_usage_data = HelperUsage().model_dump()
        return format_usage_data(empty_usage_data)
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {file_path}. File might be corrupted or empty.")
            empty_usage_data = HelperUsage().model_dump()
            return format_usage_data(empty_usage_data)
    # If loading from file, the fill percentage stats will be dicts, not objects.
    # The get_usage_summary() returns objects, so we handle both in format_usage_data if necessary,
    # but it's better if get_usage_summary converts them to dicts if they are objects.
    # For now, the fix in format_usage_data assumes it might get objects.
    return format_usage_data(data)


class FillPercentageStats(BaseModel):
    average: float = Field(default=0.0)
    count: int = Field(default=0)
    sum_total: float = Field(default=0.0)


class UsageItem(BaseModel):  # For LLM Usage
    month: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m"))
    day: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    model: str = Field(default="")  # LLM Model name
    service: str = Field(default="")  # LLM Service/Provider
    pydantic_model_name: str = Field(default="N/A")  # Associated Pydantic Model
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    requests: int = Field(default=0)
    cost: float = Field(default=0.0)


class ToolUsageItem(BaseModel):  # For Tool Usage
    month: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m"))
    day: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    tool_name: str = Field(default="")
    calls: int = Field(default=0)


class HelperUsage(BaseModel):
    usage_today: float = Field(default=0.0)
    usage_this_month: float = Field(default=0.0)
    daily_usage: List[UsageItem] = Field(default_factory=list)
    daily_tool_usage: List[ToolUsageItem] = Field(default_factory=list)
    fill_percentage_by_pydantic_model: Dict[str, FillPercentageStats] = Field(default_factory=dict)
    fill_percentage_by_llm_model: Dict[str, FillPercentageStats] = Field(default_factory=dict)


class UsageTracker:
    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            self.config_path = os.path.join(os.path.dirname(__file__), '../../logs/usage.json')
        else:
            self.config_path = os.path.join(base_path, 'logs/usage.json')

        if not os.path.exists(self.config_path):
            self._create_empty_usage_file()
        self.usage_data = self._load()

    def _create_empty_usage_file(self):
        empty_usage = HelperUsage()
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(empty_usage.model_dump(exclude_none=True), f, indent=4)

    def _load(self) -> HelperUsage:
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                # Ensure new fields exist with defaults if loading an old file
                if 'daily_tool_usage' not in data:
                    data['daily_tool_usage'] = []
                # For UsageItem, Pydantic will use default for pydantic_model_name if missing
                return HelperUsage(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: usage.json not found or corrupted at {self.config_path}. Creating a new one.")
            self._create_empty_usage_file()
            return HelperUsage()

    def _save(self):
        # Using model_dump for consistent serialization of Pydantic models
        # Pydantic's default JSON encoder handles Decimal and float precision well.
        # The regex was for extreme cases, let's simplify and rely on Pydantic first.
        json_str = self.usage_data.model_dump_json(indent=4)

        # If scientific notation is still an issue with floats after Pydantic's dump:
        def replace_scientific(match):
            num = float(match.group(0))
            return f"{num:.8f}".rstrip('0').rstrip('.') if '.' in f"{num:.8f}" else f"{num:.8f}"

        json_str = re.sub(r'\d+\.?\d*e[+-]?\d+', replace_scientific, json_str, flags=re.IGNORECASE)

        with open(self.config_path, 'w') as f:
            f.write(json_str)

    def _update_fill_percentage_stats(self, pydantic_model_name: str, llm_model_name: str, fill_percentage: float):
        if pydantic_model_name not in self.usage_data.fill_percentage_by_pydantic_model:
            self.usage_data.fill_percentage_by_pydantic_model[pydantic_model_name] = FillPercentageStats()
        p_stats = self.usage_data.fill_percentage_by_pydantic_model[pydantic_model_name]
        p_stats.count += 1
        p_stats.sum_total += fill_percentage
        p_stats.average = p_stats.sum_total / p_stats.count

        if llm_model_name not in self.usage_data.fill_percentage_by_llm_model:
            self.usage_data.fill_percentage_by_llm_model[llm_model_name] = FillPercentageStats()
        l_stats = self.usage_data.fill_percentage_by_llm_model[llm_model_name]
        l_stats.count += 1
        l_stats.sum_total += fill_percentage
        l_stats.average = l_stats.sum_total / l_stats.count

    def add_usage(self, usage_report: LLMReport, model_name: str, service: str,
                  pydantic_model_name: Optional[str] = None,  # Now required for LLM usage
                  tool_names_called: Optional[List[str]] = None):
        current_date = datetime.now()
        current_day = current_date.strftime("%Y-%m-%d")
        current_month = current_date.strftime("%Y-%m")

        # Ensure pydantic_model_name is provided for LLM usage
        actual_pydantic_model_name = pydantic_model_name or "N/A"

        llm_usage_obj = usage_report.usage or Usage()
        input_tokens = llm_usage_obj.request_tokens or 0
        output_tokens = llm_usage_obj.response_tokens or 0
        total_tokens = llm_usage_obj.total_tokens or 0
        requests = llm_usage_obj.requests or 1
        cost = usage_report.cost

        if pydantic_model_name and usage_report.fill_percentage is not None and usage_report.fill_percentage >= 0:
            self._update_fill_percentage_stats(actual_pydantic_model_name, model_name, usage_report.fill_percentage)

        existing_llm_item = None
        for item in self.usage_data.daily_usage:
            if (item.day == current_day and
                    item.model == model_name and
                    item.service == service and
                    item.pydantic_model_name == actual_pydantic_model_name):  # Added pydantic_model_name to key
                existing_llm_item = item
                break

        if existing_llm_item:
            existing_llm_item.input_tokens += input_tokens
            existing_llm_item.output_tokens += output_tokens
            existing_llm_item.total_tokens += total_tokens
            existing_llm_item.requests += requests
            existing_llm_item.cost += cost
        else:
            usage_item = UsageItem(
                month=current_month,
                day=current_day,
                model=model_name,
                service=service,
                pydantic_model_name=actual_pydantic_model_name,  # Storing it
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                requests=requests,
                cost=cost
            )
            self.usage_data.daily_usage.append(usage_item)

        if tool_names_called:
            for tool_name in tool_names_called:
                existing_tool_item = None
                for item in self.usage_data.daily_tool_usage:
                    if item.day == current_day and item.tool_name == tool_name:
                        existing_tool_item = item
                        break
                if existing_tool_item:
                    existing_tool_item.calls += 1
                else:
                    self.usage_data.daily_tool_usage.append(ToolUsageItem(
                        month=current_month, day=current_day, tool_name=tool_name, calls=1
                    ))

        self.usage_data.usage_today = self._calculate_usage_today()
        self.usage_data.usage_this_month = self._calculate_usage_this_month()
        self._save()

    def _calculate_usage_today(self) -> float:
        today = datetime.now().strftime("%Y-%m-%d")
        return sum(item.cost for item in self.usage_data.daily_usage if item.day == today)

    def _calculate_usage_this_month(self) -> float:
        current_month = datetime.now().strftime("%Y-%m")
        return sum(item.cost for item in self.usage_data.daily_usage if item.month == current_month)

    def get_usage_today(self) -> float:
        return self._calculate_usage_today()

    def get_usage_this_month(self) -> float:
        return self._calculate_usage_this_month()

    # Methods like get_usage_by_model, get_usage_by_service, get_tool_usage_by_name remain useful for specific queries
    # but get_usage_summary will provide the main data for the report.

    def get_usage_summary(self) -> Dict[str, Any]:
        summary = {}
        summary['usage_today'] = self.get_usage_today()
        summary['usage_this_month'] = self.get_usage_this_month()

        # --- Daily Summaries (Aggregated for Report) ---
        # Aggregate daily LLM usage by day, model, service, and pydantic model
        daily_llm_summary_aggregated = defaultdict(
            lambda: {'day': '', 'model': '', 'service': '', 'pydantic_model_name': '', 'requests': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost': 0.0})
        for item in self.usage_data.daily_usage:
            key = (item.day, item.model, item.service, item.pydantic_model_name)
            daily_llm_summary_aggregated[key]['day'] = item.day
            daily_llm_summary_aggregated[key]['model'] = item.model
            daily_llm_summary_aggregated[key]['service'] = item.service
            daily_llm_summary_aggregated[key]['pydantic_model_name'] = item.pydantic_model_name
            daily_llm_summary_aggregated[key]['requests'] += item.requests
            daily_llm_summary_aggregated[key]['input_tokens'] += item.input_tokens
            daily_llm_summary_aggregated[key]['output_tokens'] += item.output_tokens
            daily_llm_summary_aggregated[key]['total_tokens'] += item.total_tokens
            daily_llm_summary_aggregated[key]['cost'] += item.cost
        summary['daily_usage'] = list(daily_llm_summary_aggregated.values())


        # Aggregate daily tool usage by day and tool name
        daily_tool_summary_aggregated = defaultdict(lambda: {'day': '', 'tool_name': '', 'calls': 0})
        for item in self.usage_data.daily_tool_usage:
            key = (item.day, item.tool_name)
            daily_tool_summary_aggregated[key]['day'] = item.day
            daily_tool_summary_aggregated[key]['tool_name'] = item.tool_name
            daily_tool_summary_aggregated[key]['calls'] += item.calls
        summary['daily_tool_usage'] = list(daily_tool_summary_aggregated.values())


        # --- Monthly Summaries ---
        monthly_llm_summary = defaultdict(
            lambda: {'requests': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost': 0.0})
        for item in self.usage_data.daily_usage:
            month_key = item.month
            monthly_llm_summary[month_key]['requests'] += item.requests
            monthly_llm_summary[month_key]['input_tokens'] += item.input_tokens
            monthly_llm_summary[month_key]['output_tokens'] += item.output_tokens
            monthly_llm_summary[month_key]['total_tokens'] += item.total_tokens
            monthly_llm_summary[month_key]['cost'] += item.cost
        summary['monthly_llm_summary'] = dict(monthly_llm_summary)

        monthly_tool_summary = defaultdict(lambda: {'total_calls': 0})
        for item in self.usage_data.daily_tool_usage:
            month_key = item.month
            monthly_tool_summary[month_key]['total_calls'] += item.calls
        summary['monthly_tool_summary'] = dict(monthly_tool_summary)

        # --- All-Time Aggregations ---
        # By LLM Model
        by_model = defaultdict(
            lambda: {'requests': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost': 0.0})
        for item in self.usage_data.daily_usage:
            by_model[item.model]['requests'] += item.requests
            by_model[item.model]['input_tokens'] += item.input_tokens
            by_model[item.model]['output_tokens'] += item.output_tokens
            by_model[item.model]['total_tokens'] += item.total_tokens
            by_model[item.model]['cost'] += item.cost
        summary['by_model'] = dict(by_model)

        # By LLM Service
        by_service = defaultdict(
            lambda: {'requests': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost': 0.0})
        for item in self.usage_data.daily_usage:
            by_service[item.service]['requests'] += item.requests
            by_service[item.service]['input_tokens'] += item.input_tokens
            by_service[item.service]['output_tokens'] += item.output_tokens
            by_service[item.service]['total_tokens'] += item.total_tokens
            by_service[item.service]['cost'] += item.cost
        summary['by_service'] = dict(by_service)

        # By Pydantic Model (for LLM usage)
        usage_by_pydantic_model = defaultdict(
            lambda: {'requests': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost': 0.0})
        for item in self.usage_data.daily_usage:
            # Only include if pydantic_model_name is not "N/A" or if you want to see "N/A" as a category
            if item.pydantic_model_name != "N/A":
                key = item.pydantic_model_name
                usage_by_pydantic_model[key]['requests'] += item.requests
                usage_by_pydantic_model[key]['input_tokens'] += item.input_tokens
                usage_by_pydantic_model[key]['output_tokens'] += item.output_tokens
                usage_by_pydantic_model[key]['total_tokens'] += item.total_tokens
                usage_by_pydantic_model[key]['cost'] += item.cost
        summary['usage_by_pydantic_model'] = dict(usage_by_pydantic_model)

        # By Tool Name
        by_tool = defaultdict(lambda: {'calls': 0})
        for item in self.usage_data.daily_tool_usage:
            by_tool[item.tool_name]['calls'] += item.calls
        summary['by_tool'] = dict(by_tool)

        # Fill Percentage Stats (passing the actual objects)
        summary['fill_percentage_by_pydantic_model'] = self.usage_data.fill_percentage_by_pydantic_model
        summary['fill_percentage_by_llm_model'] = self.usage_data.fill_percentage_by_llm_model

        summary['total_llm_requests'] = sum(stats['requests'] for stats in by_model.values())
        summary['total_tool_calls'] = sum(stats['calls'] for stats in by_tool.values())

        return summary

    @property
    def config(self) -> HelperUsage:
        # This can simply return self.usage_data as calculations are done on demand or during add_usage
        return self.usage_data
