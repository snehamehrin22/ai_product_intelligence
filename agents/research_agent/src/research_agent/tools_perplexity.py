"""
Perplexity Sonar API integration via OpenRouter.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from .schemas import ResearchOutput

load_dotenv()


def get_openrouter_client() -> OpenAI:
    """Create OpenAI client configured for OpenRouter."""
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY must be set in .env")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    return client


def research_with_perplexity(query: str, model: str = "perplexity/sonar-deep-research") -> ResearchOutput:
    """
    Research a query using Perplexity Sonar via OpenRouter.

    Args:
        query: The research question or observation to investigate
        model: Perplexity model to use (default: sonar-deep-research)

    Returns:
        ResearchOutput with findings and sources
    """
    client = get_openrouter_client()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.2,
            max_tokens=2000
        )

        # Extract response
        findings = response.choices[0].message.content

        # Extract sources if available (Perplexity includes citations)
        sources = []
        # Note: Perplexity's citation format may vary, this is a placeholder
        # You might need to parse the response text for URLs or use response metadata

        # Build metadata
        metadata = {
            "model": model,
            "tokens_used": response.usage.total_tokens if response.usage else None,
            "finish_reason": response.choices[0].finish_reason
        }

        return ResearchOutput(
            query=query,
            findings=findings,
            sources=sources,
            metadata=metadata
        )

    except Exception as e:
        raise Exception(f"Perplexity research failed: {e}")
