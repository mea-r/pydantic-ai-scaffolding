"""
Testing suite for the AIHelper class.
"""


ai_helper = AIHelper('openrouter:gpt-3.5-turbo')
ai_helper.add_tool("calculator", "A simple calculator that can add, subtract, multiply, and divide.")
ai_helper.add_tool("weather", "A tool to get the current weather information.")
result = ai_helper.ask("What is the weather like today?", tools=["weather"], model=WeatherModel)

# result should be a WeatherModel object
print(result)

ai_helper = AIHelper('openrouter:gpt-3.5-turbo')
result = ai_helper.ask("Please read this PDF and summarize it.", tools=["pdf_reader"], model=PDFReaderModel, file="files/example.pdf")

# result should be a PDFReaderModel object
print(result)