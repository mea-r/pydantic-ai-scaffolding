"""Pydantic models for feedback agent"""
from pydantic import BaseModel
from typing import List


class EditingFeedback(BaseModel):
    """Model for editing feedback output"""
    overall_assessment: str
    specific_feedback: List[str]
    suggestions: List[str]
    quality_score: float
    areas_for_improvement: List[str]