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
In the end majority of this helper ended up being implemented by hand, with some LLM assistance. 

### Inital brief shared by all LLM's
**https://github.com/madviking/ai-helper/tree/start/initial-brief**

### Grok-3
https://github.com/madviking/ai-helper/tree/start/grok-3

### Claude Opus 4
https://github.com/madviking/ai-helper/tree/start/claude-opus-4

### Gemini 2.5 Pro
https://github.com/madviking/ai-helper/tree/start/gemini-2-5-pro

### Jules (jules.google.com)
https://github.com/madviking/ai-helper/tree/feature/ai-helper-core

This project works as a good (or bad) example on how architecture is evolutionary. Initially planned adapter implementation was unnecessary due to PydanticAI providing such good functionality. However, as PydanticAI is fairly new as a library, none of the tested LLM's had a full understanding of its workings. 

Note: this is by no means a fully objective test, but more of a real life scenario where the LLM's were given the same task. I didn't run them until the end, as I felt that the indication of performance of different LLM's was good enough from the progress. Prompts, costs etc. are documented in the readme files of the respective branches.

### About usage of time
Funnily enough, the manual implementation didn't end up taking more than maybe 2 x of the time I spent with any of the LLM's. 

## License
MIT
