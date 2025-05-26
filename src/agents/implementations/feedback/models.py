"""Pydantic models for feedback agent"""
from pydantic import BaseModel
from typing import List

from py_models.base import BasePyModel


class EditingFeedback(BasePyModel):
    """Model for editing feedback output"""
    overall_assessment: str
    specific_feedback: List[str]
    suggestions: List[str]
    quality_score: float
    areas_for_improvement: List[str]
