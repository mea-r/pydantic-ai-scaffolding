"""
hello_world model type definition
"""

import os
import json
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
from datetime import date

from py_models.base import BasePyModel


class Hello_worldModel(BasePyModel):
    """
    Model for extracting structured information for hello_world
    """

    # Class variables for module configuration
    MODULE_NAME: ClassVar[str] = "hello_world"
    TEST_DIR: ClassVar[str] = os.path.join(os.path.dirname(__file__), "tests")
    REPORT_DIR: ClassVar[str] = os.path.join(os.path.dirname(__file__), "reports")

    # Define model fields - REPLACE WITH YOUR SCHEMA
    message_sentiment: int = Field(..., description="How positive is this message from 1 = very negative, 10 = very positive")
    expects_response: bool = Field(..., description="Does the writer expect a response?")
