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

        self.name = self.config.get('name', agent_name)
        self.system_prompt = self.config.get('system_prompt', '')
        self.default_model = self.config.get('default_model')

        self.fallback_chain = self.config.get('fallback_chain', [])

    def _load_config(self, agent_name: str, config_override: Optional[Dict] = None) -> Dict:
        """Load agent configuration from YAML file with override support"""

        try:
            base_path = Path(__file__).parent.parent
            config_path = base_path / "implementations" / agent_name / "config.yaml"

            if not config_path.exists():
                print(f"Warning: Config file not found for agent '{agent_name}' at {config_path}")
                return {}

            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}

            if config_override:
                config.update(config_override)

            return config
        except Exception as e:
            print(f"CRITICAL ERROR loading config for '{agent_name}': {e}")
            return {}

    async def run(self, prompt: str, pydantic_model: Type[T],
                  model_name: Optional[str] = None, file_path: Optional[Union[str, Path]] = None,
                  **kwargs) -> T:
        llm_model_name = model_name or self.default_model

        if self.system_prompt:
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        agent_config = {'fallback_chain': self.fallback_chain}

        result, report = await self.ai_helper.get_result_async(
            prompt=full_prompt,
            pydantic_model=pydantic_model,
            llm_model_name=llm_model_name,
            file=file_path,
            agent_config=agent_config,
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