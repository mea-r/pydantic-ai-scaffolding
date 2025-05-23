from pydantic import BaseModel
from typing import Optional

class GeneralExampleModel(BaseModel):
    content: Optional[str] = None
    extracted_data: Optional[dict] = None
    key: Optional[str] = None
    value: Optional[str] = None

