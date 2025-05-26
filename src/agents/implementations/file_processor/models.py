"""Pydantic models for file processor agent"""
from pydantic import BaseModel
from typing import List

from py_models.base import BasePyModel


class ProcessedFileContent(BasePyModel):
    """Model for processed file content output"""
    extracted_text: str
    file_type: str
    summary: str
    key_points: List[str]
