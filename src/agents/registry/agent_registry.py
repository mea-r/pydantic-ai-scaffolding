"""Agent registry for dynamic discovery and loading"""
import importlib
from typing import Dict, Type, List, Optional
from pathlib import Path
import yaml

from ..base.agent_base import AgentBase


class AgentRegistry:
    """Registry for managing and discovering agents"""
    
    def __init__(self):
        self._agents: Dict[str, Type[AgentBase]] = {}
        self._config = self._load_registry_config()
        
    def _load_registry_config(self) -> Dict:
        """Load registry configuration from config files in implementation directories"""
        current_dir = Path(__file__).parent.parent
        agents_config = {}
        
        # Load from config.yaml files in each implementation directory
        implementations_dir = current_dir / "implementations"
        if implementations_dir.exists():
            for agent_dir in implementations_dir.iterdir():
                if agent_dir.is_dir() and not agent_dir.name.startswith('_'):
                    config_file = agent_dir / "config.yaml"
                    if config_file.exists():
                        try:
                            with open(config_file, 'r') as f:
                                agent_config = yaml.safe_load(f)
                                agents_config[agent_dir.name] = agent_config
                        except Exception as e:
                            print(f"Error loading agent config {config_file}: {e}")
        
        # Fallback to centralized config files for backwards compatibility
        if not agents_config:
            # Try centralized agents directory first
            agents_dir = current_dir / "config" / "agents"
            if agents_dir.exists():
                for yaml_file in agents_dir.glob("*.yaml"):
                    agent_name = yaml_file.stem
                    try:
                        with open(yaml_file, 'r') as f:
                            agent_config = yaml.safe_load(f)
                            agents_config[agent_name] = agent_config
                    except Exception as e:
                        print(f"Error loading agent config {yaml_file}: {e}")
            
            # Final fallback to monolithic config file
            if not agents_config:
                config_path = current_dir / "config" / "agents.yaml"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        full_config = yaml.safe_load(f)
                        agents_config = full_config.get("agents", {})
        
        return {"agents": agents_config}
    
    def register_agent(self, name: str, agent_class: Type[AgentBase]):
        """Register an agent class"""
        self._agents[name] = agent_class

        
    def get_agent_class(self, name: str) -> Optional[Type[AgentBase]]:
        """Get agent class by name"""
        return self._agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self._agents.keys())
    
    def auto_discover_agents(self):
        """Automatically discover and register agents from implementations directory"""
        # Get the absolute path to the implementations directory
        current_dir = Path(__file__).parent.parent
        implementations_dir = current_dir / "implementations"
        
        if not implementations_dir.exists():
            return
            
        for agent_dir in implementations_dir.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith('_'):
                try:
                    # Try to import the agent module using relative import path
                    module_path = f"src.agents.implementations.{agent_dir.name}.agent"
                    module = importlib.import_module(module_path)
                    
                    # Look for agent class (convention: ends with 'Agent')
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            attr_name.endswith('Agent') and
                            attr_name != 'AgentBase'):
                            
                            agent_name = agent_dir.name
                            self.register_agent(agent_name, attr)
                            break
                            
                except ImportError as e:
                    print(f"Could not import agent from {agent_dir.name}: {e}")
    
    def create_agent(self, name: str, ai_helper, **kwargs):
        """Create an agent instance"""
        agent_class = self.get_agent_class(name)
        if not agent_class:
            raise ValueError(f"Agent '{name}' not found in registry")
        
        return agent_class(ai_helper, name, **kwargs)
    
    def get_agent_info(self, name: str) -> Dict:
        """Get agent configuration and info"""
        return self._config.get("agents", {}).get(name, {})


# Global registry instance
_registry = None

def get_registry():
    """Get the global registry instance (singleton)"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
        _registry.auto_discover_agents()
    return _registry
