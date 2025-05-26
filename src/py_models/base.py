import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, ClassVar, Type, Set, Tuple, Optional, TypeVar
from pydantic import BaseModel, validator, ValidationError, field_validator, Field
from pydantic_ai.usage import Usage

T = TypeVar('T', bound='BasePyModel')

class LLMReport(BaseModel):
    model_name: str
    run_date: datetime = Field(default_factory=datetime.now)
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    usage: Optional[Usage] = Field(default_factory=Usage)
    cost: float = 0.0
    fill_percentage: int = 0
    fallback_used: bool = False
    attempted_models: List[str] = Field(default_factory=list)

class BasePyModel(BaseModel):
    """
    Base class for all Pydantic LLM Tester py_models.
    Provides common functionality for test case discovery and report saving.
    """

    # Class variable for module name - must be defined by subclasses
    MODULE_NAME: ClassVar[str]

    @classmethod
    def get_skip_fields(cls) -> Set[str]:
        """
        Get a set of field names that should be skipped during validation.
        Can be overridden by subclasses.
        """
        return set()

    # Custom classmethod to create model with field filtering
    @classmethod
    def create_filtered(cls, data: Dict[str, Any]):
        """
        Pre-process the data before validation to exclude fields with type errors
        or fields that are explicitly marked to be skipped.
        """
        if not isinstance(data, dict):
            return data

        # Create a clean copy with only valid fields
        clean_data = {}

        # Get fields to skip
        skip_fields = cls.get_skip_fields()

        for field_name, field_value in data.items():
            # Skip fields that are explicitly defined to be skipped
            if field_name in skip_fields:
                continue

            # Skip fields that don't exist in the model
            if field_name not in cls.model_fields:  # Use __fields__ for Pydantic v1
                continue

            # Add the field to clean data
            clean_data[field_name] = field_value

        # Return a model instance
        return cls(**clean_data)

