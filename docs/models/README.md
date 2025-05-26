# Pydantic Models Documentation

## Overview

Pydantic models in this system define the structured output formats for LLM interactions. They provide type safety, validation, and automatic JSON schema generation, ensuring consistent and reliable data extraction from language models.

## Model Architecture

### Base Model (`src/py_models/base.py`)

All models inherit from `BasePyModel`, which extends Pydantic's `BaseModel` with additional functionality:

#### Core Features
- **Test Framework Integration**: Automatic test case discovery and execution
- **Report Generation**: Structured output saving and retrieval
- **Field Filtering**: Skip problematic fields during validation
- **Usage Tracking**: Integration with usage reporting system

#### LLMReport Class
Tracks execution metadata for each model run:
```python
class LLMReport(BaseModel):
    model_name: str                    # LLM model used
    run_date: datetime                 # Execution timestamp
    run_id: str                        # Unique identifier
    usage: Optional[Usage]             # Token usage stats
    cost: float                        # Execution cost
    fill_percentage: int               # Model completion rate
    fallback_used: bool                # Whether fallback was triggered
    attempted_models: List[str]        # All models tried
```

### Model Structure

Each domain model follows this directory pattern:
```
src/py_models/{domain}/
├── __init__.py
├── model.py              # Model definition
├── reports/              # Generated outputs
├── tests/
│   ├── expected/         # Expected outputs for validation
│   ├── prompts/          # Test prompts
│   └── sources/          # Input data files
```

## Available Models

### Hello World Model (`src/py_models/hello_world/model.py`)

**Purpose**: Basic sentiment analysis and response detection

**Fields**:
- `message_sentiment: int` - Sentiment score (1-10, negative to positive)
- `expects_response: bool` - Whether the message expects a reply

**Use Cases**:
- Message classification
- Sentiment analysis
- Response requirement detection

**Example Output**:
```json
{
  "message_sentiment": 8,
  "expects_response": true
}
```

### Weather Model (`src/py_models/weather/model.py`)

**Purpose**: Weather information processing and creative reporting

**Fields**:
- `tool_results: Optional[dict]` - Raw tool call results
- `haiku: str` - Creative weather haiku
- `report: str` - Formal weather report

**Use Cases**:
- Weather data processing
- Creative content generation
- Tool integration testing

**Example Output**:
```json
{
  "tool_results": {"temperature": 22.5, "conditions": "Sunny"},
  "haiku": "Bright sun overhead\nWarm breeze whispers through the trees\nPerfect summer day",
  "report": "Current conditions show sunny skies with temperature of 22.5°C"
}
```

### File Analysis Model (`src/py_models/file_analysis/model.py`)

**Purpose**: Structured file content extraction and analysis

**Fields**:
- `text_content: str` - Full extracted text content
- `key: str` - Specific key information to extract
- `value: str` - Corresponding value information

**Use Cases**:
- Document processing
- Key-value extraction
- Content analysis

**Example Output**:
```json
{
  "text_content": "Full document content here...",
  "key": "contract_date",
  "value": "2024-03-15"
}
```

## Creating New Models

### Step 1: Define the Model Structure

Create the directory structure:
```bash
mkdir -p src/py_models/your_domain/{tests/{expected,prompts,sources},reports}
```

### Step 2: Implement the Model Class

Create `src/py_models/your_domain/model.py`:

```python
"""
Your domain model type definition
"""

import os
from typing import List, Optional, ClassVar
from pydantic import Field, validator

from py_models.base import BasePyModel


class YourDomainModel(BasePyModel):
    """
    Model for extracting structured information for your domain
    """
    
    # Class metadata
    name: ClassVar[str] = "YourDomainModel"
    MODULE_NAME: ClassVar[str] = "your_domain"
    TEST_DIR: ClassVar[str] = os.path.join(os.path.dirname(__file__), "tests")
    REPORT_DIR: ClassVar[str] = os.path.join(os.path.dirname(__file__), "reports")

    # Define your fields with descriptions
    primary_field: str = Field(
        ..., 
        description="Main data to extract"
    )
    
    optional_field: Optional[int] = Field(
        default=None,
        description="Optional numeric data",
        ge=0,  # Greater than or equal to 0
        le=100  # Less than or equal to 100
    )
    
    list_field: List[str] = Field(
        default_factory=list,
        description="List of extracted items"
    )
    
    confidence_score: float = Field(
        ...,
        description="Confidence in extraction accuracy (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    @validator('primary_field')
    def validate_primary_field(cls, v):
        """Custom validation for primary field"""
        if not v or not v.strip():
            raise ValueError("Primary field cannot be empty")
        return v.strip()

    @validator('list_field')
    def validate_list_items(cls, v):
        """Ensure list items are valid"""
        return [item.strip() for item in v if item.strip()]
```

### Step 3: Add Field Validation

Use Pydantic's validation features:

```python
from pydantic import Field, validator, root_validator
from typing import Any

class ValidatedModel(BasePyModel):
    email: str = Field(..., description="Email address")
    age: int = Field(..., description="Age in years", ge=0, le=150)
    tags: List[str] = Field(default_factory=list)

    @validator('email')
    def validate_email(cls, v):
        """Basic email validation"""
        if '@' not in v or '.' not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @validator('tags')
    def validate_tags(cls, v):
        """Ensure tags are unique and clean"""
        clean_tags = [tag.strip().lower() for tag in v if tag.strip()]
        return list(set(clean_tags))  # Remove duplicates

    @root_validator
    def validate_model(cls, values):
        """Cross-field validation"""
        age = values.get('age')
        email = values.get('email')
        
        if age and age < 13 and email:
            raise ValueError("Users under 13 cannot have email addresses")
        
        return values
```

### Step 4: Create Test Cases

Create test files in the appropriate directories:

#### `tests/prompts/example.txt`
```
Extract information from the following data:

Name: John Doe
Email: john.doe@example.com
Age: 30
Tags: developer, python, ai

Please extract the structured information.
```

#### `tests/sources/example.txt`
```
Raw data file that will be processed by the model.
This could be any format: JSON, CSV, plain text, etc.
```

#### `tests/expected/example.json`
```json
{
  "email": "john.doe@example.com",
  "age": 30,
  "tags": ["developer", "python", "ai"]
}
```

### Step 5: Configure Model Behavior

Add optional configuration:

```python
class ConfigurableModel(BasePyModel):
    """Model with configuration options"""
    
    @classmethod
    def get_skip_fields(cls) -> Set[str]:
        """Fields to skip during validation"""
        return {"debug_info", "internal_metadata"}

    @classmethod
    def get_test_cases(cls) -> List[str]:
        """Custom test case discovery"""
        test_dir = cls.TEST_DIR
        return [f.stem for f in Path(test_dir).glob("prompts/*.txt")]

    def save_report(self, output_dir: Optional[str] = None) -> str:
        """Save model output to reports directory"""
        if output_dir is None:
            output_dir = self.REPORT_DIR
            
        os.makedirs(output_dir, exist_ok=True)
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.dict(), f, indent=2)
            
        return filepath
```

## Model Design Patterns

### 1. Hierarchical Data
For complex nested structures:

```python
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None

class PersonModel(BasePyModel):
    name: str
    addresses: List[Address] = Field(default_factory=list)
    primary_address: Optional[Address] = None
```

### 2. Union Types
For fields that can have multiple types:

```python
from typing import Union

class FlexibleModel(BasePyModel):
    value: Union[str, int, float] = Field(..., description="Value of any type")
    status: Union[bool, str] = Field(..., description="Status as boolean or string")
```

### 3. Conditional Fields
For context-dependent fields:

```python
class ConditionalModel(BasePyModel):
    document_type: str = Field(..., description="Type of document")
    content: str = Field(..., description="Document content")
    
    # Only present for certain document types
    page_count: Optional[int] = Field(None, description="Number of pages (for PDFs)")
    image_count: Optional[int] = Field(None, description="Number of images (for media)")
    
    @root_validator
    def conditional_validation(cls, values):
        doc_type = values.get('document_type')
        
        if doc_type == 'pdf' and not values.get('page_count'):
            raise ValueError("PDF documents must specify page count")
            
        return values
```

### 4. Enumerated Values
For constrained choices:

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskModel(BasePyModel):
    title: str = Field(..., description="Task title")
    priority: Priority = Field(..., description="Task priority level")
    status: str = Field(..., description="Current status")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v
```

## Testing Models

### Unit Testing

```python
import pytest
from your_domain.model import YourDomainModel

def test_model_creation():
    """Test basic model creation"""
    data = {
        "primary_field": "test data",
        "confidence_score": 0.95
    }
    
    model = YourDomainModel(**data)
    assert model.primary_field == "test data"
    assert model.confidence_score == 0.95

def test_validation_errors():
    """Test validation error handling"""
    with pytest.raises(ValueError):
        YourDomainModel(
            primary_field="",  # Should fail validation
            confidence_score=1.5  # Out of range
        )

def test_field_filtering():
    """Test field filtering functionality"""
    data = {
        "primary_field": "test",
        "confidence_score": 0.8,
        "invalid_field": "should be ignored"
    }
    
    model = YourDomainModel.create_filtered(data)
    assert not hasattr(model, 'invalid_field')
```

### Integration Testing

```python
from src.ai_helper import AiHelper

async def test_model_with_llm():
    """Test model with actual LLM integration"""
    ai_helper = AiHelper()
    
    prompt = "Extract data from: Name: John, Age: 30"
    result, report = await ai_helper.get_result_async(
        prompt=prompt,
        pydantic_model=YourDomainModel,
        llm_model_name="gpt-4o-mini"
    )
    
    assert isinstance(result, YourDomainModel)
    assert result.primary_field is not None
    assert 0 <= result.confidence_score <= 1
    assert report.cost > 0
```

## Performance Optimization

### 1. Field Descriptions
Make field descriptions specific to guide the LLM:

```python
# Good: Specific guidance
description="Extract the main topic as a 2-3 word phrase"

# Less effective: Vague description  
description="The topic"
```

### 2. Validation Efficiency
Use efficient validators:

```python
# Efficient: Simple validation
@validator('email')
def validate_email(cls, v):
    return v.lower() if '@' in v else v

# Less efficient: Complex regex
@validator('email')
def validate_email_complex(cls, v):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, v):
        raise ValueError("Invalid email")
    return v
```

### 3. Optional vs Required Fields
Balance completeness with reliability:

```python
class OptimizedModel(BasePyModel):
    # Required: Core information that's usually available
    title: str = Field(..., description="Document title")
    
    # Optional: Information that might not always be present
    author: Optional[str] = Field(None, description="Document author if mentioned")
    date: Optional[str] = Field(None, description="Document date if specified")
```

## Error Handling

### Graceful Degradation

```python
class RobustModel(BasePyModel):
    essential_field: str = Field(..., description="Critical information")
    optional_details: Optional[List[str]] = Field(default_factory=list)
    
    @classmethod
    def get_skip_fields(cls) -> Set[str]:
        """Skip problematic fields rather than failing completely"""
        return {"metadata", "debug_info"}
    
    @validator('optional_details', pre=True)
    def handle_optional_details(cls, v):
        """Handle various input formats gracefully"""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(item) for item in v if item]
        return []
```

### Validation Recovery

```python
class RecoveryModel(BasePyModel):
    score: float = Field(..., description="Numeric score", ge=0, le=1)
    
    @validator('score', pre=True)
    def normalize_score(cls, v):
        """Attempt to normalize various score formats"""
        try:
            # Handle string percentages
            if isinstance(v, str):
                if '%' in v:
                    return float(v.replace('%', '')) / 100
                return float(v)
            
            # Handle out-of-range values
            if isinstance(v, (int, float)):
                if v > 1:
                    return v / 100  # Assume percentage
                return max(0, min(1, v))  # Clamp to range
                
        except (ValueError, TypeError):
            return 0.0  # Default fallback
```

## Best Practices

### 1. Descriptive Field Names
```python
# Good: Clear, specific names
document_title: str
publication_date: Optional[date]
confidence_score: float

# Avoid: Ambiguous names
title: str  # Title of what?
date: str   # What kind of date?
score: float  # Score of what?
```

### 2. Comprehensive Descriptions
```python
price: float = Field(
    ..., 
    description="Product price in USD, without currency symbol",
    ge=0
)

tags: List[str] = Field(
    default_factory=list,
    description="Relevant topic tags, 2-5 words each, lowercase"
)
```

### 3. Validation Strategy
```python
# Validate early and provide helpful errors
@validator('email')
def validate_email(cls, v):
    if not v:
        raise ValueError("Email is required")
    if '@' not in v:
        raise ValueError("Email must contain @ symbol")
    return v.strip().lower()

# Use root_validator for cross-field validation
@root_validator
def validate_dates(cls, values):
    start_date = values.get('start_date')
    end_date = values.get('end_date')
    
    if start_date and end_date and start_date > end_date:
        raise ValueError("Start date must be before end date")
    
    return values
```

### 4. Test Coverage
Ensure comprehensive testing:
- Valid input cases
- Invalid input handling
- Edge cases and boundary conditions
- Integration with LLM systems
- Performance with large inputs

## Troubleshooting

### Common Issues

1. **Validation Failures**: Check field constraints and data types
2. **Missing Fields**: Verify required fields are properly extracted
3. **Performance Issues**: Simplify validation logic or make fields optional
4. **Integration Errors**: Test model compatibility with LLM outputs

### Debug Techniques

```python
# Add debug information to models
class DebugModel(BasePyModel):
    # Regular fields
    content: str
    
    # Debug fields (excluded from main processing)
    debug_raw_input: Optional[str] = Field(None, exclude=True)
    debug_processing_time: Optional[float] = Field(None, exclude=True)
    
    @classmethod
    def create_with_debug(cls, data: dict, raw_input: str = None):
        """Create model instance with debug information"""
        import time
        start_time = time.time()
        
        instance = cls(**data)
        instance.debug_raw_input = raw_input
        instance.debug_processing_time = time.time() - start_time
        
        return instance
```

This documentation provides a comprehensive guide to understanding, creating, and working with Pydantic models in the system. The models serve as the foundation for structured LLM interactions and ensure reliable, validated data extraction.