from pydantic import BaseModel
from typing import Optional

class PDReaderModel(BaseModel):
    content: Optional[str] = None
    extracted_data: Optional[dict] = None
