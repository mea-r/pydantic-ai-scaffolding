### Ai Helper

This is a simple ai helper to connect with openrouter, google, openai and openrouter. Input and output is always a pydantic model. 

Steps:



### Task
Please do a simple implementation with the following structure:

py_models
    pd_reader_model.py
    weather_model.py
tests
    test_integrations.py
    files/
        inputs/
        outputs/
        test.pdf
        test.png

src/
    ai_helper.py                --- main class
    tools.py                    --- two example tools
    adapters/
        anthropic.py                
        google.py
        openai.py
        openrouter.py
    
example.py

