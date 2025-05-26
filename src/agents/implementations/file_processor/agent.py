"""File processor agent implementation"""
from typing import Union
from pathlib import Path

from ...base.agent_base import AgentBase
from .models import ProcessedFileContent
from .prompts import EXTRACT_CONTENT


class FileProcessorAgent(AgentBase):
    """Agent specialized in processing and extracting content from files"""

    async def process_file(self, file_path: Union[str, Path], **kwargs) -> ProcessedFileContent:
        """Process a file and extract its content"""
        
        result = await self.run(
            prompt=EXTRACT_CONTENT,
            pydantic_model=ProcessedFileContent,
            file_path=file_path,
            **kwargs
        )
        
        return result