"""
hello_world model type definition
"""

import os
import json
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
from datetime import date

from py_models.base import BasePyModel


class WeatherModel(BasePyModel):

    name: ClassVar[str] = "WeatherModel"

    # Define model fields - REPLACE WITH YOUR SCHEMA
    tool_results: Optional[dict] = Field(..., description="Results from tool calls")
    haiku: str = Field(..., description="Haiku about the weather")
    report: str = Field(..., description="Weather report, official")
