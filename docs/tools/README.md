# Tools Documentation

## Overview

Tools in this system extend LLM capabilities by providing access to external functions and APIs. They enable agents to perform calculations, fetch real-time data, and interact with external services during conversations.

## Tool Architecture

Tools are standalone Python functions that can be called by LLMs during conversation flows. The system uses PydanticAI's tool calling mechanism to provide structured access to these functions.

### Tool Definition Pattern

All tools follow a consistent pattern:

```python
def tool_name(parameter: type, optional_param: type = default) -> return_type:
    """Clear description of what the tool does"""
    try:
        # Tool implementation
        result = perform_operation(parameter)
        return result
    except Exception as e:
        raise Exception(f"Tool error: {str(e)}")
```

**Key Requirements:**
- Descriptive function names starting with tool prefix
- Type hints for all parameters and return values
- Clear docstrings explaining functionality
- Proper error handling with informative messages
- Return structured data when possible

## Available Tools

### Calculator Tool (`src/tools/tool_calculator.py`)

**Purpose**: Performs basic mathematical calculations

**Function**: `calculator(expression: str) -> float`

**Parameters**:
- `expression`: Mathematical expression as string (supports +, -, *, /, parentheses)

**Returns**: Calculated result as float

**Example Usage**:
```python
result = calculator("(15 + 25) * 2 / 4")  # Returns 20.0
```

**Security Features**:
- Input sanitization to allow only mathematical characters
- Safe evaluation using restricted character set
- Proper error handling for invalid expressions

### Date Tool (`src/tools/tool_date.py`)

**Purpose**: Provides human-readable current date and time information

**Function**: `tool_get_human_date() -> str`

**Parameters**: None

**Returns**: Human-friendly date string with time context

**Example Output**:
- "Today on 15th of March, Monday morning"
- "Wednesday on 3rd of April, Tuesday afternoon"

**Features**:
- Ordinal suffixes for dates (1st, 2nd, 3rd, 4th)
- Time of day classification (morning, afternoon, evening, night)
- Context-aware day references (Today vs. day name)

### Weather Tool (`src/tools/tool_weather.py`)

**Purpose**: Fetches current weather information for specified locations

**Function**: `tool_get_weather(location: str = 'Sofia, Bulgaria') -> Dict[str, Any]`

**Parameters**:
- `location`: Location string (city, country format preferred)

**Returns**: Dictionary with weather information:
```python
{
    'location': 'Sofia, Bulgaria',
    'temperature': 22.5,
    'conditions': 'Partly cloudy'
}
```

**Configuration**:
- Requires `WEATHER_API_KEY` environment variable
- Uses WeatherAPI.com service
- Default location: Sofia, Bulgaria

**Error Handling**:
- Missing API key detection
- API error response handling
- Network request error handling

## Tool Integration

### With Agents

Agents can use tools by passing them to the `run()` method:

```python
from src.tools.tool_calculator import calculator
from src.tools.tool_weather import tool_get_weather

# In agent implementation
result = await self.run(
    prompt="Calculate the cost and check weather",
    pydantic_model=MyModel,
    tools=[calculator, tool_get_weather]
)
```

### With AiHelper

Tools can be registered globally with AiHelper:

```python
from src.ai_helper import AiHelper
from src.tools import calculator, tool_get_weather

ai_helper = AiHelper()
ai_helper.register_tools([calculator, tool_get_weather])
```

### Tool Discovery

The system can automatically discover tools:

```python
# Auto-discover all tools in src/tools/
import os
import importlib
from pathlib import Path

def discover_tools():
    tools = []
    tools_dir = Path("src/tools")
    
    for file in tools_dir.glob("tool_*.py"):
        module_name = f"src.tools.{file.stem}"
        module = importlib.import_module(module_name)
        
        # Find functions starting with tool_ or matching naming pattern
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                tools.append(attr)
    
    return tools
```

## Creating New Tools

### Step 1: Define the Tool Function

Create a new file `src/tools/tool_yourname.py`:

```python
import requests
from typing import Dict, Any, Optional

def tool_your_function(parameter: str, optional_param: int = 0) -> Dict[str, Any]:
    """
    Description of what your tool does.
    
    Args:
        parameter: Description of required parameter
        optional_param: Description of optional parameter
        
    Returns:
        Dictionary containing the tool's output
        
    Raises:
        Exception: When tool operation fails
    """
    try:
        # Validate inputs
        if not parameter:
            raise ValueError("Parameter cannot be empty")
            
        # Perform tool operation
        result = some_operation(parameter)
        
        # Return structured data
        return {
            'status': 'success',
            'data': result,
            'parameter_used': parameter
        }
        
    except Exception as e:
        raise Exception(f"Tool operation failed: {str(e)}")
```

### Step 2: Handle Configuration

For tools requiring external services:

```python
import os
from dotenv import load_dotenv

load_dotenv()

def tool_api_service(query: str) -> Dict[str, Any]:
    """Tool that requires API access"""
    api_key = os.environ.get('YOUR_API_KEY')
    
    if not api_key:
        raise Exception("YOUR_API_KEY environment variable is required")
    
    # Use API key for service calls
    ...
```

### Step 3: Add Error Handling

```python
def tool_with_robust_error_handling(data: str) -> Dict[str, Any]:
    """Tool with comprehensive error handling"""
    try:
        # Validate input
        if not isinstance(data, str):
            raise TypeError(f"Expected string, got {type(data)}")
            
        if len(data) > 1000:
            raise ValueError("Input data too long (max 1000 characters)")
        
        # Process data
        result = process_data(data)
        
        if not result:
            raise RuntimeError("Processing returned empty result")
            
        return {'result': result}
        
    except (TypeError, ValueError) as e:
        # Input validation errors
        raise Exception(f"Invalid input: {str(e)}")
    except RuntimeError as e:
        # Processing errors
        raise Exception(f"Processing error: {str(e)}")
    except Exception as e:
        # Unexpected errors
        raise Exception(f"Unexpected error in tool: {str(e)}")
```

### Step 4: Add to Environment (if needed)

For tools requiring API keys, add to `env-example`:

```bash
# Your Tool Configuration
YOUR_API_KEY=your_api_key_here
YOUR_SERVICE_URL=https://api.yourservice.com
```

### Step 5: Test Your Tool

Create test cases:

```python
# Test basic functionality
def test_your_tool():
    result = tool_your_function("test_input")
    assert result['status'] == 'success'
    assert 'data' in result

# Test error handling
def test_your_tool_error_handling():
    try:
        tool_your_function("")
        assert False, "Should have raised exception"
    except Exception as e:
        assert "cannot be empty" in str(e)
```

## Tool Best Practices

### 1. Input Validation
Always validate inputs before processing:
```python
def tool_example(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("Input cannot be empty or whitespace")
    # Continue processing...
```

### 2. Structured Returns
Return consistent, structured data:
```python
# Good: Structured response
return {
    'success': True,
    'data': result,
    'metadata': {'timestamp': datetime.now()}
}

# Avoid: Raw strings or inconsistent formats
return "Result: " + str(result)
```

### 3. Resource Management
Handle external resources properly:
```python
def tool_with_resources(url: str) -> Dict[str, Any]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return {'data': response.json()}
    except requests.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
```

### 4. Configuration Management
Use environment variables for configuration:
```python
import os
from typing import Optional

def get_config_value(key: str, default: Optional[str] = None) -> str:
    value = os.environ.get(key, default)
    if value is None:
        raise Exception(f"Required configuration {key} not found")
    return value
```

### 5. Documentation
Include comprehensive docstrings:
```python
def tool_example(param1: str, param2: int = 5) -> Dict[str, Any]:
    """
    Brief description of tool purpose.
    
    Longer description explaining what the tool does, when to use it,
    and any important considerations.
    
    Args:
        param1: Description of first parameter, including format requirements
        param2: Description of optional parameter with default behavior
        
    Returns:
        Dictionary containing:
        - 'result': The main output
        - 'metadata': Additional information about the operation
        
    Raises:
        ValueError: When input parameters are invalid
        RuntimeError: When external service is unavailable
        
    Example:
        >>> result = tool_example("input", 10)
        >>> print(result['result'])
        'processed_input'
    """
```

## Usage Tracking

Tools are automatically tracked for usage analytics:
- Call counts per tool
- Daily and monthly summaries
- Integration with cost reporting system

Tool usage appears in usage reports:
```
TOOL USAGE BY NAME (ALL TIME)
+-------------+--------------+
| Tool Name   | Total Calls  |
+-------------+--------------+
| calculator  | 45           |
| tool_get_weather | 23      |
| tool_get_human_date | 12   |
+-------------+--------------+
```

## Performance Considerations

### 1. Caching
For expensive operations, consider caching:
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def tool_expensive_operation(param: str) -> str:
    # Cache results for repeated calls
    return expensive_computation(param)
```

### 2. Timeouts
Set appropriate timeouts for external calls:
```python
def tool_external_api(query: str) -> Dict[str, Any]:
    try:
        response = requests.get(api_url, timeout=5)  # 5 second timeout
        return response.json()
    except requests.Timeout:
        raise Exception("API request timed out")
```

### 3. Rate Limiting
Respect API rate limits:
```python
import time
from datetime import datetime

last_call_time = {}

def tool_rate_limited_api(param: str) -> Dict[str, Any]:
    now = datetime.now()
    if 'last_call' in last_call_time:
        time_diff = (now - last_call_time['last_call']).total_seconds()
        if time_diff < 1.0:  # Minimum 1 second between calls
            time.sleep(1.0 - time_diff)
    
    last_call_time['last_call'] = now
    # Make API call...
```

## Security Considerations

### 1. Input Sanitization
Never execute arbitrary code:
```python
# DANGEROUS - Don't do this
def bad_tool(expression: str) -> Any:
    return eval(expression)  # Can execute arbitrary Python code

# SAFE - Restrict to specific operations
def safe_calculator(expression: str) -> float:
    allowed_chars = "0123456789+-*/()., "
    cleaned = ''.join(c for c in expression if c in allowed_chars)
    return eval(cleaned)  # Only mathematical expressions
```

### 2. Credential Management
Never log or expose sensitive data:
```python
def tool_with_credentials(api_key: str, data: str) -> Dict[str, Any]:
    # Log the operation but not the credentials
    print(f"Processing data of length {len(data)}")  # OK
    print(f"Using API key: {api_key}")  # NEVER DO THIS
    
    try:
        result = api_call(api_key, data)
        return {'success': True, 'data': result}
    except Exception as e:
        # Log error but not sensitive details
        print(f"API call failed: {type(e).__name__}")
        raise
```

### 3. Resource Limits
Prevent resource exhaustion:
```python
def tool_with_limits(data: str) -> Dict[str, Any]:
    # Limit input size
    if len(data) > 10000:
        raise ValueError("Input too large (max 10KB)")
    
    # Limit processing time
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Processing timeout")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        result = long_running_operation(data)
        return {'result': result}
    finally:
        signal.alarm(0)  # Cancel timeout
```

## Troubleshooting

### Common Issues

1. **Tool Not Found**: Ensure function is properly exported and naming follows conventions
2. **Import Errors**: Check dependencies are installed and modules are importable
3. **Configuration Errors**: Verify environment variables are set correctly
4. **API Failures**: Implement proper error handling and fallback mechanisms
5. **Performance Issues**: Add timeouts and consider caching strategies

### Debug Logging

Add logging to tools for debugging:
```python
import logging

logger = logging.getLogger(__name__)

def tool_with_logging(param: str) -> Dict[str, Any]:
    logger.info(f"Tool called with param length: {len(param)}")
    
    try:
        result = process_param(param)
        logger.info(f"Tool completed successfully")
        return {'result': result}
    except Exception as e:
        logger.error(f"Tool failed: {str(e)}")
        raise
```