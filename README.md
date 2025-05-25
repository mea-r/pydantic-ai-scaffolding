# AI Helper
/co
This project serves as an LLM integration layer, leveraging Pydantic models and the PydanticAI library for seamless connectivity with various Large Language Models. It provides a flexible framework for interacting with different LLM providers and models, handling tasks such as sending prompts, receiving structured outputs based on Pydantic models, tracking usage, and utilizing tools.

I also have a Python package which will do a comparison between different llm's performance and reliability, comparing expected results to actual results from different llm's. Functionality is partly overlapping with thi ai-helper implementation. You can find it from here:  https://github.com/madviking/pydantic-llm-tester. 

Want to see how token usage for the exact same task compare? **example_report.txt** contains a report comparing the token usage of different LLMs for the same task.

Pricing information and a list of models that work properly with PydanticAI tool calling: **llm_prices.txt**.

## Keywords
Pydantic, PydanticAI, OpenRouter, LLM testing, LLM integrations, LLM helpers

## Features

- **Multi-Provider Support:** Integrate with various LLM providers like OpenAI, Anthropic, Google, and OpenRouter.
- **Pydantic Model Integration:** Define the structure of expected LLM outputs using Pydantic models for reliable and type-safe data handling.
- **Tool Calling:** Utilize tools within LLM interactions to extend capabilities (e.g., calculator, weather).
- **Usage Tracking:** Monitor and report LLM usage and associated costs.
- **Command-Line Interface:** Interact with the AI Helper for testing, usage reporting, and model management.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd ai-helper
    ```
2.  **Run the installation script:**
    ```bash
    bash install.sh
    ```
    This script sets up a virtual environment and installs the necessary dependencies.
3.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```
4.  **Configure API Keys:**
    Copy the `.env-example` file to `.env` and add your API keys for the desired LLM providers.
    ```bash
    cp .env-example .env
    ```
    Edit the `.env` file:
    ```
    OPENAI_API_KEY=your_openai_key
    ANTHROPIC_API_KEY=your_anthropic_key
    GOOGLE_API_KEY=your_google_key
    OPEN_ROUTER_API_KEY=your_openrouter_key
    ```

## Usage

There are few useful command-line (`cli.py`) functionalities. Ensure your virtual environment is activated (`source venv/bin/activate`) before running the commands. Code in cli.py also serves as an example on how to use the AiHelper in your own project.

-   **Run a simple test case (without tool calling):**
    ```bash
    python cli.py --simple_test
    ```
-   **Run a test case with tool calling:**
    ```bash
    python cli.py --test_tools
    ```
-   **Update non-working models in the config file:**
    ```bash
    python cli.py --update_non_working
    ```
-   **Update and print the price list for models:**
    ```bash
    python cli.py --prices
    ```
-   **Print a usage report:**
    ```bash
    python cli.py --get_usage
    ```
-   **Run your custom code:**
    Modify the `if args.custom is not None:` block in `cli.py` and run:
    ```bash
    python cli.py --custom
    ```

## Project Structure

-   `src/ai_helper.py`: Contains the core `AiHelper` class for interacting with LLMs.
-   `cli.py`: Provides the command-line interface for the project.
-   `requirements.txt`: Lists the project's dependencies.
-   `models.json`: Configuration for various LLM models and their providers.
-   `src/adapters/`: Contains modules for different LLM provider integrations.
-   `src/py_models/`: Contains Pydantic models used for structured LLM outputs.
-   `src/tools/`: Contains definitions for tools that LLMs can utilize.
-   `tests/`: Contains test files for various components of the project.
-   `install.sh`: Script for setting up the project environment.

## Guidelines for Implementation

-   No function should be longer than 200 lines.
-   No class should be longer than 700 lines.
-   Feel free to create new files to make things more modular.
-   `.env` contains the credentials. `env-example` is provided.
-   ALWAYS write tests before implementing. TDD!
-   ALWAYS stop for approval after creating the tests.
-   ALWAYS run tests after making changes.
-   ALWAYS rely on providers for getting and modifying the LLM's, Configs, and Pydantic models.
-   PATHS should always be coming from the utils, never hard coded.
-   When changing any methods, ALWAYS search for usages elsewhere.
-   To setup the project, run `install.sh` and then `source venv/bin/activate`.

## Notes about manual implementation vs. LLMs

In the end majority of this helper ended up being implemented by hand, with some LLM assistance.

### Initial brief shared by all LLMs

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
