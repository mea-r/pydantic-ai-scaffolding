import os
from typing import Dict, Any

import requests
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

load_dotenv()

def calculator(expression: str) -> float:
    """A simple calculator that can add, subtract, multiply, and divide."""
    try:
        # Use eval safely for mathematical expressions only
        # Remove any non-mathematical characters for safety
        allowed_chars = "0123456789+-*/()., "
        cleaned_expr = ''.join(c for c in expression if c in allowed_chars)

        # Evaluate the expression
        result = eval(cleaned_expr)
        return float(result)
    except Exception as e:
        raise Exception(f"Invalid expression: {expression}. Error: {str(e)}")
