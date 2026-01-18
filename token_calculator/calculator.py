"""
Core token calculation engine.
Handles token counting and cost calculations for different models.
"""

from typing import Dict, List, Tuple
import tiktoken
from models import ModelConfig, MODELS


class TokenCalculator:
    """Handles token counting and cost calculations."""

    def __init__(self):
        self._encoding_cache: Dict[str, tiktoken.Encoding] = {}

    def _get_encoding(self, encoding_name: str) -> tiktoken.Encoding:
        """Get or cache encoding for a given encoding name."""
        if encoding_name not in self._encoding_cache:
            try:
                self._encoding_cache[encoding_name] = tiktoken.get_encoding(encoding_name)
            except Exception:
                # Fallback to cl100k_base if encoding not found
                self._encoding_cache[encoding_name] = tiktoken.get_encoding("cl100k_base")
        return self._encoding_cache[encoding_name]

    def count_tokens(self, text: str, encoding_name: str) -> Tuple[int, List[int]]:
        """
        Count tokens in text using specified encoding.

        Args:
            text: Input text to tokenize
            encoding_name: Name of the tokenizer encoding

        Returns:
            Tuple of (token_count, token_list)
        """
        encoding = self._get_encoding(encoding_name)
        token_list = encoding.encode(text)
        return len(token_list), token_list

    def calculate_cost(
        self,
        num_tokens: int,
        cost_per_1m_tokens: float
    ) -> float:
        """
        Calculate cost for a given number of tokens.

        Args:
            num_tokens: Number of tokens
            cost_per_1m_tokens: Cost per million tokens

        Returns:
            Cost in USD
        """
        return (num_tokens / 1_000_000) * cost_per_1m_tokens

    def analyze_single_model(
        self,
        model_id: str,
        input_text: str,
        output_text: str = "",
    ) -> dict:
        """
        Analyze costs for a single model.

        Args:
            model_id: ID of the model to analyze
            input_text: Input/prompt text
            output_text: Output/completion text (optional)

        Returns:
            Dictionary with analysis results
        """
        if model_id not in MODELS:
            raise ValueError(f"Unknown model: {model_id}")

        config = MODELS[model_id]

        # Count input tokens
        input_token_count, input_token_list = self.count_tokens(
            input_text, config.encoding_name
        )
        input_cost = self.calculate_cost(
            input_token_count, config.cost_per_1m_input_tokens
        )

        # Count output tokens if provided
        output_token_count = 0
        output_token_list = []
        output_cost = 0.0

        if output_text:
            output_token_count, output_token_list = self.count_tokens(
                output_text, config.encoding_name
            )
            output_cost = self.calculate_cost(
                output_token_count, config.cost_per_1m_output_tokens
            )

        total_cost = input_cost + output_cost
        total_tokens = input_token_count + output_token_count

        return {
            "model_id": model_id,
            "model_name": config.name,
            "provider": config.provider,
            "encoding": config.encoding_name,
            "input_tokens": input_token_count,
            "output_tokens": output_token_count,
            "total_tokens": total_tokens,
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost,
            "cost_per_1m_input": config.cost_per_1m_input_tokens,
            "cost_per_1m_output": config.cost_per_1m_output_tokens,
            "context_window": config.context_window,
        }

    def analyze_all_models(
        self,
        input_text: str,
        output_text: str = "",
    ) -> Dict[str, dict]:
        """
        Analyze costs across all available models.

        Args:
            input_text: Input/prompt text
            output_text: Output/completion text (optional)

        Returns:
            Dictionary mapping model_id to analysis results
        """
        results = {}
        for model_id in MODELS.keys():
            results[model_id] = self.analyze_single_model(
                model_id, input_text, output_text
            )
        return results

    def get_cost_per_token(self, model_id: str, token_type: str = "input") -> float:
        """
        Get cost per individual token for a model.

        Args:
            model_id: ID of the model
            token_type: "input" or "output"

        Returns:
            Cost per single token in USD
        """
        if model_id not in MODELS:
            raise ValueError(f"Unknown model: {model_id}")

        config = MODELS[model_id]
        if token_type == "input":
            return config.cost_per_1m_input_tokens / 1_000_000
        elif token_type == "output":
            return config.cost_per_1m_output_tokens / 1_000_000
        else:
            raise ValueError(f"Invalid token_type: {token_type}")
