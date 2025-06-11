"""Agents package - Multi-agent system for AI workflows"""

from .base import AgentBase
from .registry import AgentRegistry, get_registry
from .implementations import (
    FileProcessorAgent, ProcessedFileContent,
    TextEditorAgent, EditedContent,
    FeedbackAgent, EditingFeedback
)
from .workflows import BaseWorkflow, ContentEditingWorkflow, SentimentWorkflow

# Agents are auto-discovered when registry is first accessed

__all__ = [
    # Base classes
    'AgentBase',
    
    # Registry
    'AgentRegistry', 'get_registry',
    
    # Agent implementations
    'FileProcessorAgent', 'ProcessedFileContent',
    'TextEditorAgent', 'EditedContent', 
    'FeedbackAgent', 'EditingFeedback',
    
    # Workflows
    'BaseWorkflow', 'ContentEditingWorkflow'
]