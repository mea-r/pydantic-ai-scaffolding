from pydantic import BaseModel, Field

class InspirationModel(BaseModel):
    # pydantic model holds an inspirational quote and i ts author
    quote: str = Field(..., description="The generated inspirational quote.")
    author: str = Field(..., description="The author of the quote. If unknown, should be 'Anonymous'.")