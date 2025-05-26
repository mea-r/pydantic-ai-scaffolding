from typing import Any, Optional, Union, TypeVar, Tuple, List
from datetime import datetime
import uuid
import os
import mimetypes
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import ModelResponse, ToolCallPart, BinaryContent
from pydantic_ai.providers.google import GoogleProvider

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from dotenv import load_dotenv
from pydantic_ai.providers.openrouter import OpenRouterProvider

from helpers.llm_info_provider import LLMInfoProvider
from helpers.usage_tracker import UsageTracker
from helpers.config_helper import ConfigHelper, FallbackModel
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
        self.usage_tracker = UsageTracker()
        self.config_helper = ConfigHelper()

    """
    Do the actual request and generate cost report + cost info + save whatever needs to be saved
    """
    def get_result(self, prompt: str, pydantic_model, llm_model_name: str = 'deepseek/deepseek-prover-v2:free', file: Optional[Union[str, Path]] = None, provider='open_router', tools: list = None, agent_config: Optional[dict] = None) -> Tuple[T, LLMReport] | Tuple[None, None]:
        """Execute request with fallback support"""
        
        if '/' not in llm_model_name:
            raise ValueError(f"Model name '{llm_model_name}' must be in the format 'provider/model_name'.")

        if tools is None:
            tools = []

        # Prepare user prompt with optional file attachment
        if file:
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file}")
            
            file_data = file_path.read_bytes()
            media_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
            
            user_prompt = [
                prompt,
                BinaryContent(data=file_data, media_type=media_type)
            ]
        else:
            user_prompt = prompt

        return self._execute_with_fallback(
            user_prompt=user_prompt,
            pydantic_model=pydantic_model,
            primary_model=llm_model_name,
            primary_provider=provider,
            tools=tools,
            agent_config=agent_config
        )

    def _execute_with_fallback(self, user_prompt, pydantic_model, primary_model: str, primary_provider: str, tools: list, agent_config: Optional[dict] = None) -> Tuple[T, LLMReport]:
        """Execute request with fallback logic"""
        
        attempted_models = []
        last_error = None
        
        # Build fallback chain
        fallback_models = self._build_fallback_chain(primary_model, primary_provider, agent_config)
        
        for model_info in fallback_models:
            try:
                model_name, provider = model_info['model'], model_info['provider']
                attempted_models.append(f"{provider}/{model_name}")
                
                llm_provider = self._get_llm_provider(provider, model_name)
                agent = Agent(llm_provider, output_type=pydantic_model, instrument=True, tools=tools)
                agent_output = agent.run_sync(user_prompt)
                result = agent_output.output
                
                # Success! Update report with actual model used and fallback info
                report = self._post_process(agent_output, f"{provider}/{model_name}", provider, pydantic_model.__name__)
                report.attempted_models = attempted_models
                report.fallback_used = len(attempted_models) > 1
                
                return result, report
                
            except Exception as e:
                last_error = e
                print(f"Model {model_info['model']} failed: {str(e)}")
                continue
        
        # All models failed
        raise Exception(f"All fallback models failed. Attempted: {attempted_models}. Last error: {str(last_error)}")

    def _build_fallback_chain(self, primary_model: str, primary_provider: str, agent_config: Optional[dict] = None) -> List[dict]:
        """Build the complete fallback chain for execution"""
        
        fallback_chain = []
        
        # 1. Primary model
        primary_clean = primary_model.split('/', 1)[-1] if '/' in primary_model else primary_model
        fallback_chain.append({'model': primary_clean, 'provider': primary_provider})
        
        # 2. Agent-specific fallbacks (if provided)
        if agent_config:
            if 'fallback_model' in agent_config and 'fallback_provider' in agent_config:
                fallback_chain.append({
                    'model': agent_config['fallback_model'],
                    'provider': agent_config['fallback_provider']
                })
            
            if 'fallback_chain' in agent_config:
                for fallback in agent_config['fallback_chain']:
                    fallback_chain.append(fallback)
        
        # 3. System-wide fallbacks
        system_fallback = self.config_helper.get_fallback_model()
        if system_fallback:
            try:
                provider, model = self.config_helper.parse_model_string(system_fallback)
                fallback_chain.append({'model': model, 'provider': provider})
            except ValueError:
                print(f"Invalid system fallback model format: {system_fallback}")
        
        # 4. System-wide fallback chain
        for fallback_model in self.config_helper.get_fallback_chain():
            fallback_chain.append({
                'model': fallback_model.model,
                'provider': fallback_model.provider
            })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_chain = []
        for item in fallback_chain:
            key = f"{item['provider']}/{item['model']}"
            if key not in seen:
                seen.add(key)
                unique_chain.append(item)
        
        return unique_chain

    async def get_result_async(self, prompt: str, pydantic_model, llm_model_name: str = 'deepseek/deepseek-prover-v2:free', file: Optional[Union[str, Path]] = None, provider='open_router', tools: list = None, agent_config: Optional[dict] = None) -> Tuple[T, LLMReport] | Tuple[None, None]:
        """Async version of get_result with fallback support"""
        
        if '/' not in llm_model_name:
            raise ValueError(f"Model name '{llm_model_name}' must be in the format 'provider/model_name'.")

        if tools is None:
            tools = []

        # Prepare user prompt with optional file attachment
        if file:
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file}")
            
            file_data = file_path.read_bytes()
            media_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
            
            user_prompt = [
                prompt,
                BinaryContent(data=file_data, media_type=media_type)
            ]
        else:
            user_prompt = prompt

        return await self._execute_with_fallback_async(
            user_prompt=user_prompt,
            pydantic_model=pydantic_model,
            primary_model=llm_model_name,
            primary_provider=provider,
            tools=tools,
            agent_config=agent_config
        )

    async def _execute_with_fallback_async(self, user_prompt, pydantic_model, primary_model: str, primary_provider: str, tools: list, agent_config: Optional[dict] = None) -> Tuple[T, LLMReport]:
        """Async version of execute request with fallback logic"""
        
        attempted_models = []
        last_error = None
        
        # Build fallback chain
        fallback_models = self._build_fallback_chain(primary_model, primary_provider, agent_config)
        
        for model_info in fallback_models:
            try:
                model_name, provider = model_info['model'], model_info['provider']
                attempted_models.append(f"{provider}/{model_name}")
                
                llm_provider = self._get_llm_provider(provider, model_name)
                agent = Agent(llm_provider, output_type=pydantic_model, instrument=True, tools=tools)
                agent_output = await agent.run(user_prompt)
                result = agent_output.output
                
                # Success! Update report with actual model used and fallback info
                report = self._post_process(agent_output, f"{provider}/{model_name}", provider, pydantic_model.__name__)
                report.attempted_models = attempted_models
                report.fallback_used = len(attempted_models) > 1
                
                return result, report
                
            except Exception as e:
                last_error = e
                print(f"Model {model_info['model']} failed: {str(e)}")
                continue
        
        # All models failed
        raise Exception(f"All fallback models failed. Attempted: {attempted_models}. Last error: {str(last_error)}")

    """
    Usage data calculation. Save hooks for reporting.
    """
    def _post_process(self, agent_result: AgentRunResult, model_name: str, provider: str, pydantic_model_name: str) -> LLMReport:
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

        self.usage_tracker.add_usage(
            report,
            service=provider,
            model_name=model_name,  # ensure this is the full name like 'openai/gpt-4o'
            pydantic_model_name=pydantic_model_name,
            tool_names_called=self._extract_tool_names(agent_result)
        )

        return report

    def _extract_tool_names(self, agent_run_result: AgentRunResult) -> List[str]:
        """
        Extracts tool names from the agent run result using the all_messages() method.
        This is suitable for pydantic-ai v1.x+.
        """
        tool_names_called: List[str] = []

        if not hasattr(agent_run_result, 'all_messages') or not callable(agent_run_result.all_messages):
            print("Warning: agent_run_result.all_messages() not available. Tool tracking might be using an outdated method or fail.")
            # Consider a fallback to the older history inspection if you need to support multiple pydantic-ai versions
            return []

        messages = agent_run_result.all_messages()
        if not messages:
            return []

        for message_item in messages: # message_item can be ModelRequest or ModelResponse
            if isinstance(message_item, ModelResponse):
                for part in message_item.parts:
                    if isinstance(part, ToolCallPart):
                        tool_names_called.append(part.tool_name)
        return tool_names_called

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

