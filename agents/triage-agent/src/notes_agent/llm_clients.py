"""
LLM client wrappers for different providers.
"""
import os
import json
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_deepseek_client() -> OpenAI:
    """
    Get DeepSeek client (OpenAI-compatible).

    DeepSeek uses the OpenAI SDK with a custom base URL.
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )


def get_openai_client() -> OpenAI:
    """Get OpenAI client."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")

    return OpenAI(api_key=api_key)


def call_deepseek(
    system_prompt: str,
    user_prompt: str,
    model: str = "deepseek-chat",
    temperature: float = 0.2,
    max_tokens: int = 4000,
    response_format: Optional[dict] = None
) -> str:
    """
    Call DeepSeek API and return the response content.

    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        model: Model name (default: deepseek-chat)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        response_format: Optional response format (e.g., {"type": "json_object"})

    Returns:
        Response content as string
    """
    client = get_deepseek_client()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    if response_format:
        kwargs["response_format"] = response_format

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def call_openai(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: int = 4000,
    response_format: Optional[dict] = None
) -> str:
    """
    Call OpenAI API and return the response content.

    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        model: Model name (default: gpt-4o-mini)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        response_format: Optional response format (e.g., {"type": "json_object"})

    Returns:
        Response content as string
    """
    client = get_openai_client()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    if response_format:
        kwargs["response_format"] = response_format

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def parse_json_response(response: str) -> dict:
    """
    Parse JSON response, handling potential formatting issues.

    Args:
        response: Raw response string

    Returns:
        Parsed JSON dict

    Raises:
        json.JSONDecodeError: If response is not valid JSON
    """
    # Try direct parse first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try extracting JSON between first { and last }
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = response[start:end+1]
            return json.loads(json_str)
        else:
            raise
