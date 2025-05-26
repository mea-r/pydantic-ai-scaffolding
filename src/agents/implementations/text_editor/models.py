"""Pydantic models for text editor agent"""
from pydantic import BaseModel
from typing import List


class EditedContent(BaseModel):
    """Model for edited content output"""
    edited_text: str
    changes_made: List[str]
    editing_rationale: str
    confidence_score: float