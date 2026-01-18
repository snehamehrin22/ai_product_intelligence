#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Dict, List, Tuple

import tiktoken


@dataclass
class ModelConfig:
    name: str
    encoding_name: str
    cost_per_1m_input_tokens: float
    cost_per_1m_output_tokens: float


MODELS: Dict[str, ModelConfig] = {
    "gpt-4": ModelConfig(
        name="GPT-4",
        encoding_name="cl100k_base",
        cost_per_1m_input_tokens=30.0,
        cost_per_1m_output_tokens=60.0,
    ),
    "gpt-4-turbo": ModelConfig(
        name="GPT-4 Turbo",
        encoding_name="cl100k_base",
        cost_per_1m_input_tokens=10.0,
        cost_per_1m_output_tokens=30.0,
    ),
    "gpt-3.5-turbo": ModelConfig(
        name="GPT-3.5 Turbo",
        encoding_name="cl100k_base",
        cost_per_1m_input_tokens=0.5,
        cost_per_1m_output_tokens=1.5,
    ),
    "claude-3-opus": ModelConfig(
        name="Claude 3 Opus",
        encoding_name="cl100k_base",  # Approximation
        cost_per_1m_input_tokens=15.0,
        cost_per_1m_output_tokens=75.0,
    ),
    "claude-3-sonnet": ModelConfig(
        name="Claude 3 Sonnet",
        encoding_name="cl100k_base",  # Approximation
        cost_per_1m_input_tokens=3.0,
        cost_per_1m_output_tokens=15.0,
    ),
    "claude-3-haiku": ModelConfig(
        name="Claude 3 Haiku",
        encoding_name="cl100k_base",  # Approximation
        cost_per_1m_input_tokens=0.25,
        cost_per_1m_output_tokens=1.25,
    ),
}


def count_tokens(text: str, encoding_name: str) -> Tuple[int, List[int]]:
    encoding = tiktoken.get_encoding(encoding_name)
    token_list = encoding.encode(text)
    return len(token_list), token_list


def calculate_cost(num_tokens: int, cost_per_1m_tokens: float) -> float:
    return (num_tokens / 1_000_000) * cost_per_1m_tokens


def calculate_cost_per_mode(input_text: str) -> Dict[str, dict]:
    results: Dict[str, dict] = {}

    for model_id, config in MODELS.items():
        token_count, token_list = count_tokens(input_text, config.encoding_name)
        input_cost_usd = calculate_cost(token_count, config.cost_per_1m_input_tokens)

        results[model_id] = {
            "model_name": config.name,
            "encoding": config.encoding_name,
            "token_count": token_count,
            "token_list": token_list,
            "estimated_input_cost_usd": input_cost_usd,
        }

    return results


if __name__ == "__main__":
    input_text = "Hello, world!"
    results = calculate_cost_per_mode(input_text)
    print(results)