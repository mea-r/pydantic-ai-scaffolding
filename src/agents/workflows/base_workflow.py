"""Base workflow orchestration"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import yaml
from pathlib import Path

from ..registry.agent_registry import get_registry


class BaseWorkflow(ABC):
    """Base class for all workflows"""
    
    def __init__(self, ai_helper, workflow_name: str):
        self.ai_helper = ai_helper
        self.workflow_name = workflow_name
        self.config = self._load_workflow_config(workflow_name)
        self.agents = {}
        
    def _load_workflow_config(self, workflow_name: str) -> Dict:
        """Load workflow configuration"""
        # Get the absolute path to the config file
        current_dir = Path(__file__).parent.parent
        config_path = current_dir / "config" / "agents.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                all_configs = yaml.safe_load(f)
                return all_configs.get('workflows', {}).get(workflow_name, {})
        return {}
    
    def _initialize_agents(self):
        """Initialize required agents for this workflow"""
        required_agents = self.config.get('agents', [])
        registry = get_registry()
        
        # Debug: Show available agents before creation
        print(f"Debug: Available agents in registry: {registry.list_agents()}")
        print(f"Debug: Required agents: {required_agents}")
        
        for agent_name in required_agents:
            if agent_name not in self.agents:
                try:
                    agent = registry.create_agent(agent_name, self.ai_helper)
                    self.agents[agent_name] = agent
                    print(f"Debug: Successfully created agent '{agent_name}'")
                except Exception as e:
                    print(f"Failed to create agent '{agent_name}': {e}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the workflow - to be implemented by subclasses"""
        pass
    
    def get_config_value(self, key: str, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)