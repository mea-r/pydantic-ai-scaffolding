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

from .llm_info_provider import LLMInfoProvider
from py_models.base import LLMReport
from py_models.hello_world.model import Hello_worldModel


"""
Saves reports to either files or database.
"""

class ReportGenerator:

    def __init__(self, target: str = 'file'):
        pass



