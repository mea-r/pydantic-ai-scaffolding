# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an LLM integration layer built on PydanticAI that provides a flexible framework for interacting with multiple LLM providers (OpenAI, Anthropic, Google, OpenRouter). The project focuses on structured outputs using Pydantic models, tool calling, usage tracking, and cost reporting.

## Commands

### Development Setup
```bash
bash install.sh                    # Set up virtual environment and dependencies
source venv/bin/activate           # Activate virtual environment
```

### Testing
```bash
python -m pytest                   # Run all tests
python -m pytest tests/test_ai_helper.py  # Run specific test file
python -m unittest                 # Alternative test runner
```

### CLI Operations
```bash
python cli.py --simple_test        # Run basic test without tools
python cli.py --test_tools         # Run test with tool calling
python cli.py --test_file          # Run test with file analysis
python cli.py --update_non_working # Update non-working models in config
python cli.py --prices             # Print LLM pricing information
python cli.py --usage              # Print usage report
python cli.py --custom             # Run custom code (modify cli.py)
```

## Architecture

### Core Components

**AiHelper (`src/ai_helper.py`)**: Main class that orchestrates LLM interactions. Handles provider selection, request execution, and generates cost/usage reports.

**Pydantic Models (`src/py_models/`)**: Structured output definitions organized by domain (hello_world, weather, file_analysis). Each model includes test data, prompts, and expected outputs.

**Tools (`src/tools/`)**: Callable functions for LLM tool use (calculator, date, weather). Tools extend LLM capabilities beyond text generation.

**Helpers (`src/helpers/`)**: 
- `usage_tracker.py`: Tracks and reports token usage/costs
- `llm_info_provider.py`: Manages model configurations and pricing
- `config_helper.py`: Configuration management utilities

### Request Flow
1. `AiHelper.get_result()` receives prompt, model selection, optional tools, and optional file
2. If file provided: reads binary data, determines MIME type, creates BinaryContent attachment
3. Creates PydanticAI Agent with specified model, tools, and file content
4. Executes request and captures usage metrics
5. Returns structured result + LLMReport with cost/performance data

### Model Organization
Each domain model in `py_models/` follows this structure:
- `model.py`: Pydantic model definition
- `tests/prompts/`: Input prompts for testing
- `tests/sources/`: Source data files
- `tests/expected/`: Expected output examples

## Development Guidelines

- Functions max 200 lines, classes max 700 lines
- Use TDD: write tests before implementation
- Always run tests after changes
- Use provider patterns for LLM/config access
- Get paths from utils, never hardcode
- Search for usage when modifying methods
- API keys in `.env` (copy from `env-example`)