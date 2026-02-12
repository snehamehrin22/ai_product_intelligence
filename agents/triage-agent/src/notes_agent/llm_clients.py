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


def get_openrouter_client() -> OpenAI:
    """
    Get OpenRouter client (OpenAI-compatible).

    OpenRouter provides access to multiple models through an OpenAI-compatible API.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment")

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


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


def call_openrouter(
    system_prompt: str,
    user_prompt: str,
    model: str = "anthropic/claude-3.5-sonnet",
    temperature: float = 0.2,
    max_tokens: int = 8000,
    response_format: Optional[dict] = None
) -> str:
    """
    Call OpenRouter API and return the response content.

    OpenRouter gives access to multiple models:
    - anthropic/claude-3.5-sonnet (recommended for complex reasoning)
    - openai/gpt-4o
    - openai/gpt-4o-mini
    - google/gemini-pro-1.5
    - deepseek/deepseek-chat

    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        model: Model name (default: anthropic/claude-3.5-sonnet)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        response_format: Optional response format (e.g., {"type": "json_object"})

    Returns:
        Response content as string
    """
    client = get_openrouter_client()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "extra_headers": {
            "HTTP-Referer": "https://github.com/triage-agent",  # Optional, for rankings
            "X-Title": "Triage Agent"  # Optional, shows in rankings
        }
    }

    # Note: response_format may not be supported by all models on OpenRouter
    if response_format:
        kwargs["response_format"] = response_format

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def fix_common_json_issues(response: str) -> str:
    """
    Fix common LLM JSON formatting issues.

    Args:
        response: Raw LLM response

    Returns:
        Cleaned response string
    """
    # Remove markdown code blocks
    response = response.replace('```json', '').replace('```', '')

    # Remove common prefixes
    prefixes = [
        "Here is the JSON:",
        "Here's the output:",
        "Here is the output:",
        "Output:",
        "Here you go:",
        "Here are the results:"
    ]
    for prefix in prefixes:
        if response.strip().startswith(prefix):
            response = response[len(prefix):].strip()

    # If array isn't closed properly, try to fix it
    response = response.strip()
    if response.startswith('[') and not response.endswith(']'):
        # Find last complete object
        last_brace = response.rfind('}')
        if last_brace != -1:
            # Close the array after last complete object
            response = response[:last_brace+1] + '\n]'

    return response.strip()


def parse_json_response(response: str, as_string: bool = False):
    """
    Parse JSON response, handling potential formatting issues.

    Args:
        response: Raw response string or already parsed dict/list
        as_string: If True, return formatted JSON string instead of parsing

    Returns:
        Parsed JSON (dict or list) or formatted JSON string

    Raises:
        json.JSONDecodeError: If response is not valid JSON
    """
    # If already parsed, just return it
    if isinstance(response, (dict, list)):
        return json.dumps(response, indent=2, ensure_ascii=False) if as_string else response

    # Clean up common formatting issues
    response = fix_common_json_issues(response)

    # Try direct parse first
    try:
        result = json.loads(response)
        return json.dumps(result, indent=2, ensure_ascii=False) if as_string else result
    except json.JSONDecodeError:
        # Try extracting JSON array between first [ and last ]
        if '[' in response:
            start = response.find('[')
            end = response.rfind(']')
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end+1]
                result = json.loads(json_str)
                return json.dumps(result, indent=2, ensure_ascii=False) if as_string else result

        # Try extracting JSON object between first { and last }
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = response[start:end+1]
            result = json.loads(json_str)
            return json.dumps(result, indent=2, ensure_ascii=False) if as_string else result

        raise
