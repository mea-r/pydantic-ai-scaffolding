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
from pydantic_ai.providers.google import GoogleProvider
from pydantic import BaseModel, Field

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from dotenv import load_dotenv

load_dotenv()

class LLMBase:
    """Handles file content and metadata"""

    def __init__(self):
        # load .env

        key_openai = os.getenv('OPEN_AI_KEY')
        key_anthropic = os.getenv('ANTHROPIC_API_KEY')
        key_google = os.getenv('GOOGLE_API_KEY')
        open_router = os.getenv('OPEN_ROUTER_API_KEY')

        print(key_openai)
        exit()

        self.openai = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key=key_openai))
        self.anthropic = AnthropicModel('claude-3-5-sonnet-latest', provider=AnthropicProvider(api_key=key_anthropic))
        self.google = GoogleModel('gemini-2.5-pro-exp-03-25', provider=GoogleProvider(api_key=key_google))
        self.open_router = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key=open_router))

    # this is where abstraction for llm-tester will be put in place
    def get_result(self, prompt: str, model):
        agent = Agent(self.anthropic, output_type=model, instrument=True)
        result = agent.run_sync(prompt)
        return result

    def test(self):
        test_text = """I confirm that the NDA has been signed on both sides. My sincere apologies for the delay in following up - over the past few weeks, series of regional public holidays and an unusually high workload disrupted our regular scheduling.
                    Attached to this email, you'll find a short but I believe comprehensive CV of the developer we would propose for the project. He could bring solid expertise in Odoo development, and has extensive experience in odoo migrations.
                    Please feel free to reach out if you have any questions.
                    """
        prompt = 'Please analyse the sentiment of this text\n Here is the text to analyse:' + test_text
        result = self.get_result(prompt, Hello_worldModel)
        print(result)


if __name__ == '__main__':
    base = LLMBase()
    result = base.test()
    print(result)
