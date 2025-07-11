from pydantic import BaseModel, Field
from enum import Enum


class ModelName(str, Enum):
    qwen3 = "qwen3"                                                
    gpt4o = "gpt-4o"   
    gpt4omini = "gpt-4o-mini"                                               


class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName.qwen3)


class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName