"""Pydantic models for text editor agent"""
from pydantic import BaseModel
from typing import List

from py_models.base import BasePyModel


class EditedContent(BasePyModel):
    """Model for edited content output"""
    edited_text: str
    changes_made: List[str]
    editing_rationale: str
    confidence_score: float
