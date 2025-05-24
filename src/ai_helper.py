from typing import Any, Optional, Union, TypeVar, Tuple
from datetime import datetime
import uuid
import os
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.providers.google import GoogleProvider

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from dotenv import load_dotenv
from pydantic_ai.providers.openrouter import OpenRouterProvider

from helpers.llm_info_provider import LLMInfoProvider
from py_models.base import LLMReport
from py_models.hello_world.model import Hello_worldModel

load_dotenv()
T = TypeVar('T', bound='BasePyModel')

class AiHelper:
    """Handles file content and metadata"""

    def __init__(self):
        key_openai = os.getenv('OPENAI_API_KEY')
        key_anthropic = os.getenv('ANTHROPIC_API_KEY')
        key_google = os.getenv('GOOGLE_API_KEY')
        open_router = os.getenv('OPEN_ROUTER_API_KEY')

        self.openai = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key=key_openai))
        self.anthropic = AnthropicModel('claude-3-5-sonnet-latest', provider=AnthropicProvider(api_key=key_anthropic))
        self.google = GoogleModel('gemini-2.5-pro-exp-03-25', provider=GoogleProvider(api_key=key_google))
        self.open_router = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key=open_router))

        self.info_provider = LLMInfoProvider()

    """
    Do the actual request and generate cost report + cost info + save whatever needs to be saved
    """
    def get_result(self, prompt: str, pydantic_model, model_name: str = 'deepseek/deepseek-prover-v2:free', file: Optional[Union[str, Path]] = None, provider='open_router', tools: list = None) -> Tuple[T, LLMReport] | Tuple[None, None]:

        if '/' not in model_name:
            raise ValueError(f"Model name '{model_name}' must be in the format 'provider/model_name'.")

        llm_provider = self._get_llm_provider(provider, model_name)
        agent = Agent(llm_provider, output_type=pydantic_model, instrument=True, tools=tools)
        agent_output = agent.run_sync(prompt)
        result = agent_output.output
        return result, self._post_process(agent_output, model_name)

    """
    Usage data calculation. Save hooks for reporting.
    """
    def _post_process(self, agent_result: AgentRunResult, model_name) -> LLMReport:
        report = LLMReport(
            model_name=model_name,
            usage=agent_result.usage(),
            run_date=datetime.now(),
            run_id=str(uuid.uuid4()),
        )

        filled_fields = len([field for field in agent_result.output.__dict__.values() if field is not None])
        total_fields = len(agent_result.output.__dict__)
        percentage = int((filled_fields / total_fields) * 100)

        report.cost = self.info_provider.get_cost_info(model_name, agent_result.usage())
        report.fill_percentage = percentage
        return report

    def _get_llm_provider(self, name: str, model_name: str) -> Any:
        # if not self.info_provider.get_model_info(model_name):
        #     raise ValueError(f"Unknown model: {model_name}")

        # Split model_name to get provider and model
        if name != 'open_router':
            model_name = model_name.split('/',1)[-1]
        elif not self.info_provider.get_model_info(model_name):
            raise ValueError(f"Unknown model: {model_name}")

        """
        Returns the appropriate LLM provider based on the name.
        """

        if name == 'openai':
            self.openai = OpenAIModel(model_name, provider=OpenAIProvider(api_key=os.getenv('OPENAI_API_KEY')))
            return self.openai
        elif name == 'anthropic':
            self.anthropic = AnthropicModel(model_name, provider=AnthropicProvider(api_key=os.getenv('ANTHROPIC_API_KEY')))
            return self.anthropic
        elif name == 'google':
            self.google = GoogleModel(model_name, provider=GoogleProvider(api_key=os.getenv('GOOGLE_API_KEY')))
            return self.google
        elif name == 'open_router':
            self.open_router = OpenAIModel(model_name, provider=OpenRouterProvider(api_key=os.getenv('OPEN_ROUTER_API_KEY')))
            return self.open_router
        else:
            raise ValueError(f"Unknown provider: {name}")

