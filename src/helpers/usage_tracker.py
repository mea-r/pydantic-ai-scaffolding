from os import getenv
from typing import Any, Dict, List, Optional, Union, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime
import uuid
import os
from pathlib import Path
import json
import mimetypes

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.providers.google import GoogleProvider
from pydantic import BaseModel, Field

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from dotenv import load_dotenv

from py_models.base import LLMReport

import json
from os import path
from typing import Any, Dict, List
from pydantic import BaseModel, Field
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

    # Summary section
    if 'usage_today' in data or 'usage_this_month' in data:
        output.append("=" * 60)
        output.append("USAGE SUMMARY")
        output.append("=" * 60)

        summary_data = []
        if 'usage_today' in data:
            summary_data.append(['Today', f"${data['usage_today']:.6f}"])
        if 'usage_this_month' in data:
            summary_data.append(['This Month', f"${data['usage_this_month']:.6f}"])

        if summary_data:
            output.append(tabulate(summary_data, headers=['Period', 'Cost'], tablefmt='grid'))
            output.append("")

    # Daily usage table
    if 'daily_usage' in data and data['daily_usage']:
        output.append("DAILY USAGE BREAKDOWN")
        output.append("-" * 40)

        daily_data = []
        for item in data['daily_usage']:
            daily_data.append([
                item.get('day', 'N/A'),
                item.get('model', 'N/A'),
                item.get('service', 'N/A'),
                item.get('requests', 0),
                item.get('input_tokens', 0),
                item.get('output_tokens', 0),
                item.get('total_tokens', 0),
                f"${item.get('cost', 0):.6f}"
            ])

        headers = ['Date', 'Model', 'Service', 'Requests', 'Input Tokens', 'Output Tokens', 'Total Tokens', 'Cost']
        output.append(tabulate(daily_data, headers=headers, tablefmt='grid'))
        output.append("")

    # Fill percentage stats
    if 'fill_percentage_by_pydantic_model' in data and data['fill_percentage_by_pydantic_model']:
        output.append("FILL PERCENTAGE BY PYDANTIC MODEL")
        output.append("-" * 40)

        pydantic_data = []
        for model_name, stats in data['fill_percentage_by_pydantic_model'].items():
            pydantic_data.append([
                model_name,
                f"{stats.get('average', 0):.2f}%",
                stats.get('sample_count', 0)
            ])

        output.append(tabulate(pydantic_data, headers=['Model', 'Avg Fill %', 'Samples'], tablefmt='grid'))
        output.append("")

    if 'fill_percentage_by_llm_model' in data and data['fill_percentage_by_llm_model']:
        output.append("FILL PERCENTAGE BY LLM MODEL")
        output.append("-" * 40)

        llm_data = []
        for model_name, stats in data['fill_percentage_by_llm_model'].items():
            llm_data.append([
                model_name,
                f"{stats.get('average', 0):.2f}%",
                stats.get('sample_count', 0)
            ])

        output.append(tabulate(llm_data, headers=['Model', 'Avg Fill %', 'Samples'], tablefmt='grid'))
        output.append("")

    # Model usage summary (if available from get_usage_summary())
    if 'by_model' in data:
        output.append("USAGE BY MODEL")
        output.append("-" * 40)

        model_data = []
        for model, stats in data['by_model'].items():
            model_data.append([
                model,
                stats.get('requests', 0),
                stats.get('input_tokens', 0),
                stats.get('output_tokens', 0),
                stats.get('total_tokens', 0),
                f"${stats.get('cost', 0):.6f}"
            ])

        output.append(
            tabulate(model_data, headers=['Model', 'Requests', 'Input Tokens', 'Output Tokens', 'Total Tokens', 'Cost'],
                     tablefmt='grid'))
        output.append("")

    # Service usage summary
    if 'by_service' in data:
        output.append("USAGE BY SERVICE")
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

    return "\n".join(output)


def print_usage_report(data: Dict[str, Any]):
    """
    Convenience function to print formatted usage data

    Args:
        data: Dictionary containing usage data
    """
    print(format_usage_data(data))


def format_usage_from_file(file_path: str) -> str:
    """
    Load usage data from JSON file and format it

    Args:
        file_path: Path to JSON usage file

    Returns:
        Formatted string with tables
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return format_usage_data(data)


class FillPercentageStats(BaseModel):
    average: float = Field(default=0.0, description="Running average fill percentage")
    count: int = Field(default=0, description="Number of samples")
    sum_total: float = Field(default=0.0, description="Sum of all fill percentages for calculation")


class UsageItem(BaseModel):
    month: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m"))
    day: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    model: str = Field(default="")
    service: str = Field(default="")
    input_tokens: int = Field(default=0, description="Number of input tokens used")
    output_tokens: int = Field(default=0, description="Number of output tokens used")
    total_tokens: int = Field(default=0, description="Total tokens used")
    requests: int = Field(default=0, description="Number of requests")
    cost: float = Field(default=0.0, description="Cost incurred for the usage")


class HelperUsage(BaseModel):
    usage_today: float = Field(default=0.0, description="Total cost incurred today")
    usage_this_month: float = Field(default=0.0, description="Total cost incurred this month")
    daily_usage: List[UsageItem] = Field(default_factory=list)
    # Fill percentage tracking by pydantic model and llm model
    fill_percentage_by_pydantic_model: Dict[str, FillPercentageStats] = Field(default_factory=dict)
    fill_percentage_by_llm_model: Dict[str, FillPercentageStats] = Field(default_factory=dict)


class UsageTracker:
    def __init__(self):
        self.config_path = path.join(path.dirname(__file__), '../../usage.json')
        if not path.exists(self.config_path):
            # Create empty usage file if it doesn't exist
            self._create_empty_usage_file()
        self.usage_data = self._load()

    def _create_empty_usage_file(self):
        """Create an empty usage file with default structure"""
        empty_usage = HelperUsage()
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(empty_usage.model_dump(), f, indent=4)

    def _load(self) -> HelperUsage:
        with open(self.config_path, 'r') as f:
            return HelperUsage(**json.load(f))

    def _save(self):
        """Save usage data with proper float formatting to avoid scientific notation"""

        def format_floats(obj):
            if isinstance(obj, dict):
                return {k: format_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [format_floats(item) for item in obj]
            elif isinstance(obj, float):
                # Convert to Decimal to avoid scientific notation, then back to float
                from decimal import Decimal
                return float(Decimal(str(obj)))
            else:
                return obj

        formatted_data = format_floats(self.usage_data.model_dump())

        # Write JSON with custom formatting to avoid scientific notation
        json_str = json.dumps(formatted_data, indent=4)

        # Replace any remaining scientific notation with fixed decimal
        import re
        def replace_scientific(match):
            num = float(match.group(0))
            return f"{num:.8f}".rstrip('0').rstrip('.')

        json_str = re.sub(r'\d+\.?\d*e[+-]?\d+', replace_scientific, json_str, flags=re.IGNORECASE)

        with open(self.config_path, 'w') as f:
            f.write(json_str)


    def _update_fill_percentage_stats(self, pydantic_model_name: str, llm_model_name: str, fill_percentage: int):
        """Update running average for fill percentage without storing individual calls"""
        # Update pydantic model stats
        if pydantic_model_name not in self.usage_data.fill_percentage_by_pydantic_model:
            self.usage_data.fill_percentage_by_pydantic_model[pydantic_model_name] = FillPercentageStats()

        pydantic_stats = self.usage_data.fill_percentage_by_pydantic_model[pydantic_model_name]
        pydantic_stats.count += 1
        pydantic_stats.sum_total += fill_percentage
        pydantic_stats.average = pydantic_stats.sum_total / pydantic_stats.count

        # Update LLM model stats
        if llm_model_name not in self.usage_data.fill_percentage_by_llm_model:
            self.usage_data.fill_percentage_by_llm_model[llm_model_name] = FillPercentageStats()

        llm_stats = self.usage_data.fill_percentage_by_llm_model[llm_model_name]
        llm_stats.count += 1
        llm_stats.sum_total += fill_percentage
        llm_stats.average = llm_stats.sum_total / llm_stats.count

    def add_usage(self, usage_report: LLMReport, model_name: str, service: str,
                  pydantic_model_name: Optional[str] = None):
        """Add usage data and update totals"""
        current_date = datetime.now()
        current_day = current_date.strftime("%Y-%m-%d")
        current_month = current_date.strftime("%Y-%m")

        # Extract usage data from PydanticAI Usage structure
        usage = usage_report.usage or Usage()
        input_tokens = usage.request_tokens or 0
        output_tokens = usage.response_tokens or 0
        total_tokens = usage.total_tokens or 0
        requests = usage.requests or 1

        # Use cost directly from LLMReport
        cost = usage_report.cost

        # Update fill percentage stats if provided
        if pydantic_model_name and usage_report.fill_percentage >= 0:
            self._update_fill_percentage_stats(pydantic_model_name, model_name, usage_report.fill_percentage)

        # Find existing usage item for today with same model and service for aggregation
        existing_item = None
        for item in self.usage_data.daily_usage:
            if (item.day == current_day and
                    item.model == model_name and
                    item.service == service):
                existing_item = item
                break

        if existing_item:
            # Aggregate with existing item
            existing_item.input_tokens += input_tokens
            existing_item.output_tokens += output_tokens
            existing_item.total_tokens += total_tokens
            existing_item.requests += requests
            existing_item.cost += cost
        else:
            # Create new usage item
            usage_item = UsageItem(
                month=current_month,
                day=current_day,
                model=model_name,
                service=service,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                requests=requests,
                cost=cost
            )
            self.usage_data.daily_usage.append(usage_item)

        # Update totals
        self.usage_data.usage_today = self._calculate_usage_today()
        self.usage_data.usage_this_month = self._calculate_usage_this_month()

        # Save to file
        self._save()

    def _calculate_usage_today(self) -> float:
        """Calculate total usage for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        return sum(item.cost for item in self.usage_data.daily_usage if item.day == today)

    def _calculate_usage_this_month(self) -> float:
        """Calculate total usage for this month"""
        current_month = datetime.now().strftime("%Y-%m")
        return sum(item.cost for item in self.usage_data.daily_usage if item.month == current_month)

    def get_usage_today(self) -> float:
        """Return usage by model and service for today"""
        self.usage_data.usage_today = self._calculate_usage_today()
        return self.usage_data.usage_today

    def get_usage_this_month(self) -> float:
        """Return usage by model and service for this month"""
        self.usage_data.usage_this_month = self._calculate_usage_this_month()
        return self.usage_data.usage_this_month

    def get_usage_by_model(self, model_name: str, date_from: datetime, date_to: datetime) -> List[UsageItem]:
        """Get usage data filtered by model and date range"""
        from_str = date_from.strftime("%Y-%m-%d")
        to_str = date_to.strftime("%Y-%m-%d")

        return [
            item for item in self.usage_data.daily_usage
            if item.model == model_name and from_str <= item.day <= to_str
        ]

    def get_usage_by_service(self, service: str, date_from: datetime, date_to: datetime) -> List[UsageItem]:
        """Get usage data filtered by service and date range"""
        from_str = date_from.strftime("%Y-%m-%d")
        to_str = date_to.strftime("%Y-%m-%d")

        return [
            item for item in self.usage_data.daily_usage
            if item.service == service and from_str <= item.day <= to_str
        ]

    def get_fill_percentage_stats(self) -> Dict[str, Any]:
        """Get fill percentage statistics by pydantic model and LLM model"""
        return {
            'by_pydantic_model': {
                name: {
                    'average': stats.average,
                    'sample_count': stats.count
                }
                for name, stats in self.usage_data.fill_percentage_by_pydantic_model.items()
            },
            'by_llm_model': {
                name: {
                    'average': stats.average,
                    'sample_count': stats.count
                }
                for name, stats in self.usage_data.fill_percentage_by_llm_model.items()
            }
        }

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of usage statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.now().strftime("%Y-%m")

        # Group by model
        model_usage = {}
        for item in self.usage_data.daily_usage:
            if item.model not in model_usage:
                model_usage[item.model] = {
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'total_tokens': 0,
                    'requests': 0,
                    'cost': 0.0
                }
            model_usage[item.model]['input_tokens'] += item.input_tokens
            model_usage[item.model]['output_tokens'] += item.output_tokens
            model_usage[item.model]['total_tokens'] += item.total_tokens
            model_usage[item.model]['requests'] += item.requests
            model_usage[item.model]['cost'] += item.cost

        # Group by service
        service_usage = {}
        for item in self.usage_data.daily_usage:
            if item.service not in service_usage:
                service_usage[item.service] = {
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'total_tokens': 0,
                    'requests': 0,
                    'cost': 0.0
                }
            service_usage[item.service]['input_tokens'] += item.input_tokens
            service_usage[item.service]['output_tokens'] += item.output_tokens
            service_usage[item.service]['total_tokens'] += item.total_tokens
            service_usage[item.service]['requests'] += item.requests
            service_usage[item.service]['cost'] += item.cost

        return {
            'today': self.get_usage_today(),
            'this_month': self.get_usage_this_month(),
            'by_model': model_usage,
            'by_service': service_usage,
            'total_requests': sum(item.requests for item in self.usage_data.daily_usage),
            'fill_percentage_stats': self.get_fill_percentage_stats()
        }

    @property
    def config(self) -> HelperUsage:
        return self.usage_data
