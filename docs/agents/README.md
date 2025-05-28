# Agent Development Guide

## Overview

Agents in this system are specialized components that execute specific tasks using LLM capabilities. They provide a layer of abstraction between the raw LLM interface and specific use cases, handling model selection, prompt management, and structured output generation.

## Agent Architecture

### Base Classes

#### AgentBase (`src/agents/base/agent_base.py`)
All agents inherit from `AgentBase` which provides:
- **Configuration Management**: YAML-based configuration with runtime overrides
- **Model Selection**: Primary and fallback model support  
- **Prompt Handling**: System prompt injection and formatting
- **Structured Execution**: Integration with PydanticAI for typed outputs

Key methods:
- `run()`: Execute agent with prompt and return structured result
- `get_capability()`: Check if agent supports specific functionality
- `get_description()`: Get agent description from config

### Agent Registry (`src/agents/registry/agent_registry.py`)

The registry provides dynamic agent discovery and management:
- **Auto-discovery**: Scans `implementations/` directory for agent classes
- **Registration**: Maps agent names to classes
- **Factory Pattern**: Creates agent instances with proper initialization
- **Configuration Access**: Retrieves agent metadata from YAML

## Configuration System

Agents are configured via `src/agents/config/agents.yaml`:

```yaml
agents:
  my_agent:
    name: "My Agent"
    description: "What this agent does"
    default_model: "openai/gpt-4o"
    default_provider: "openai"
    fallback_model: "claude-3-5-sonnet"
    fallback_provider: "anthropic"
    fallback_chain:
      - model: "gpt-4o-mini"
        provider: "openai"
    capabilities:
      - text_processing
      - analysis
    system_prompt: |
      You are a specialized agent that...
```

### Configuration Fields

- **name**: Human-readable agent name
- **description**: Agent purpose and capabilities
- **default_model/provider**: Primary model to use
- **fallback_model/provider**: Secondary model if primary fails
- **fallback_chain**: Multiple fallback options in order
- **capabilities**: List of supported features
- **system_prompt**: Agent-specific instructions

## Current Agents

### CV Processing Agents

#### CVAnalysisAgent (`src/agents/implementations/cv_analysis/`)
**Purpose**: Extracts structured data from CV documents with high accuracy

**Capabilities**:
- Document analysis and vision processing
- Structured data extraction following CVData model
- Skills categorization and experience parsing
- Quality assessment of extraction

**Default Model**: google/gemini-2.5-pro-preview (vision-capable)

#### EmailIntegrationAgent (`src/agents/implementations/email_integration/`)
**Purpose**: Integrates additional information from email communications with CV data

**Capabilities**:
- Email content extraction and analysis
- CV data enhancement without overwriting
- Conflict resolution between CV and email data
- Context-aware information integration

#### CVAnonymizationAgent (`src/agents/implementations/cv_anonymization/`)
**Purpose**: Anonymizes personal information and enhances content quality

**Capabilities**:
- Complete personal information anonymization
- Pronoun replacement (they/them/their)
- Company name anonymization with systematic placeholders
- Grammar and style improvements while preserving technical accuracy

#### CVFormattingAgent (`src/agents/implementations/cv_formatting/`)
**Purpose**: Applies proper HTML formatting to CV description fields

**Capabilities**:
- HTML formatting using allowed tags: `<p>`, `<br>`, `<ul>`, `<li>`, `<strong>`, `<em>`
- Content structuring for improved readability
- Semantic markup validation

#### CVQualityAgent (`src/agents/implementations/cv_quality/`)
**Purpose**: Validates CV processing quality and compliance

**Capabilities**:
- Comprehensive quality validation across multiple dimensions
- Anonymization completeness verification (≥95% threshold)
- HTML formatting compliance checking
- Quality metrics generation and recommendations

### General Purpose Agents

#### TextEditorAgent (`src/agents/implementations/text_editor/`)
**Purpose**: Improves text quality through grammar correction and style enhancement

**Key Methods**:
- `edit_content(content)`: Improve provided text
- `apply_feedback(original, edited, feedback)`: Revise based on feedback

**Output Model**: `EditedContent`
- `edited_text`: Improved content
- `changes_made`: List of modifications
- `editing_rationale`: Explanation of changes
- `confidence_score`: Quality assessment (0-1)

#### FileProcessorAgent (`src/agents/implementations/file_processor/`)
**Purpose**: Extracts and analyzes content from various file types

**Capabilities**: 
- File reading (PDF, images, documents)
- Content extraction and summarization
- Image analysis and description
- Multi-modal content processing

#### FeedbackAgent (`src/agents/implementations/feedback/`)
**Purpose**: Provides editorial feedback and quality assessment

**Capabilities**:
- Comparative analysis of original vs edited content
- Quality scoring and improvement suggestions
- Objective editorial assessment
- Multi-iteration feedback loops

## Agent Lifecycle

1. **Registration**: Registry auto-discovers agents at startup
2. **Configuration**: YAML config loaded and validated
3. **Instantiation**: Agent created with AiHelper reference
4. **Execution**: `run()` method processes requests
5. **Fallback**: If primary model fails, fallbacks attempted

## Error Handling

- **Model Failures**: Automatic fallback to configured alternatives
- **Configuration Errors**: Graceful degradation with defaults
- **Import Errors**: Logged but don't break other agents
- **Validation Errors**: Proper exception propagation

## Integration Points

### With AiHelper
Agents receive an `AiHelper` instance for:
- LLM provider access
- Usage tracking
- Cost reporting
- File handling

### With Pydantic Models
Agents work with structured outputs defined in `src/py_models/`:
- Type safety and validation
- Automatic JSON schema generation
- Test case management

### With Workflows
Agents can be orchestrated in multi-step workflows defined in `workflows.yaml`:
- **CV Processing Workflow**: Complete pipeline from analysis to quality validation
- **Content Editing Workflow**: File processing, editing, and feedback loops
- Sequential execution with fallback handling
- Quality thresholds and validation requirements
- Iterative improvement with max iteration limits
- Comprehensive reporting and metrics

## Best Practices

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Configuration-Driven**: Use YAML config for all behavioral parameters
3. **Structured Outputs**: Always use Pydantic models for responses
4. **Error Resilience**: Implement proper fallback strategies
5. **Testing**: Include test cases for all major functionality
6. **Documentation**: Maintain clear descriptions and examples

## Performance Considerations

- **Model Selection**: Choose appropriate models for task complexity
- **Fallback Strategy**: Balance reliability vs cost in fallback chains
- **Caching**: Consider response caching for repeated operations
- **Resource Management**: Monitor token usage and costs

## Agent Command Line Usage

### CV Processing
```bash
# Process CV with optional email integration
python cli.py --process_cv <cv_file_path> [email_file_path]

# Enable debug logging for detailed forensics
python cli.py --vv --process_cv <cv_file_path>
```

### General Agent Testing
```bash
# Test agent functionality
python cli.py --test_agent

# Test with specific models
python cli.py --test_tools all  # Test all models
python cli.py --test_file all   # Test file processing with all models
```

## See Also

- [Creating New Agents](how-to-create-agents.md)
- [Models Documentation](../models/README.md)
- [Tools Documentation](../tools/README.md)
- [CV Processing Implementation](../../cv-implementation.md)