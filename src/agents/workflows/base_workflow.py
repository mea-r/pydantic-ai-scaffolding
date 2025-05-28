"""Base workflow orchestration"""
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
import yaml
import time
import logging
import os
import traceback
from pathlib import Path

from ..registry.agent_registry import get_registry


class BaseWorkflow(ABC):
    """Base class for all workflows with common stage execution and reporting"""
    
    def __init__(self, ai_helper, workflow_name: str):
        self.ai_helper = ai_helper
        self.workflow_name = workflow_name
        self.config = self._load_workflow_config(workflow_name)
        self.agents = {}
        self.processing_report = {
            'stages_completed': [], 
            'processing_time': {}, 
            'quality_metrics': {}, 
            'errors': [], 
            'warnings': []
        }
        self.logger = logging.getLogger('forensics') if os.getenv('AI_HELPER_DEBUG', 'false').lower() == 'true' else None
        
    def _load_workflow_config(self, workflow_name: str) -> Dict:
        """Load workflow configuration from workflows.yaml"""
        current_dir = Path(__file__).parent.parent
        workflows_path = current_dir / "config" / "workflows.yaml"
        
        if workflows_path.exists():
            with open(workflows_path, 'r') as f:
                all_configs = yaml.safe_load(f)
                return all_configs.get('workflows', {}).get(workflow_name, {})
        
        # Fallback to old location for backwards compatibility
        agents_path = current_dir / "config" / "agents.yaml"
        if agents_path.exists():
            with open(agents_path, 'r') as f:
                all_configs = yaml.safe_load(f)
                return all_configs.get('workflows', {}).get(workflow_name, {})
        
        return {}
    
    def _initialize_agents(self):
        """Initialize required agents for this workflow"""
        required_agents = self.config.get('agents', [])
        registry = get_registry()
        
        for agent_name in required_agents:
            if agent_name not in self.agents:
                try:
                    agent = registry.create_agent(agent_name, self.ai_helper)
                    self.agents[agent_name] = agent
                except Exception as e:
                    print(f"Failed to create agent '{agent_name}': {e}")
    
    async def _execute_stage(self, stage_name: str, agent_name: str, method_name: str, 
                           *args, return_full_result: bool = False, **kwargs):
        """Execute a single workflow stage with timing and error handling"""
        stage_start_time = time.time()
        stage_num = len(self.processing_report['stages_completed']) + 1
        print(f"Stage {stage_num}: {stage_name.title().replace('_', ' ')}...")

        try:
            agent = self.agents[agent_name]
            method = getattr(agent, method_name)
            result = await method(*args, **kwargs)

            stage_duration = time.time() - stage_start_time
            self.processing_report['processing_time'][stage_name] = stage_duration
            self.processing_report['stages_completed'].append(stage_name)

            self._log(f"Stage {stage_num} ({stage_name}) completed successfully in {stage_duration:.2f}s", level='info')

            if return_full_result:
                return result
            
            # Try to extract the appropriate data from the result
            if hasattr(result, f"{stage_name.split('_')[0]}_cv_data"):
                return getattr(result, f"{stage_name.split('_')[0]}_cv_data")
            elif hasattr(result, "validated_cv_data"):
                return result.validated_cv_data
            else:
                return result

        except Exception as e:
            stage_duration = time.time() - stage_start_time
            error_msg = f"Stage {stage_num} ({stage_name}) failed after {stage_duration:.2f}s: {str(e)}"
            self._log(error_msg, level='error')
            raise Exception(error_msg) from e

    def _generate_report(self, additional_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate comprehensive processing report"""
        report = {
            'workflow_name': self.workflow_name,
            'stages_executed': self.processing_report['stages_completed'],
            'overall_success': len(self.processing_report['errors']) == 0,
            'errors': self.processing_report['errors'],
            'warnings': self.processing_report['warnings'],
            'processing_time': self.processing_report['processing_time'],
            'total_time': sum(self.processing_report['processing_time'].values())
        }
        
        if additional_data:
            report.update(additional_data)
            
        return report

    def _log(self, message: str, level: str = 'info'):
        """Centralized logging with debug info"""
        if self.logger:
            getattr(self.logger, level)(message)
            if level == 'error':
                self.logger.debug(f"Full traceback: {traceback.format_exc()}")

    async def validate_prerequisites(self, **kwargs) -> Dict[str, Any]:
        """Validate that all prerequisites are met for workflow execution"""
        validation_result = {'valid': True, 'errors': [], 'warnings': []}

        # Check required agents are available
        required_agents = self.config.get('agents', [])
        for agent_name in required_agents:
            if agent_name not in self.agents:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Required agent not available: {agent_name}")

        return validation_result

    def reset_state(self):
        """Reset workflow state for reuse"""
        self.processing_report = {
            'stages_completed': [], 
            'processing_time': {}, 
            'quality_metrics': {}, 
            'errors': [], 
            'warnings': []
        }
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the workflow - to be implemented by subclasses"""
        pass
    
    def get_config_value(self, key: str, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)