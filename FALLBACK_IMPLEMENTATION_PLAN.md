# Fallback Provider Support Implementation Plan

## Overview
This document outlines the implementation plan for adding fallback provider support to the AI Helper framework. The goal is to provide automatic failover capabilities when primary models fail, at both agent-level and system-wide levels.

## Current Architecture Analysis

### Key Integration Points:
1. **AiHelper.get_result()** (`src/ai_helper.py:49-78`): Main request processing method
2. **Agent Configuration** (`src/agents/config/agents.yaml`): Agent-specific model settings
3. **Config Management** (`src/helpers/config_helper.py`): System-wide configuration
4. **AgentBase.run()** (`src/agents/base/agent_base.py:38-63`): Agent execution logic

### Current Flow:
1. Request comes to `AiHelper.get_result()` with model/provider parameters
2. `_get_llm_provider()` creates the appropriate provider instance
3. PydanticAI Agent executes the request
4. Results are post-processed for usage tracking and cost calculation

## Proposed Fallback Design

### 1. Configuration Structure

#### System-Level Fallbacks (config.json):
```json
{
  "defaults": {
    "model": "open_router:mistralai/mistral-7b-instruct:free",
    "fallback_model": "open_router:openai/gpt-3.5-turbo"
  },
  "fallback_chain": [
    "open_router:openai/gpt-4o-mini",
    "anthropic:claude-3-haiku",
    "google:gemini-2.0-flash-001"
  ]
}
```

#### Agent-Level Fallbacks (agents.yaml):
```yaml
agents:
  file_processor:
    default_model: "google/gemini-2.5-pro-preview-03-25"
    default_provider: "google"
    fallback_model: "openai/gpt-4o"
    fallback_provider: "openai"
    fallback_chain:
      - model: "anthropic/claude-3-5-sonnet"
        provider: "anthropic"
      - model: "openai/gpt-4o-mini"
        provider: "openai"
```

### 2. Fallback Logic Flow

```
1. Try primary model (agent-specific or user-specified)
   ↓ (on failure)
2. Try agent-specific fallback model
   ↓ (on failure) 
3. Try agent fallback chain (if configured)
   ↓ (on failure)
4. Try system-wide fallback model
   ↓ (on failure)
5. Try system-wide fallback chain
   ↓ (on failure)
6. Raise exception with all attempted models
```

### 3. Error Handling Strategy

**Retry Conditions:**
- Model unavailable/rate limited
- Authentication errors 
- Timeout errors
- Provider-specific errors

**No Retry Conditions:**
- Input validation errors
- Pydantic model validation errors
- File not found errors

### 4. Implementation Changes

#### AiHelper Class Updates:
- Add `_execute_with_fallback()` method
- Modify `get_result()` and `get_result_async()` to use fallback logic
- Update `_post_process()` to track fallback usage

#### Configuration Updates:
- Extend `Config` class in `config_helper.py`
- Add fallback parsing methods
- Update agent configuration loading

#### Usage Tracking:
- Track which model actually succeeded
- Record fallback attempts in LLMReport
- Update cost calculations for actual model used

### 5. Benefits

- **Reliability**: Automatic failover prevents complete request failures
- **Cost Optimization**: Can fallback to cheaper models when primary fails
- **Flexibility**: Per-agent and system-wide configuration options
- **Transparency**: Full tracking of fallback attempts and costs

### 6. Backward Compatibility

- Existing configurations continue to work without changes
- Fallback configuration is optional
- Default behavior unchanged when no fallbacks configured

## Next Steps

1. ✅ Architecture analysis complete
2. 🔄 Design configuration structure  
3. ⏳ Implement fallback logic in AiHelper
4. ⏳ Update configuration management
5. ⏳ Add fallback tracking to usage reports
6. ⏳ Write comprehensive tests
7. ⏳ Update CLI for demonstration

## Risk Mitigation

- **Infinite loops**: Limit fallback attempts to prevent cycles
- **Cost explosion**: Track and limit fallback usage 
- **Debugging complexity**: Comprehensive logging of fallback attempts
- **Configuration errors**: Validation of fallback chains at startup