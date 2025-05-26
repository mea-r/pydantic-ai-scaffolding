from typing import Any, Optional, Union, TypeVar, Tuple, List
from datetime import datetime
import uuid
import mimetypes
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import ModelResponse, ToolCallPart, BinaryContent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
from dotenv import load_dotenv
import os

from helpers.llm_info_provider import LLMInfoProvider
from helpers.usage_tracker import UsageTracker
from helpers.config_helper import ConfigHelper
from py_models.base import LLMReport

load_dotenv()
T = TypeVar('T', bound='BasePyModel')


class AiHelper:
    def __init__(self):
        self.info_provider = LLMInfoProvider()
        self.usage_tracker = UsageTracker()
        self.config_helper = ConfigHelper()

        # Provider configs
        self.providers = {
            'openai': (OpenAIModel, OpenAIProvider, 'OPENAI_API_KEY'),
            'anthropic': (AnthropicModel, AnthropicProvider, 'ANTHROPIC_API_KEY'),
            'google': (GoogleModel, GoogleProvider, 'GOOGLE_API_KEY'),
            'open_router': (OpenAIModel, OpenRouterProvider, 'OPEN_ROUTER_API_KEY')
        }

    """
    This is the main sync method we use
    """
    def get_result(self, prompt: str, pydantic_model, llm_model_name: str = 'deepseek/deepseek-prover-v2:free',
                   file: Optional[Union[str, Path]] = None, provider='open_router', tools: list = None,
                   agent_config: Optional[dict] = None) -> Tuple[T, LLMReport] | Tuple[None, None]:
        if '/' not in llm_model_name:
            raise ValueError(f"Model name '{llm_model_name}' must be in the format 'provider/model_name'.")

        tools = tools or []
        user_prompt = self._prepare_prompt(prompt, file)
        fallback_models = self._build_fallback_chain(llm_model_name, provider, agent_config)

        return self._execute_with_fallback(user_prompt, pydantic_model, fallback_models, tools)

    """
    Async version is used by agent graphs
    """
    async def get_result_async(self, prompt: str, pydantic_model,
                               llm_model_name: str = 'deepseek/deepseek-prover-v2:free',
                               file: Optional[Union[str, Path]] = None, provider='open_router', tools: list = None,
                               agent_config: Optional[dict] = None) -> Tuple[T, LLMReport] | Tuple[None, None]:
        if '/' not in llm_model_name:
            raise ValueError(f"Model name '{llm_model_name}' must be in the format 'provider/model_name'.")

        tools = tools or []
        user_prompt = self._prepare_prompt(prompt, file)
        fallback_models = self._build_fallback_chain(llm_model_name, provider, agent_config)

        return await self._execute_with_fallback_async(user_prompt, pydantic_model, fallback_models, tools)

    def _prepare_prompt(self, prompt: str, file):
        if not file:
            return prompt

        file_path = Path(file)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file}")

        return [prompt, BinaryContent(
            data=file_path.read_bytes(),
            media_type=mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
        )]

    def _execute_with_fallback(self, user_prompt, pydantic_model, fallback_models, tools):
        attempted_models, last_error = [], None

        for model_info in fallback_models:

            try:
                model_name, provider = model_info['model'], model_info['provider']
                attempted_models.append(f"{provider}/{model_name}")

                llm_provider = self._get_llm_provider(provider, model_name)
                agent = Agent(llm_provider, output_type=pydantic_model, instrument=True, tools=tools)
                agent_output = agent.run_sync(user_prompt)

                report = self._post_process(agent_output, f"{provider}/{model_name}", provider, pydantic_model.__name__)
                report.attempted_models = attempted_models
                report.fallback_used = len(attempted_models) > 1

                return agent_output.output, report

            except Exception as e:
                last_error = e
                print(f"Model {model_info['model']} failed: {str(e)}")
                continue

        raise Exception(f"All fallback models failed. Attempted: {attempted_models}. Last error: {str(last_error)}")

    async def _execute_with_fallback_async(self, user_prompt, pydantic_model, fallback_models, tools):
        attempted_models, last_error = [], None

        for model_info in fallback_models:
            try:
                model_name, provider = model_info['model'], model_info['provider']
                attempted_models.append(f"{provider}/{model_name}")
                llm_provider = self._get_llm_provider(provider, model_name)
                agent = Agent(llm_provider, output_type=pydantic_model, instrument=True, tools=tools)
                agent_output = await agent.run(user_prompt)

                report = self._post_process(agent_output, f"{provider}/{model_name}", provider, pydantic_model.__name__)
                report.attempted_models = attempted_models
                report.fallback_used = len(attempted_models) > 1

                return agent_output.output, report

            except Exception as e:
                last_error = e
                print(f"Model {model_info['model']} failed: {str(e)}")
                continue

        raise Exception(f"All fallback models failed. Attempted: {attempted_models}. Last error: {str(last_error)}")

    def _build_fallback_chain(self, primary_model: str, primary_provider: str, agent_config: dict = None) -> List[dict]:
        # Handle primary model - keep full format for open_router, strip for others
        primary_model_name = primary_model.split('/', 1)[-1] if primary_provider != 'open_router' else primary_model
        fallback_chain = [{'model': primary_model_name, 'provider': primary_provider}]

        # Add agent-specific fallbacks
        if agent_config:
            if 'fallback_model' in agent_config and 'fallback_provider' in agent_config:
                fallback_model = agent_config['fallback_model']
                # Strip provider prefix if present, except for open_router
                if '/' in fallback_model and agent_config['fallback_provider'] != 'open_router':
                    fallback_model = fallback_model.split('/', 1)[-1]
                fallback_chain.append(
                    {'model': fallback_model, 'provider': agent_config['fallback_provider']})

            for fallback in agent_config.get('fallback_chain', []):
                model = fallback['model']
                # Strip provider prefix if present, except for open_router
                if '/' in model and fallback['provider'] != 'open_router':
                    model = model.split('/', 1)[-1]
                fallback_chain.append({'model': model, 'provider': fallback['provider']})

        # Add system fallbacks
        try:
            model = self.config_helper.get_fallback_model()
            provider = self.config_helper.get_fallback_provider()
            fallback_chain.append({'model': model, 'provider': provider})

            fallback_chain.extend([{'model': f.model, 'provider': f.provider}
                                   for f in self.config_helper.get_fallback_chain()])
        except Exception as e:
            print(f"Error loading system fallbacks: {e}")

        # Remove duplicates
        seen, unique_chain = set(), []
        for item in fallback_chain:
            key = f"{item['provider']}/{item['model']}"
            if key not in seen:
                seen.add(key)
                unique_chain.append(item)

        return unique_chain

    def _post_process(self, agent_result: AgentRunResult, model_name: str, provider: str,
                      pydantic_model_name: str) -> LLMReport:
        filled_fields = sum(1 for field in agent_result.output.__dict__.values() if field is not None)
        total_fields = len(agent_result.output.__dict__)

        report = LLMReport(
            model_name=model_name,
            usage=agent_result.usage(),
            run_date=datetime.now(),
            run_id=str(uuid.uuid4()),
            cost=self.info_provider.get_cost_info(model_name, agent_result.usage()),
            fill_percentage=int((filled_fields / total_fields) * 100)
        )

        self.usage_tracker.add_usage(report, provider, model_name, pydantic_model_name,
                                     self._extract_tool_names(agent_result))
        return report

    def _extract_tool_names(self, agent_run_result: AgentRunResult) -> List[str]:
        if not hasattr(agent_run_result, 'all_messages') or not callable(agent_run_result.all_messages):
            print("Warning: agent_run_result.all_messages() not available.")
            return []

        tool_names = []
        for message in agent_run_result.all_messages() or []:
            if isinstance(message, ModelResponse):
                tool_names.extend(part.tool_name for part in message.parts if isinstance(part, ToolCallPart))
        return tool_names

    def _get_llm_provider(self, name: str, model_name: str) -> Any:
        if name not in self.providers:
            raise ValueError(f"Unknown provider: {name}")

        model_class, provider_class, env_key = self.providers[name]

        # Handle model name formatting
        # if name == 'open_router' and not self.info_provider.get_model_info(model_name):
        #     raise ValueError(f"Unknown model: {model_name}")

        return model_class(model_name, provider=provider_class(api_key=os.getenv(env_key)))
