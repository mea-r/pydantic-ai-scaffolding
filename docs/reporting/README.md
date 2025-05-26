# Reporting and Usage Tracking Documentation

## Overview

The reporting system provides comprehensive tracking and analysis of LLM usage, costs, performance metrics, and tool utilization. It helps monitor system efficiency, track costs, and optimize model selection across the entire platform.

## Core Components

### Usage Tracker (`src/helpers/usage_tracker.py`)

The `UsageTracker` class is the central component for collecting and analyzing usage data.

#### Key Features
- **Real-time Usage Tracking**: Automatic capture of LLM requests and tool calls
- **Cost Calculation**: Precise cost tracking based on token usage and model pricing
- **Performance Metrics**: Fill percentage tracking for model completion rates
- **Time-based Analysis**: Daily, monthly, and all-time usage summaries
- **Structured Storage**: JSON-based persistence with proper data modeling

#### Core Data Models

```python
class LLMReport(BaseModel):
    """Individual execution report"""
    model_name: str                    # LLM model used
    run_date: datetime                 # Execution timestamp
    run_id: str                        # Unique identifier
    usage: Optional[Usage]             # Token usage statistics
    cost: float                        # Execution cost in USD
    fill_percentage: int               # Model completion rate (0-100)
    fallback_used: bool                # Whether fallback was triggered
    attempted_models: List[str]        # All models attempted

class UsageItem(BaseModel):
    """LLM usage aggregation unit"""
    month: str                         # Format: "YYYY-MM"
    day: str                           # Format: "YYYY-MM-DD"
    model: str                         # LLM model name
    service: str                       # Provider (openai, anthropic, etc.)
    pydantic_model_name: str           # Associated output model
    input_tokens: int                  # Request tokens
    output_tokens: int                 # Response tokens
    total_tokens: int                  # Combined tokens
    requests: int                      # Number of requests
    cost: float                        # Total cost

class ToolUsageItem(BaseModel):
    """Tool usage tracking unit"""
    month: str                         # Format: "YYYY-MM"
    day: str                           # Format: "YYYY-MM-DD"
    tool_name: str                     # Tool function name
    calls: int                         # Number of calls

class FillPercentageStats(BaseModel):
    """Model completion statistics"""
    average: float                     # Average fill percentage
    count: int                         # Number of samples
    sum_total: float                   # Sum for average calculation
```

### Report Generator (`src/helpers/report_generator.py`)

Handles report generation and formatting (currently minimal implementation).

#### Planned Features
- Database integration for large-scale deployments
- Custom report templates
- Export to various formats (PDF, CSV, etc.)
- Scheduled report generation

## Usage Tracking Workflow

### 1. Automatic Data Collection

Usage data is automatically collected whenever LLM requests are made:

```python
# In AiHelper.get_result_async()
usage_tracker = UsageTracker()
usage_tracker.add_usage(
    usage_report=llm_report,
    model_name=model_name,
    service=provider,
    pydantic_model_name=pydantic_model.__name__,
    tool_names_called=tool_names_used
)
```

### 2. Data Aggregation

The system automatically aggregates data across multiple dimensions:
- **By Time**: Daily, monthly summaries
- **By Model**: Usage per LLM model
- **By Service**: Usage per provider
- **By Pydantic Model**: Usage per output format
- **By Tool**: Tool call frequencies

### 3. Persistent Storage

All data is stored in `logs/usage.json` with automatic backup and recovery:

```json
{
  "usage_today": 0.045,
  "usage_this_month": 1.234,
  "daily_usage": [
    {
      "day": "2024-03-15",
      "model": "gpt-4o",
      "service": "openai",
      "pydantic_model_name": "Hello_worldModel",
      "requests": 5,
      "input_tokens": 1500,
      "output_tokens": 300,
      "total_tokens": 1800,
      "cost": 0.045
    }
  ],
  "fill_percentage_by_pydantic_model": {
    "Hello_worldModel": {
      "average": 92.5,
      "count": 10,
      "sum_total": 925.0
    }
  }
}
```

## Reporting Features

### Summary Reports

The system generates comprehensive usage summaries:

```python
usage_tracker = UsageTracker()
summary = usage_tracker.get_usage_summary()

# Contains:
# - Today's usage and costs
# - Monthly summaries
# - Daily breakdowns
# - Model performance metrics
# - Tool usage statistics
```

### Formatted Output

Reports are automatically formatted into readable tables:

```python
from src.helpers.usage_tracker import format_usage_data, print_usage_report

# Load and format from file
formatted_report = format_usage_from_file("logs/usage.json")

# Print to console
print_usage_report(summary_data)
```

#### Sample Report Output

```
============================================================
OVERALL USAGE SUMMARY (COSTS)
============================================================
┌─────────────────────┬──────────────┐
│ Period              │ Value        │
├─────────────────────┼──────────────┤
│ Today (LLM Cost)    │ $0.045000    │
│ This Month (LLM Cost)│ $1.234000   │
└─────────────────────┴──────────────┘

LLM USAGE BY LLM MODEL (ALL TIME)
────────────────────────────────────────
┌─────────────────┬──────────┬─────────────┬──────────────┬─────────────┬──────────┬──────────┐
│ LLM Model       │ Requests │ Input Tokens│ Output Tokens│ Total Tokens│ Cost     │ Avg Fill %│
├─────────────────┼──────────┼─────────────┼──────────────┼─────────────┼──────────┼──────────┤
│ gpt-4o          │ 25       │ 12500       │ 2500         │ 15000       │ $0.750000│ 95.20%   │
│ claude-3-5-sonnet│ 15      │ 7500        │ 1800         │ 9300        │ $0.465000│ 88.40%   │
└─────────────────┴──────────┴─────────────┴──────────────┴─────────────┴──────────┴──────────┘

TOOL USAGE BY NAME (ALL TIME)
────────────────────────────────────────
┌─────────────────┬─────────────┐
│ Tool Name       │ Total Calls │
├─────────────────┼─────────────┤
│ calculator      │ 45          │
│ tool_get_weather│ 23          │
└─────────────────┴─────────────┘
```

### Performance Metrics

#### Fill Percentage Tracking

Monitors how completely models fulfill the requested Pydantic schemas:

```python
# Automatic calculation during model execution
fill_percentage = calculate_fill_percentage(result, expected_schema)

# Tracked by model and Pydantic type
fill_stats = usage_tracker.usage_data.fill_percentage_by_llm_model["gpt-4o"]
print(f"Average fill rate: {fill_stats.average:.2f}%")
```

#### Cost Analysis

Detailed cost tracking with multiple breakdowns:
- Cost per model
- Cost per service provider
- Cost per Pydantic model type
- Daily and monthly cost trends

#### Token Efficiency

Monitor token usage patterns:
- Input vs output token ratios
- Token efficiency by model
- Cost per token analysis

## CLI Integration

### Usage Commands

```bash
# Display comprehensive usage report
python cli.py --usage

# Print pricing information
python cli.py --prices

# Update model status based on performance
python cli.py --update_non_working
```

### Custom Analysis

```python
# In cli.py custom section
from src.helpers.usage_tracker import UsageTracker

tracker = UsageTracker()
summary = tracker.get_usage_summary()

# Custom analysis
high_cost_models = [
    model for model, stats in summary['by_model'].items()
    if stats['cost'] > 1.0
]

print(f"High cost models: {high_cost_models}")
```

## Advanced Features

### Fallback Tracking

Monitor when and why fallback models are used:

```python
# Tracked automatically in LLMReport
if llm_report.fallback_used:
    print(f"Fallback triggered: {llm_report.attempted_models}")
```

### Quality Metrics

Track model performance beyond just costs:

```python
# Fill percentage indicates completion quality
low_performance_models = [
    model for model, stats in summary['fill_percentage_by_llm_model'].items()
    if stats.average < 80.0
]
```

### Time-based Analysis

Analyze usage patterns over time:

```python
# Monthly trends
monthly_summary = summary['monthly_llm_summary']
for month, stats in monthly_summary.items():
    efficiency = stats['output_tokens'] / stats['input_tokens']
    print(f"{month}: {efficiency:.2f} output/input ratio")
```

## Configuration and Customization

### Storage Configuration

```python
# Custom storage location
tracker = UsageTracker(base_path="/custom/path")

# Alternative: Environment variable
os.environ['USAGE_LOG_PATH'] = '/custom/logs/usage.json'
```

### Report Formatting

```python
# Custom report formatting
def custom_format_usage(data: Dict[str, Any]) -> str:
    """Custom report format for specific needs"""
    output = []
    
    # Add custom sections
    if 'by_model' in data:
        output.append("CUSTOM MODEL ANALYSIS")
        for model, stats in data['by_model'].items():
            cost_per_token = stats['cost'] / stats['total_tokens']
            output.append(f"{model}: ${cost_per_token:.8f} per token")
    
    return "\n".join(output)
```

### Filtering and Aggregation

```python
class CustomUsageTracker(UsageTracker):
    """Extended tracker with custom filtering"""
    
    def get_filtered_summary(self, 
                           start_date: str = None,
                           end_date: str = None,
                           model_filter: List[str] = None) -> Dict[str, Any]:
        """Get usage summary with date and model filtering"""
        
        filtered_usage = []
        for item in self.usage_data.daily_usage:
            # Date filtering
            if start_date and item.day < start_date:
                continue
            if end_date and item.day > end_date:
                continue
            
            # Model filtering
            if model_filter and item.model not in model_filter:
                continue
                
            filtered_usage.append(item)
        
        # Generate summary from filtered data
        return self._aggregate_usage(filtered_usage)
```

## Best Practices

### 1. Regular Monitoring

Set up regular usage review:

```python
# Weekly usage review
def weekly_usage_review():
    tracker = UsageTracker()
    summary = tracker.get_usage_summary()
    
    # Check for cost anomalies
    weekly_cost = calculate_weekly_cost(summary)
    if weekly_cost > COST_THRESHOLD:
        send_alert(f"Weekly cost exceeded threshold: ${weekly_cost}")
    
    # Check model performance
    low_performers = get_low_performing_models(summary)
    if low_performers:
        review_model_configuration(low_performers)
```

### 2. Cost Optimization

Monitor and optimize costs:

```python
def optimize_model_selection():
    """Analyze cost vs performance for model optimization"""
    tracker = UsageTracker()
    summary = tracker.get_usage_summary()
    
    # Calculate cost-effectiveness
    model_efficiency = {}
    for model, stats in summary['by_model'].items():
        fill_stats = summary['fill_percentage_by_llm_model'].get(model)
        if fill_stats:
            # Cost per successful completion
            efficiency = stats['cost'] / (stats['requests'] * fill_stats.average / 100)
            model_efficiency[model] = efficiency
    
    # Recommend most efficient models
    sorted_models = sorted(model_efficiency.items(), key=lambda x: x[1])
    return sorted_models
```

### 3. Performance Monitoring

Track system health:

```python
def monitor_system_health():
    """Monitor for performance issues"""
    tracker = UsageTracker()
    summary = tracker.get_usage_summary()
    
    alerts = []
    
    # Check for high fallback usage
    total_requests = sum(stats['requests'] for stats in summary['by_model'].values())
    fallback_rate = calculate_fallback_rate(summary)
    
    if fallback_rate > 0.2:  # 20% fallback rate
        alerts.append(f"High fallback rate: {fallback_rate:.1%}")
    
    # Check for declining fill percentages
    recent_fill_rates = get_recent_fill_rates(summary)
    if detect_declining_performance(recent_fill_rates):
        alerts.append("Model performance declining")
    
    return alerts
```

### 4. Data Retention

Manage historical data:

```python
def archive_old_data():
    """Archive old usage data to prevent files from growing too large"""
    tracker = UsageTracker()
    
    # Archive data older than 90 days
    cutoff_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    old_data = [
        item for item in tracker.usage_data.daily_usage
        if item.day < cutoff_date
    ]
    
    if old_data:
        # Save to archive
        archive_data(old_data)
        
        # Remove from active tracking
        tracker.usage_data.daily_usage = [
            item for item in tracker.usage_data.daily_usage
            if item.day >= cutoff_date
        ]
        
        tracker._save()
```

## Troubleshooting

### Common Issues

1. **Missing Usage Data**: Check file permissions for `logs/usage.json`
2. **Incorrect Costs**: Verify model pricing in `llm_prices.txt`
3. **Performance Issues**: Large usage files may need archiving
4. **Incomplete Reports**: Ensure all required fields are being tracked

### Debug Mode

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugUsageTracker(UsageTracker):
    def add_usage(self, *args, **kwargs):
        logger.debug(f"Adding usage: {args}, {kwargs}")
        super().add_usage(*args, **kwargs)
        logger.debug("Usage added successfully")
```

### Data Recovery

Recover from corrupted usage files:

```python
def recover_usage_data():
    """Attempt to recover from corrupted usage file"""
    import shutil
    
    usage_file = "logs/usage.json"
    backup_file = f"{usage_file}.backup"
    
    try:
        # Try to load current file
        tracker = UsageTracker()
        return tracker
    except Exception as e:
        print(f"Usage file corrupted: {e}")
        
        # Try backup file
        if os.path.exists(backup_file):
            shutil.copy(backup_file, usage_file)
            return UsageTracker()
        
        # Create new file
        print("Creating new usage file")
        return UsageTracker()
```

This reporting system provides comprehensive insights into LLM usage patterns, costs, and performance, enabling data-driven optimization of the AI helper system.