# How to Create a New Agent

This guide walks through creating a new agent from scratch, using a hypothetical "SummaryAgent" as an example.

## Step 1: Plan Your Agent

Before coding, define:
- **Purpose**: What specific task will this agent perform?
- **Input**: What data does it need to process?
- **Output**: What structured result should it return?
- **Dependencies**: What tools or models does it require?

### Example: SummaryAgent
- **Purpose**: Generate concise summaries of long documents
- **Input**: Raw text content (potentially with file support)
- **Output**: Summary with key points and metadata
- **Dependencies**: Models good at text comprehension

## Step 2: Create the Agent Directory Structure

```bash
mkdir -p src/agents/implementations/summary
touch src/agents/implementations/summary/__init__.py
touch src/agents/implementations/summary/agent.py
touch src/agents/implementations/summary/models.py
touch src/agents/implementations/summary/prompts.py
```

## Step 3: Define the Output Model

Create `src/agents/implementations/summary/models.py`:

```python
"""Pydantic models for summary agent"""
from pydantic import BaseModel, Field
from typing import List
from py_models.base import BasePyModel


class DocumentSummary(BasePyModel):
    """Model for document summary output"""
    
    # Core summary fields
    summary: str = Field(description="Concise summary of the document")
    key_points: List[str] = Field(description="3-5 most important points")
    
    # Metadata fields
    original_length: int = Field(description="Original document word count")
    summary_length: int = Field(description="Summary word count") 
    compression_ratio: float = Field(description="Summary length / original length")
    
    # Quality indicators
    confidence_score: float = Field(description="Confidence in summary quality (0-1)")
    topics_covered: List[str] = Field(description="Main topics identified")
    
    # Optional categorization
    document_type: str = Field(description="Detected document type (article, report, etc.)")
    complexity_level: str = Field(description="Content complexity (simple, moderate, complex)")
```

**Key Points:**
- Inherit from `BasePyModel` for integration with the testing framework
- Use descriptive field names and add `Field(description=...)` for LLM guidance
- Include both core output and metadata for quality assessment
- Consider validation and business logic needs

## Step 4: Create Prompt Templates

Create `src/agents/implementations/summary/prompts.py`:

```python
"""Prompts for summary agent"""

SUMMARIZE_DOCUMENT = """
Analyze and summarize the following document:

DOCUMENT CONTENT:
{content}

Your task:
1. Create a concise summary that captures the essential information
2. Identify 3-5 key points that represent the most important ideas
3. Determine the document type and complexity level
4. Extract main topics covered
5. Assess your confidence in the summary quality

Guidelines:
- Keep summary under 200 words unless document is extremely long
- Focus on factual content, not opinions
- Maintain neutral tone
- Preserve critical details and conclusions
- If document is technical, explain concepts clearly

Provide a confidence score based on:
- Clarity of the original content
- Completeness of information captured
- Quality of key point extraction
"""

SUMMARIZE_WITH_FOCUS = """
Analyze the following document with specific focus on: {focus_area}

DOCUMENT CONTENT:
{content}

FOCUS AREA: {focus_area}

Create a summary that:
1. Emphasizes information related to the focus area
2. Maintains overall document context
3. Highlights relevant key points
4. Notes if focus area is not well covered in the document

Follow the same quality guidelines as standard summarization.
"""
```

**Key Points:**
- Use clear, specific instructions for the LLM
- Include placeholders `{content}`, `{focus_area}` for dynamic content
- Provide explicit guidelines for quality and style
- Consider multiple prompt variants for different use cases

## Step 5: Implement the Agent Class

Create `src/agents/implementations/summary/agent.py`:

```python
"""Summary agent implementation"""
from typing import Optional, Union
from pathlib import Path

from ...base.agent_base import AgentBase
from .models import DocumentSummary
from .prompts import SUMMARIZE_DOCUMENT, SUMMARIZE_WITH_FOCUS


class SummaryAgent(AgentBase):
    """Agent specialized in document summarization"""

    async def summarize_document(self, content: str, **kwargs) -> DocumentSummary:
        """Generate a summary of the provided document content"""
        
        # Add word count to the prompt context
        word_count = len(content.split())
        enhanced_prompt = f"{SUMMARIZE_DOCUMENT}\n\nOriginal document word count: {word_count}"
        
        result = await self.run(
            prompt=enhanced_prompt.format(content=content),
            pydantic_model=DocumentSummary,
            **kwargs
        )
        
        return result

    async def summarize_with_focus(self, content: str, focus_area: str, 
                                 **kwargs) -> DocumentSummary:
        """Generate a focused summary emphasizing specific aspects"""
        
        prompt = SUMMARIZE_WITH_FOCUS.format(
            content=content,
            focus_area=focus_area
        )
        
        result = await self.run(
            prompt=prompt,
            pydantic_model=DocumentSummary,
            **kwargs
        )
        
        return result

    async def summarize_file(self, file_path: Union[str, Path], 
                           **kwargs) -> DocumentSummary:
        """Summarize content from a file"""
        
        result = await self.run(
            prompt=SUMMARIZE_DOCUMENT,
            pydantic_model=DocumentSummary,
            file_path=file_path,
            **kwargs
        )
        
        return result
```

**Key Points:**
- Class name must end with "Agent" for auto-discovery
- All async methods for consistency with the framework
- Use `self.run()` for actual LLM execution
- Support both text and file inputs
- Pass through `**kwargs` for flexibility
- Add business logic like word counting where helpful

## Step 6: Add Agent Configuration

Add to `src/agents/config/agents.yaml`:

```yaml
  summary:
    name: "Document Summarizer"
    description: "Creates concise summaries of documents with key point extraction and metadata analysis"
    default_model: "openai/gpt-4o"
    default_provider: "openai"
    fallback_model: "claude-3-5-sonnet"
    fallback_provider: "anthropic"
    fallback_chain:
      - model: "gpt-4o-mini"
        provider: "openai"
      - model: "gemini-2.0-flash-001"
        provider: "google"
    capabilities:
      - text_summarization
      - document_analysis
      - key_point_extraction
      - file_processing
    system_prompt: |
      You are a document summarization specialist. Your role is to:
      1. Extract and condense key information from documents
      2. Identify the most important points and insights
      3. Maintain accuracy while achieving conciseness
      4. Provide metadata about the summarization process
      
      Focus on clarity, completeness, and actionable insights.
      Preserve critical details while removing redundancy.
```

**Key Points:**
- Use descriptive name and comprehensive description
- Choose models appropriate for text processing tasks
- Define clear fallback strategy for reliability
- List specific capabilities for discoverability
- Write focused system prompt for consistent behavior

## Step 7: Test Your Agent

Create test files and validation:

```python
# Test usage example
from src.agents.registry.agent_registry import get_registry
from src.ai_helper import AiHelper

# Initialize
ai_helper = AiHelper()
registry = get_registry()

# Create agent instance
summary_agent = registry.create_agent("summary", ai_helper)

# Test summarization
test_content = """
Long document content here...
"""

result = await summary_agent.summarize_document(test_content)
print(f"Summary: {result.summary}")
print(f"Key Points: {result.key_points}")
print(f"Confidence: {result.confidence_score}")
```

## Step 8: Integrate with Workflows (Optional)

If your agent should participate in multi-step workflows, add workflow configuration:

```yaml
workflows:
  document_processing:
    description: "Complete document analysis workflow"
    agents:
      - file_processor  # Extract content from files
      - summary         # Summarize content
      - feedback        # Quality assessment
    max_iterations: 1
    quality_threshold: 0.8
```

## Step 9: Documentation and Examples

Document your agent:
- Add usage examples to agent docstrings
- Include configuration options and their effects
- Document any special capabilities or limitations
- Provide sample inputs and expected outputs

## Common Patterns

### Error Handling
```python
async def safe_summarize(self, content: str, **kwargs) -> DocumentSummary:
    """Summarize with enhanced error handling"""
    try:
        if not content.strip():
            raise ValueError("Content cannot be empty")
            
        if len(content.split()) > 10000:
            # Handle very long documents
            kwargs['model_name'] = kwargs.get('model_name', 'claude-3-5-sonnet')
            
        return await self.summarize_document(content, **kwargs)
        
    except Exception as e:
        # Log error and potentially return partial result
        print(f"Summarization failed: {e}")
        raise
```

### Configuration Access
```python
def get_max_length(self) -> int:
    """Get maximum summary length from config"""
    return self.config.get('max_summary_length', 200)
    
def supports_file_processing(self) -> bool:
    """Check if agent supports file input"""
    return self.get_capability('file_processing')
```

### Multi-step Processing
```python
async def summarize_with_validation(self, content: str, **kwargs) -> DocumentSummary:
    """Summarize with quality validation step"""
    
    # Generate initial summary
    summary = await self.summarize_document(content, **kwargs)
    
    # Validate quality if confidence is low
    if summary.confidence_score < 0.7:
        # Retry with different prompt or model
        summary = await self.summarize_with_focus(
            content, "key insights and conclusions", **kwargs
        )
    
    return summary
```

## Best Practices Checklist

- [ ] Agent has single, clear responsibility
- [ ] Output model includes relevant metadata
- [ ] Prompts are specific and well-structured
- [ ] Configuration is comprehensive
- [ ] Error handling is implemented
- [ ] Tests cover main functionality
- [ ] Documentation is complete
- [ ] Follows naming conventions (ends with "Agent")
- [ ] Uses async/await consistently
- [ ] Supports both direct and file-based input

## Testing Your Agent

After implementation:

1. **Unit Tests**: Test individual methods with known inputs
2. **Integration Tests**: Test with real LLM calls
3. **Edge Cases**: Test with empty, very long, or malformed content
4. **Model Fallbacks**: Verify fallback behavior works
5. **Configuration**: Test different config options
6. **Performance**: Measure token usage and response times

Your agent is now ready for production use!