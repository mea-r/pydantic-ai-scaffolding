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

from llm_info_provider import LLMInfoProvider
from py_models.base import LLMReport
from py_models.hello_world import Hello_worldModel


class ReportGenerator:
    """Handles file content and metadata"""

    def __init__(self):
        # load .env

        key_openai = os.getenv('OPENAI_API_KEY')
        key_anthropic = os.getenv('ANTHROPIC_API_KEY')
        key_google = os.getenv('GOOGLE_API_KEY')
        open_router = os.getenv('OPEN_ROUTER_API_KEY')

        self.openai = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key=key_openai))
        self.anthropic = AnthropicModel('claude-3-5-sonnet-latest', provider=AnthropicProvider(api_key=key_anthropic))
        self.google = GoogleModel('gemini-2.5-pro-exp-03-25', provider=GoogleProvider(api_key=key_google))
        self.open_router = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key=open_router))

        self.info_provider = LLMInfoProvider()

