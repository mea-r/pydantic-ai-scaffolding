"""Base classes for all agents"""
from typing import Optional, Union, Dict, TypeVar, Tuple, Any, Type
from pathlib import Path
import yaml
import json

# Import the type from py_models
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from py_models.base import BasePyModel, T


class AgentBase:
    """Base class for all agents with improved configuration management"""

    def __init__(self, ai_helper, agent_name: str, config_override: Optional[Dict] = None):
        self.ai_helper = ai_helper
        self.agent_name = agent_name
        self.config = self._load_config(agent_name, config_override)

    def _load_config(self, agent_name: str, config_override: Optional[Dict] = None) -> Dict:
        """Load agent configuration from YAML file with override support"""
        config_path = Path(f"src/agents/config/agents.yaml")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                all_configs = yaml.safe_load(f)
                config = all_configs.get('agents', {}).get(agent_name, {})
        else:
            config = {}
        
        # Apply any runtime overrides
        if config_override:
            config.update(config_override)
            
        return config

    async def run(self, prompt: str, pydantic_model: Type[T],
                  model_name: Optional[str] = None, file_path: Optional[Union[str, Path]] = None,
                  provider: Optional[str] = None, **kwargs) -> T:
        """Execute agent with given parameters and fallback support"""

        # Use config defaults if not specified
        model_name = model_name or self.config.get('default_model')
        provider = provider or self.config.get('default_provider')
        
        # Add system prompt if configured
        system_prompt = self.config.get('system_prompt', '')
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        # Prepare agent config for fallback support
        agent_config = {}
        if 'fallback_model' in self.config:
            agent_config['fallback_model'] = self.config['fallback_model']
        if 'fallback_provider' in self.config:
            agent_config['fallback_provider'] = self.config['fallback_provider']
        if 'fallback_chain' in self.config:
            agent_config['fallback_chain'] = self.config['fallback_chain']

        result, report = await self.ai_helper.get_result_async(
            prompt=full_prompt,
            pydantic_model=pydantic_model,
            llm_model_name=model_name,
            file=file_path,
            provider=provider,
            agent_config=agent_config if agent_config else None,
            **kwargs
        )

        return result

    def get_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        capabilities = self.config.get('capabilities', [])
        return capability in capabilities

    def get_description(self) -> str:
        """Get agent description"""
        return self.config.get('description', f"Agent: {self.agent_name}")