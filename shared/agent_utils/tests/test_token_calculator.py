"""Tests for token cost calculator."""

import pytest
from agent_utils import calculate_cost, get_pricing
from agent_utils.token_calculator import format_cost, PRICING


def test_get_pricing_openai():
    """Test getting OpenAI pricing."""
    pricing = get_pricing("openai", "gpt-4o")
    assert pricing["input"] == 2.50
    assert pricing["output"] == 10.00


def test_get_pricing_anthropic():
    """Test getting Anthropic pricing."""
    pricing = get_pricing("anthropic", "claude-3-5-sonnet-20241022")
    assert pricing["input"] == 3.00
    assert pricing["output"] == 15.00


def test_get_pricing_deepseek():
    """Test getting DeepSeek pricing."""
    pricing = get_pricing("deepseek", "deepseek-chat")
    assert pricing["input"] == 0.27
    assert pricing["output"] == 1.10


def test_get_pricing_invalid_provider():
    """Test error handling for invalid provider."""
    with pytest.raises(ValueError, match="Unknown provider"):
        get_pricing("invalid", "gpt-4")


def test_get_pricing_invalid_model():
    """Test error handling for invalid model."""
    with pytest.raises(ValueError, match="Unknown model"):
        get_pricing("openai", "invalid-model")


def test_calculate_cost_gpt4o():
    """Test cost calculation for GPT-4o."""
    tokens = {
        "prompt_tokens": 1000,
        "completion_tokens": 500,
        "total_tokens": 1500
    }

    cost = calculate_cost("openai", "gpt-4o", tokens)

    # GPT-4o: $2.50 per 1M input, $10.00 per 1M output
    # Expected: (1000/1M * 2.50) + (500/1M * 10.00) = 0.0025 + 0.005 = 0.0075
    assert cost["prompt_cost"] == pytest.approx(0.0025)
    assert cost["completion_cost"] == pytest.approx(0.0050)
    assert cost["total_cost"] == pytest.approx(0.0075)
    assert cost["provider"] == "openai"
    assert cost["model"] == "gpt-4o"
    assert cost["tokens"] == tokens


def test_calculate_cost_claude():
    """Test cost calculation for Claude."""
    tokens = {
        "prompt_tokens": 2000,
        "completion_tokens": 1000,
        "total_tokens": 3000
    }

    cost = calculate_cost("anthropic", "claude-3-5-sonnet-20241022", tokens)

    # Claude 3.5 Sonnet: $3.00 per 1M input, $15.00 per 1M output
    # Expected: (2000/1M * 3.00) + (1000/1M * 15.00) = 0.006 + 0.015 = 0.021
    assert cost["prompt_cost"] == pytest.approx(0.006)
    assert cost["completion_cost"] == pytest.approx(0.015)
    assert cost["total_cost"] == pytest.approx(0.021)


def test_calculate_cost_deepseek():
    """Test cost calculation for DeepSeek."""
    tokens = {
        "prompt_tokens": 10000,
        "completion_tokens": 5000,
        "total_tokens": 15000
    }

    cost = calculate_cost("deepseek", "deepseek-chat", tokens)

    # DeepSeek: $0.27 per 1M input, $1.10 per 1M output
    # Expected: (10000/1M * 0.27) + (5000/1M * 1.10) = 0.0027 + 0.0055 = 0.0082
    assert cost["prompt_cost"] == pytest.approx(0.0027)
    assert cost["completion_cost"] == pytest.approx(0.0055)
    assert cost["total_cost"] == pytest.approx(0.0082)


def test_calculate_cost_zero_tokens():
    """Test cost calculation with zero tokens."""
    tokens = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }

    cost = calculate_cost("openai", "gpt-4o", tokens)

    assert cost["prompt_cost"] == 0.0
    assert cost["completion_cost"] == 0.0
    assert cost["total_cost"] == 0.0


def test_calculate_cost_large_numbers():
    """Test cost calculation with large token counts."""
    tokens = {
        "prompt_tokens": 100_000,
        "completion_tokens": 50_000,
        "total_tokens": 150_000
    }

    cost = calculate_cost("openai", "gpt-4", tokens)

    # GPT-4: $30.00 per 1M input, $60.00 per 1M output
    # Expected: (100000/1M * 30) + (50000/1M * 60) = 3.0 + 3.0 = 6.0
    assert cost["prompt_cost"] == pytest.approx(3.0)
    assert cost["completion_cost"] == pytest.approx(3.0)
    assert cost["total_cost"] == pytest.approx(6.0)


def test_format_cost_simple():
    """Test simple cost formatting."""
    tokens = {
        "prompt_tokens": 1000,
        "completion_tokens": 500,
        "total_tokens": 1500
    }
    cost = calculate_cost("openai", "gpt-4o", tokens)

    formatted = format_cost(cost)
    assert formatted == "$0.0075"


def test_format_cost_verbose():
    """Test verbose cost formatting."""
    tokens = {
        "prompt_tokens": 1000,
        "completion_tokens": 500,
        "total_tokens": 1500
    }
    cost = calculate_cost("openai", "gpt-4o", tokens)

    formatted = format_cost(cost, verbose=True)
    assert "$0.0075" in formatted
    assert "prompt: $0.0025" in formatted
    assert "completion: $0.0050" in formatted
    assert "openai" in formatted
    assert "gpt-4o" in formatted
    assert "1000 + 500 = 1500" in formatted


def test_all_models_have_pricing():
    """Ensure all models in PRICING have input and output prices."""
    for provider, models in PRICING.items():
        for model, pricing in models.items():
            assert "input" in pricing, f"{provider}/{model} missing input price"
            assert "output" in pricing, f"{provider}/{model} missing output price"
            assert pricing["input"] > 0, f"{provider}/{model} input price must be > 0"
            assert pricing["output"] > 0, f"{provider}/{model} output price must be > 0"


def test_cheapest_to_most_expensive():
    """Document cost comparison across providers."""
    # Using 1M tokens as baseline
    tokens = {
        "prompt_tokens": 1_000_000,
        "completion_tokens": 0,
        "total_tokens": 1_000_000
    }

    costs = []
    for provider, models in PRICING.items():
        for model in models:
            cost = calculate_cost(provider, model, tokens)
            costs.append((provider, model, cost["total_cost"]))

    # Sort by cost
    costs.sort(key=lambda x: x[2])

    # Cheapest should be Haiku or DeepSeek
    cheapest = costs[0]
    assert cheapest[2] < 1.0  # Less than $1 for 1M input tokens

    # Most expensive should be GPT-4 or Claude Opus
    most_expensive = costs[-1]
    assert most_expensive[2] > 10.0  # More than $10 for 1M input tokens

    # Print for documentation
    print("\n=== Cost Comparison (1M input tokens) ===")
    for provider, model, cost in costs:
        print(f"{provider:10s} {model:30s} ${cost:.2f}")
