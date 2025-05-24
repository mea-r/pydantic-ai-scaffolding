### Ai Helper
This is an LLM integration layer which relies heavily on Pydantic models and PydanticAI for LLM connectivity. 

### Activating the environment
Simply run install.sh and then do source venv/bin/activate

#### Guidelines for implementation
- No function should be longer than 200 lines.
- No class should be longer than 700 lines.
- Feel free to create new files to make things more modular.
- .env contains the credentials. env-example is provided.
- ALWAYS write tests before implementing. TDD!
- ALWAYS stop for approval after creating the tests. 
- ALWAYS run tests after making changes.
- ALWAYS rely on providers for getting and modifying the LLM's, Configs, and Pydantic models.
- PATHS should always be coming from the utils, never hard coded.
- When changing any methods, ALWAYS search for usages elsewhere.
- To setup the project, run install.sh and then source venv/bin/activate


## Notes about manual implementation vs. llm's

This project works as a good (or bad) example on how architecture is evolutionary. Initially planned adapter implementation was unnecessary due to PydanticAI providing such good functionality. However, as PydanticAI is fairly new as a library, none of the tested LLM's had a full understanding of its workings. 
