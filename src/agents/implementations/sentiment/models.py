from pydantic import Field
from enum import Enum

from py_models.base import BasePyModel

class SentimentLabel(str, Enum):
    """Enumeration for the possible sentiment labels."""
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"

class SentimentModel(BasePyModel):
    """Model for sentiment analysis output"""
    sentiment: SentimentLabel = Field(
        ...,
        description="The overall sentiment of the text."
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="A confidence score from 0.0 to 1.0 for the sentiment classification."
    )
    justification: str = Field(
        ...,
        description="A brief, one-sentence explanation for why this sentiment was chosen."
    )