# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an LLM integration framework built on PydanticAI that provides structured interactions with multiple LLM providers (OpenAI, Anthropic, Google, OpenRouter). The project supports two main paradigms:

1. **Direct LLM Integration**: Core `AiHelper` class for simple, structured LLM interactions
2. **Agent System**: Sophisticated agentic workflows for complex document processing (especially CV/resume processing)

## Commands

### Development Setup
```bash
bash install.sh                    # Set up virtual environment and dependencies
source venv/bin/activate           # Activate virtual environment
cp env-example .env               # Copy environment template
# Edit .env with your API keys
```

### Testing
```bash
python -m pytest                   # Run all tests
python -m pytest tests/test_ai_helper.py  # Run specific test file
python -m unittest                 # Alternative test runner
```

### CLI Operations
```bash
# Basic testing
python cli.py --simple_test        # Basic test without tools
python cli.py --test_tools         # Test with tool calling
python cli.py --test_file          # Test file analysis
python cli.py --test_agent         # Test agent functionality

# Configuration management
python cli.py --update_non_working # Update non-working models in config
python cli.py --test_file_capability # Test and update file-capable models

# Reporting
python cli.py --prices             # Print LLM pricing information
python cli.py --usage              # Print usage report
python cli.py --usage_save         # Save usage report to file

# CV Processing (Agent System)
python cli.py --process_cv <cv_file_path> [email_file_path]

# Debug mode
python cli.py --vv <command>       # Enable verbose debug logging
```

## Architecture

### Core Components

**AiHelper (`src/ai_helper.py`)**: Primary LLM interface handling provider selection, request execution, usage tracking, and fallback mechanisms. Supports file attachments and tool calling.

**Agent System (`src/agents/`)**: 
- `AgentBase`: Foundation class with configuration management and fallback support
- `AgentRegistry`: Dynamic agent discovery and instantiation
- Specialized agents for CV processing, text editing, file processing, feedback, etc.
- YAML-based configuration for agents and workflows

**Models & Data (`src/py_models/`)**: Pydantic models organized by domain with test data, prompts, and expected outputs. Each model includes structured test cases.

**Tools (`src/tools/`)**: Callable functions extending LLM capabilities (calculator, date, weather). Tools are automatically integrated into agent contexts.

**Helpers (`src/helpers/`)**: 
- `usage_tracker.py`: Comprehensive token usage and cost tracking
- `llm_info_provider.py`: Model configuration, pricing, and capability management
- `config_helper.py`: Configuration utilities and validation

### Request Flow

**Direct AiHelper Flow:**
1. `AiHelper.get_result()` processes prompt, model selection, tools, and optional file
2. File handling: binary data extraction, MIME type detection, BinaryContent creation
3. PydanticAI Agent creation with model, tools, and attachments
4. Request execution with usage capture and fallback handling
5. Returns structured result + LLMReport with metrics

**Agent Workflow Flow:**
1. Agent discovery via `AgentRegistry.get_agent()`
2. Configuration loading from `agents/config/agents.yaml`
3. Workflow execution via `BaseWorkflow` with step-by-step processing
4. Quality validation and iterative improvement
5. Comprehensive reporting and forensics logging

### Agent Configuration

Agents are configured in `src/agents/config/agents.yaml` with:
- Default and fallback models/providers
- System prompts and capabilities
- Fallback chains for reliability
- Quality thresholds and validation rules

Workflows are defined in `src/agents/config/workflows.yaml` with agent sequences and quality requirements.

### Model Organization

Domain models in `py_models/` follow this structure:
- `model.py`: Pydantic model definition
- `tests/prompts/`: Input prompts for testing
- `tests/sources/`: Source data files
- `tests/expected/`: Expected output examples

## Development Guidelines

- Functions max 200 lines, classes max 700 lines
- Use TDD: write tests before implementation
- Run tests after changes: `python -m pytest`
- Use provider patterns for LLM/config access
- Get paths from utils, never hardcode
- Search for usage when modifying methods
- API keys in `.env` (copy from `env-example`)
- Use `--vv` flag for debug logging to `logs/forensics.log`

## Key Patterns

**Fallback Strategy**: All agents and core AiHelper support comprehensive fallback chains to ensure reliability across different LLM providers.

**Configuration-Driven**: Agent behavior, model selection, and workflow orchestration are externally configurable via YAML files.

**Usage Tracking**: All LLM interactions are automatically tracked for cost analysis and optimization.

**File Processing**: Robust file handling with MIME type detection and multi-modal LLM support for document analysis.