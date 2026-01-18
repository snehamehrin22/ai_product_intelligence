"""
Model configurations for token cost calculation.
Contains pricing and encoding information for various LLM providers.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ModelConfig:
    """Configuration for a single LLM model."""

    name: str
    provider: str
    encoding_name: str
    cost_per_1m_input_tokens: float
    cost_per_1m_output_tokens: float
    context_window: int

    @property
    def cost_ratio(self) -> float:
        """Output to input cost ratio."""
        if self.cost_per_1m_input_tokens == 0:
            return 0
        return self.cost_per_1m_output_tokens / self.cost_per_1m_input_tokens


# Model configurations with updated 2025 pricing
MODELS: Dict[str, ModelConfig] = {
    # OpenAI Models
    "gpt-4-turbo": ModelConfig(
        name="GPT-4 Turbo",
        provider="OpenAI",
        encoding_name="cl100k_base",
        cost_per_1m_input_tokens=10.0,
        cost_per_1m_output_tokens=30.0,
        context_window=128000,
    ),
    "gpt-4": ModelConfig(
        name="GPT-4",
        provider="OpenAI",
        encoding_name="cl100k_base",
        cost_per_1m_input_tokens=30.0,
        cost_per_1m_output_tokens=60.0,
        context_window=8192,
    ),
    "gpt-3.5-turbo": ModelConfig(
        name="GPT-3.5 Turbo",
        provider="OpenAI",
        encoding_name="cl100k_base",
        cost_per_1m_input_tokens=0.5,
        cost_per_1m_output_tokens=1.5,
        context_window=16385,
    ),
    "gpt-4o": ModelConfig(
        name="GPT-4o",
        provider="OpenAI",
        encoding_name="o200k_base",
        cost_per_1m_input_tokens=2.5,
        cost_per_1m_output_tokens=10.0,
        context_window=128000,
    ),
    "gpt-4o-mini": ModelConfig(
        name="GPT-4o Mini",
        provider="OpenAI",
        encoding_name="o200k_base",
        cost_per_1m_input_tokens=0.15,
        cost_per_1m_output_tokens=0.6,
        context_window=128000,
    ),

    # Anthropic Claude Models
    "claude-3-opus": ModelConfig(
        name="Claude 3 Opus",
        provider="Anthropic",
        encoding_name="cl100k_base",  # Approximation
        cost_per_1m_input_tokens=15.0,
        cost_per_1m_output_tokens=75.0,
        context_window=200000,
    ),
    "claude-3-sonnet": ModelConfig(
        name="Claude 3.5 Sonnet",
        provider="Anthropic",
        encoding_name="cl100k_base",  # Approximation
        cost_per_1m_input_tokens=3.0,
        cost_per_1m_output_tokens=15.0,
        context_window=200000,
    ),
    "claude-3-haiku": ModelConfig(
        name="Claude 3 Haiku",
        provider="Anthropic",
        encoding_name="cl100k_base",  # Approximation
        cost_per_1m_input_tokens=0.25,
        cost_per_1m_output_tokens=1.25,
        context_window=200000,
    ),

    # Google Gemini Models
    "gemini-1.5-pro": ModelConfig(
        name="Gemini 1.5 Pro",
        provider="Google",
        encoding_name="cl100k_base",  # Approximation
        cost_per_1m_input_tokens=1.25,
        cost_per_1m_output_tokens=5.0,
        context_window=2000000,
    ),
    "gemini-1.5-flash": ModelConfig(
        name="Gemini 1.5 Flash",
        provider="Google",
        encoding_name="cl100k_base",  # Approximation
        cost_per_1m_input_tokens=0.075,
        cost_per_1m_output_tokens=0.3,
        context_window=1000000,
    ),
}


def get_model_by_provider(provider: str) -> Dict[str, ModelConfig]:
    """Get all models from a specific provider."""
    return {
        model_id: config
        for model_id, config in MODELS.items()
        if config.provider == provider
    }


def get_all_providers() -> List[str]:
    """Get list of all unique providers."""
    return sorted(list(set(config.provider for config in MODELS.values())))
