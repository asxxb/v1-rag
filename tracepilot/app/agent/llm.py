import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict, Any, Callable
from app.config import settings

class MockLLM:
    def __init__(self):
        self.call_count = 0

    def generate(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None) -> Any:
        self.call_count += 1
        return type('obj', (object,), {
            'choices': [type('obj', (object,), {
                'message': type('obj', (object,), {
                    'content': 'This is a mock LLM response indicating the likely root cause is a PaymentClient timeout configuration introduced in a recent deployment.',
                    'tool_calls': None
                })
            })]
        })

def get_llm_client():
    if not settings.llm_api_key or settings.llm_api_key == "your_api_key_here":
        print("WARNING: Using Mock LLM because LLM_API_KEY is not set.")
        return MockLLM()
    
    return OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url
    )
