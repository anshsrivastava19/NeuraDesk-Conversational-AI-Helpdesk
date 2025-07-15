"""
pydantic.py

This module defines Pydantic models and Enums used for validating and managing
query input and output data in the chatbot application.
"""

from pydantic import BaseModel, Field
from enum import Enum


class ModelName(str, Enum):
    """
    Enum representing supported model names for inference.

    Attributes:
        qwen3: Represents the Qwen 3 model (local).
        gpt4o: Represents OpenAI's GPT-4o model.
        gpt4omini: Represents OpenAI's GPT-4o-mini model.
    """
    qwen3 = "qwen3"                                                
    gpt4o = "gpt-4o"   
    gpt4omini = "gpt-4o-mini"                                               


class QueryInput(BaseModel):
    """
    Schema for incoming user query input.

    Attributes:
        question (str): The user's natural language question.
        session_id (str, optional): ID for tracking the conversation session.
        model (ModelName): The selected LLM model for the query.
    """
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName.qwen3)


class QueryResponse(BaseModel):
    """
    Schema for the model's response to a user query.

    Attributes:
        answer (str): The generated answer from the model.
        session_id (str): The session ID to associate the response with the correct conversation.
        model (ModelName): The model used to generate the response.
    """
    answer: str
    session_id: str
    model: ModelName