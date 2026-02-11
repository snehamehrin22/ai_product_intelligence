"""Token cost calculator for different LLM providers.

Pricing data as of February 2025.
"""

from typing import Dict, Literal, TypedDict


class TokenUsage(TypedDict):
    """Token usage from an LLM response."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CostBreakdown(TypedDict):
    """Cost breakdown for an LLM call."""
    prompt_cost: float
    completion_cost: float
    total_cost: float
    provider: str
    model: str
    tokens: TokenUsage


# Pricing in USD per 1 million tokens
# Last updated: February 2025
PRICING = {
    "openai": {
        "gpt-4o": {
            "input": 2.50,
            "output": 10.00,
        },
        "gpt-4": {
            "input": 30.00,
            "output": 60.00,
        },
        "gpt-4-turbo": {
            "input": 10.00,
            "output": 30.00,
        },
        "gpt-3.5-turbo": {
            "input": 0.50,
            "output": 1.50,
        },
    },
    "anthropic": {
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,
            "output": 15.00,
        },
        "claude-3-opus-20240229": {
            "input": 15.00,
            "output": 75.00,
        },
        "claude-3-sonnet-20240229": {
            "input": 3.00,
            "output": 15.00,
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,
            "output": 1.25,
        },
    },
    "deepseek": {
        "deepseek-chat": {
            "input": 0.27,
            "output": 1.10,
        },
        "deepseek-coder": {
            "input": 0.27,
            "output": 1.10,
        },
    },
}


def get_pricing(
    provider: Literal["openai", "anthropic", "deepseek"],
    model: str
) -> Dict[str, float]:
    """
    Get pricing for a specific provider and model.

    Args:
        provider: LLM provider name
        model: Model name

    Returns:
        Dictionary with 'input' and 'output' prices per 1M tokens

    Raises:
        ValueError: If provider or model not found
    """
    if provider not in PRICING:
        available = ", ".join(PRICING.keys())
        raise ValueError(
            f"Unknown provider: {provider}. Available providers: {available}"
        )

    if model not in PRICING[provider]:
        available = ", ".join(PRICING[provider].keys())
        raise ValueError(
            f"Unknown model: {model} for provider {provider}. "
            f"Available models: {available}"
        )

    return PRICING[provider][model]


def calculate_cost(
    provider: Literal["openai", "anthropic", "deepseek"],
    model: str,
    tokens: TokenUsage,
) -> CostBreakdown:
    """
    Calculate cost for an LLM call based on token usage.

    Args:
        provider: LLM provider name (openai, anthropic, deepseek)
        model: Model name (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
        tokens: Token usage with prompt_tokens and completion_tokens

    Returns:
        CostBreakdown with prompt_cost, completion_cost, and total_cost in USD

    Example:
        >>> tokens = {"prompt_tokens": 1000, "completion_tokens": 500, "total_tokens": 1500}
        >>> cost = calculate_cost("openai", "gpt-4o", tokens)
        >>> print(f"${cost['total_cost']:.4f}")
        $0.0075

    Raises:
        ValueError: If provider or model not found
    """
    pricing = get_pricing(provider, model)

    # Convert from per-million to per-token
    prompt_cost = (tokens["prompt_tokens"] / 1_000_000) * pricing["input"]
    completion_cost = (tokens["completion_tokens"] / 1_000_000) * pricing["output"]
    total_cost = prompt_cost + completion_cost

    return CostBreakdown(
        prompt_cost=prompt_cost,
        completion_cost=completion_cost,
        total_cost=total_cost,
        provider=provider,
        model=model,
        tokens=tokens,
    )


def format_cost(cost: CostBreakdown, verbose: bool = False) -> str:
    """
    Format cost breakdown as a human-readable string.

    Args:
        cost: Cost breakdown from calculate_cost()
        verbose: If True, include detailed breakdown

    Returns:
        Formatted cost string

    Example:
        >>> cost = calculate_cost("openai", "gpt-4o", {"prompt_tokens": 1000, "completion_tokens": 500, "total_tokens": 1500})
        >>> print(format_cost(cost))
        $0.0075
        >>> print(format_cost(cost, verbose=True))
        Total: $0.0075 (prompt: $0.0025, completion: $0.0050)
        Provider: openai, Model: gpt-4o
        Tokens: 1000 + 500 = 1500
    """
    if verbose:
        return (
            f"Total: ${cost['total_cost']:.4f} "
            f"(prompt: ${cost['prompt_cost']:.4f}, completion: ${cost['completion_cost']:.4f})\n"
            f"Provider: {cost['provider']}, Model: {cost['model']}\n"
            f"Tokens: {cost['tokens']['prompt_tokens']} + {cost['tokens']['completion_tokens']} = {cost['tokens']['total_tokens']}"
        )
    else:
        return f"${cost['total_cost']:.4f}"
