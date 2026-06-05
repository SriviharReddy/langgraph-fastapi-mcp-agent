from pydantic import BaseModel, Field
from typing import Annotated, Optional


class ChatRequest(BaseModel):
    message: Annotated[str, Field(..., min_length=1, max_length=32000)]
    thread_id: Annotated[Optional[str], Field(default=None)]
