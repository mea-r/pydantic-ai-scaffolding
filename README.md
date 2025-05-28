# AI Helper
This project is a comprehensive LLM integration framework built on PydanticAI, providing two complementary paradigms:

1. **Core LLM Integration**: Direct, structured interactions with multiple LLM providers (OpenAI, Anthropic, Google, OpenRouter) using Pydantic models for type-safe outputs
2. **Agent System**: Sophisticated agentic workflows for complex document processing, especially CV/resume analysis and content editing

The framework handles provider abstraction, fallback strategies, usage tracking, tool calling, and multi-modal file processing.

I also have a Python package which will do a comparison between different llm's performance and reliability, comparing expected results to actual results from different llm's. Functionality is partly overlapping with thi ai-helper implementation. You can find it from here:  https://github.com/madviking/pydantic-llm-tester. 

Want to see how token usage for the exact same task compare? **example_report.txt** contains a report comparing the token usage of different LLMs for the same task.

Pricing information and a list of models that work properly with PydanticAI tool calling: **llm_prices.txt**.

## Keywords
Pydantic, PydanticAI, OpenRouter, LLM testing, LLM integrations, LLM helpers

## Features

### Core LLM Integration
- **Multi-Provider Support:** Seamless integration with OpenAI, Anthropic, Google, and OpenRouter
- **Pydantic Model Integration:** Type-safe, structured outputs with automatic validation
- **Fallback Strategies:** Comprehensive model/provider fallback chains for reliability
- **File Processing:** Multi-modal support for PDFs, images, and documents with MIME type detection
- **Tool Calling:** Extensible tool system (calculator, weather, date utilities)
- **Usage Tracking:** Comprehensive cost monitoring and performance analytics

### Agent System
- **Specialized Agents:** Domain-specific agents for CV processing, text editing, file analysis, and quality assurance
- **Workflow Orchestration:** Multi-step agentic workflows with quality validation
- **Configuration-Driven:** YAML-based agent and workflow configuration
- **Quality Validation:** Automated quality thresholds and iterative improvement
- **CV Processing Pipeline:** Complete CV analysis, anonymization, formatting, and quality assurance
- **Debug & Forensics:** Detailed logging and debugging capabilities for workflow analysis

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

### Core Testing & Management
-   **Basic functionality tests:**
    ```bash
    python cli.py --simple_test        # Basic test without tools
    python cli.py --test_tools         # Test with tool calling
    python cli.py --test_file          # Test file analysis
    python cli.py --test_agent         # Test agent functionality
    ```

-   **Model and configuration management:**
    ```bash
    python cli.py --update_non_working # Update non-working models
    python cli.py --test_file_capability # Test file processing capabilities
    python cli.py --prices             # Display LLM pricing information
    python cli.py --usage              # Print usage report
    python cli.py --usage_save         # Save usage report to file
    ```

### Agent System & CV Processing
-   **CV processing with agentic workflow:**
    ```bash
    # Process CV with optional email integration
    python cli.py --process_cv <cv_file_path> [email_file_path]
    
    # Enable detailed debug logging
    python cli.py --vv --process_cv <cv_file_path>
    ```

-   **Advanced testing:**
    ```bash
    python cli.py --test_tools all     # Test all models with tool calling
    python cli.py --test_file all      # Test file processing with all models
    python cli.py --test_fallback      # Test fallback functionality
    ```

-   **Custom development:**
    ```bash
    python cli.py --custom             # Run custom code (modify cli.py)
    ```

## Project Structure

### Core Components
-   `src/ai_helper.py`: Core `AiHelper` class for direct LLM interactions
-   `cli.py`: Comprehensive command-line interface for testing and operations
-   `src/py_models/`: Pydantic models organized by domain with test data and prompts
-   `src/tools/`: Tool definitions for extending LLM capabilities
-   `src/helpers/`: Utilities for usage tracking, configuration, and model management

### Agent System
-   `src/agents/base/`: Base classes for agent implementation
-   `src/agents/implementations/`: Specialized agents for different tasks
   - `cv_analysis/`: CV data extraction and parsing
   - `cv_anonymization/`: Personal information anonymization and content enhancement
   - `cv_formatting/`: HTML formatting for CV descriptions
   - `cv_quality/`: Quality validation and metrics
   - `email_integration/`: Email content integration with CV data
   - `text_editor/`: General text editing and improvement
   - `file_processor/`: Multi-modal file content extraction
   - `feedback/`: Editorial feedback and quality assessment
-   `src/agents/config/`: YAML configuration for agents and workflows
-   `src/agents/registry/`: Dynamic agent discovery and management
-   `src/agents/workflows/`: Multi-step workflow orchestration

### Configuration & Documentation
-   `models.json`: LLM model configurations and provider mappings
-   `docs/`: Comprehensive documentation for agents, models, and tools
-   `logs/`: Usage tracking and debug/forensics logging
-   `tests/`: Test suite covering core functionality and integrations

## Development Guidelines

### Code Quality Standards
-   Functions max 200 lines, classes max 700 lines
-   Maintain modular design with clear separation of concerns
-   Follow TDD: write tests before implementation
-   Run tests after making changes: `python -m pytest`
-   Search for usage when modifying methods to ensure compatibility

### Configuration & Security
-   API keys in `.env` (copy from `env-example`)
-   Use provider patterns for LLM/config access, never direct instantiation
-   Get paths from utilities, never hardcode file paths
-   Leverage configuration files for agent and workflow behavior

### Agent Development
-   All agents inherit from `AgentBase` with YAML configuration
-   Use structured outputs with Pydantic models
-   Implement comprehensive fallback strategies
-   Include quality thresholds and validation logic
-   Support both text and file-based inputs
-   Add debug logging with `--vv` flag for troubleshooting

### Testing & Debugging
-   Use `python cli.py --test_agent` for agent functionality testing
-   Enable debug mode with `--vv` flag for detailed forensics logging
-   Test with multiple models using `all` parameter
-   Validate fallback behavior with `--test_fallback`

## Notes about manual implementation vs. LLMs

This project started as a real life experiment to new Opus 4 model. I provided the initial scaffolding and brief:
**https://github.com/madviking/ai-helper/tree/start/initial-brief**

And then tried to get llm's to implement based on the briefing and some followup prompting. If you are interested to see how something like this evolves in the hands of different LLM's, you can check out the branches below. I also did a manual implementation of the same functionality, which is available in the `feature/ai-helper-core` branch. This then later became the main branch.

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

This project demonstrates evolutionary architecture where the initial adapter-based design was simplified thanks to PydanticAI's robust functionality. The current dual-paradigm approach emerged organically:

1. **Core Integration**: Started as simple LLM wrapper, evolved into comprehensive provider abstraction
2. **Agent System**: Added for complex workflows, now supports sophisticated CV processing pipelines
3. **Configuration-Driven**: Moved from hardcoded behavior to YAML-based agent and workflow configuration
4. **Quality Focus**: Integrated comprehensive validation, fallback strategies, and metrics collection

Note: this is by no means a fully objective test, but more of a real life scenario where the LLM's were given the same task. I didn't run them until the end, as I felt that the indication of performance of different LLM's was good enough from the progress. Prompts, costs etc. are documented in the readme files of the respective branches.

### Current Capabilities

The framework now supports production-ready workflows including:
- **Complete CV Processing**: From raw PDF to anonymized, formatted, validated output
- **Multi-Modal Analysis**: Vision-capable models for document and image processing  
- **Quality Assurance**: Automated validation with configurable thresholds
- **Cost Optimization**: Intelligent model selection and fallback strategies
- **Debug & Monitoring**: Comprehensive logging and usage analytics

### Performance & Reliability

The system emphasizes reliability through multiple fallback layers, comprehensive error handling, and quality validation. Token usage and costs are tracked for optimization, with detailed reporting available via the CLI.

## License

MIT
