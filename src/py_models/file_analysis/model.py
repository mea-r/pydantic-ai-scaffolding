"""
file_analysis model type definition
"""

import os
from typing import ClassVar
from pydantic import Field

from py_models.base import BasePyModel


class FileAnalysisModel(BasePyModel):

    name: ClassVar[str] = "FileAnalysisModel"

    """
    Model for extracting structured information from file analysis
    """

    # Class variables for module configuration
    MODULE_NAME: ClassVar[str] = "file_analysis"
    TEST_DIR: ClassVar[str] = os.path.join(os.path.dirname(__file__), "tests")
    REPORT_DIR: ClassVar[str] = os.path.join(os.path.dirname(__file__), "reports")

    # Define model fields
    text_content: str = Field(..., description="The full text content extracted from the file")
    key: str = Field(..., description="There is a key inside that you are supposed to find")
    value: str = Field(..., description="There is a value inside that you are supposed to find")
3.
