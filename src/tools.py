
"""
Tools should follow PydanticAI's tool calling convention.
https://ai.pydantic.dev/api/tools/

Weather api call (WEATHER_API_KEY is in the env):
http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q=Sofia&aqi=no

"""

def calculator(expression: str):
    """A simple calculator that can add, subtract, multiply, and divide."""
    pass

def weather(location: str):
    """A tool to get the current weather information."""
    pass

def pdf_reader(file_path: str):
    """A tool to read and extract information from a PDF file."""
    pass
