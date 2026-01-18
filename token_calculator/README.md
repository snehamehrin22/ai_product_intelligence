# LLM Token Cost Analyzer

A clean, interactive tool for comparing token costs across different Large Language Model (LLM) providers including OpenAI, Anthropic, and Google.

## Features

- **Quick Compare**: Instant cost comparison across all models
- **Detailed Analysis**: In-depth breakdown by provider and model
- **Scale Calculator**: Project costs for high-volume usage
- **Interactive Visualizations**: Charts and graphs for easy understanding
- **Real-time Token Counting**: Accurate token counts using tiktoken
- **Provider Filtering**: Focus on specific providers

## Supported Models

### OpenAI
- GPT-4 Turbo
- GPT-4
- GPT-3.5 Turbo
- GPT-4o
- GPT-4o Mini

### Anthropic
- Claude 3 Opus
- Claude 3.5 Sonnet
- Claude 3 Haiku

### Google
- Gemini 1.5 Pro
- Gemini 1.5 Flash

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive UI (Recommended)

Launch the Streamlit app:
```bash
cd token_calculator
streamlit run app.py
```

Then open your browser to the provided URL (usually http://localhost:8501)

### Programmatic Usage

```python
from calculator import TokenCalculator
from comparison import ModelComparator

# Initialize
calculator = TokenCalculator()
comparator = ModelComparator()

# Analyze a single model
result = calculator.analyze_single_model(
    model_id="gpt-4o-mini",
    input_text="What is the weather like today?",
    output_text="I don't have access to real-time weather data."
)
print(f"Total cost: ${result['total_cost_usd']:.6f}")

# Compare all models
results = comparator.compare_all_models(
    input_text="What is the weather like today?",
    output_text="I don't have access to real-time weather data."
)

for r in results[:3]:  # Top 3 cheapest
    print(f"{r.model_name}: ${r.total_cost:.6f}")

# Calculate costs at scale
scale_result = comparator.calculate_cost_at_scale(
    model_id="gpt-4o-mini",
    input_text="Sample input",
    output_text="Sample output",
    num_requests=10000
)
print(f"Cost for 10k requests: ${scale_result['total_cost_usd']:.2f}")
```

## Project Structure

```
token_calculator/
├── app.py              # Streamlit UI application
├── models.py           # Model configurations and pricing
├── calculator.py       # Core token calculation engine
├── comparison.py       # Comparative analysis utilities
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## File Descriptions

- **models.py**: Contains all model configurations including pricing, encoding types, and context windows
- **calculator.py**: Core calculation engine with token counting and cost computation
- **comparison.py**: Advanced comparison features including ranking, provider analysis, and scale calculations
- **app.py**: Interactive Streamlit UI with three analysis modes and visualizations

## Key Functions

### TokenCalculator
- `count_tokens(text, encoding)`: Count tokens in text
- `analyze_single_model()`: Analyze costs for one model
- `analyze_all_models()`: Analyze costs across all models
- `get_cost_per_token()`: Get per-token cost

### ModelComparator
- `compare_all_models()`: Rank all models by cost
- `get_provider_comparison()`: Compare providers
- `get_best_value_models()`: Find most cost-effective options
- `calculate_cost_at_scale()`: Project costs for high volume
- `find_cheapest_for_use_case()`: Recommend cheapest model for your use case

## Examples

### Example 1: Quick cost check
```python
from calculator import TokenCalculator

calc = TokenCalculator()
result = calc.analyze_single_model(
    "gpt-4o-mini",
    "Hello, how are you?",
    "I'm doing great, thank you!"
)
print(f"Cost: ${result['total_cost_usd']:.6f}")
```

### Example 2: Find cheapest model
```python
from comparison import ModelComparator

comp = ModelComparator()
results = comp.compare_all_models(
    input_text="Translate this to French: Hello",
    output_text="Bonjour"
)
print(f"Cheapest: {results[0].model_name} at ${results[0].total_cost:.6f}")
```

### Example 3: Scale calculation
```python
from comparison import ModelComparator

comp = ModelComparator()
model_id, monthly_cost = comp.find_cheapest_for_use_case(
    input_text="Sample prompt",
    output_text="Sample response",
    monthly_requests=100000
)
print(f"Best model: {model_id}")
print(f"Monthly cost: ${monthly_cost:.2f}")
```

## Tips

- Input both prompt and expected output for accurate cost estimates
- Use the Scale Calculator for production planning
- Filter by provider to compare within ecosystem
- Check the detailed breakdown to understand input vs output costs

## Notes

- Token counts are approximations for non-OpenAI models
- Prices are current as of January 2025
- Context windows vary by model
- All costs are in USD

## License

MIT
