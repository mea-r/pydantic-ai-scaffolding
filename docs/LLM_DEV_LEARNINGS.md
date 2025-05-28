# Notes about manual implementation vs. LLMs
This project started as a real life experiment to new Opus 4 model. I provided the initial scaffolding and brief: https://github.com/madviking/ai-helper/tree/start/initial-brief

And then tried to get llm's to implement based on the briefing and some followup prompting. If you are interested to see how something like this evolves in the hands of different LLM's, you can check out the branches below. I also did a manual implementation of the same functionality, which is available in the feature/ai-helper-core branch. This then later became the main branch.

#### Initial brief shared by all LLMs
https://github.com/madviking/ai-helper/tree/start/initial-brief

#### Grok-3
https://github.com/madviking/ai-helper/tree/start/grok-3

#### Claude Opus 4
https://github.com/madviking/ai-helper/tree/start/claude-opus-4

#### Gemini 2.5 Pro
https://github.com/madviking/ai-helper/tree/start/gemini-2-5-pro

#### Jules (jules.google.com)
https://github.com/madviking/ai-helper/tree/feature/ai-helper-core

This project works as a good (or a bad) example on how architecture is evolutionary. Initially planned adapter implementation was unnecessary due to PydanticAI providing such good functionality. However, as PydanticAI is fairly new as a library, none of the tested LLM's had a full understanding of its workings.

Note: this is by no means a fully objective test, but more of a real life scenario where the LLM's were given the same task. I didn't run them until the end, as I felt that the indication of performance of different LLM's was good enough from the progress. Prompts, costs etc. are documented in the readme files of the respective branches.

About usage of time
Funnily enough, the manual implementation didn't end up taking more than maybe 2 x of the time I spent with any of the LLM's.

