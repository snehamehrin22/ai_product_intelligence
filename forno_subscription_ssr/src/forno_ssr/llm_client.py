"""
OpenAI LLM client for generating synthetic responses and embeddings.

Uses GPT-4o for text generation and text-embedding-3-small for embeddings.
"""

import os
import json
from pathlib import Path
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

from .schemas import Persona, SubscriptionConcept

# Load environment variables
load_dotenv()


class LLMClient:
    """
    Client for OpenAI API interactions.

    Handles both text generation (GPT-4o) and embeddings (text-embedding-3-small).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        embedding_model: str = "text-embedding-3-small",
        temperature: float = 0.5,
    ):
        """
        Initialize LLM client.

        Args:
            api_key: OpenAI API key (defaults to env var)
            model: Model for text generation
            embedding_model: Model for embeddings
            temperature: Sampling temperature for generation
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_model = embedding_model
        self.temperature = temperature

        # Load prompts from files
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.system_prompt = self._load_prompt("persona_system.txt")
        self.question_template = self._load_prompt("subscription_question.txt")

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt from the prompts directory."""
        prompt_path = self.prompts_dir / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")

    def generate_persona_description(self, persona: Persona) -> str:
        """
        Create a detailed persona description for the user prompt.

        Args:
            persona: Persona object

        Returns:
            Text description of the persona
        """
        return f"""You are a {persona.age}-year-old {persona.role}.

Your situation:
- Income level: {persona.income_level.value}
- You visit Forno Cultura {persona.visit_frequency}
- Your typical behavior: {persona.current_behavior}
- Location: {persona.location}

Respond as this person would, considering your budget, habits, and relationship with Forno."""

    def generate_concept_description(self, concept: SubscriptionConcept) -> str:
        """
        Create detailed concept description for the prompt.

        Args:
            concept: SubscriptionConcept object

        Returns:
            Text description of the subscription concept
        """
        value_props_text = "\n".join([f"• {vp}" for vp in concept.value_props])

        return f"""SUBSCRIPTION CONCEPT: {concept.name}

{concept.description}

KEY BENEFITS:
{value_props_text}

PRICING: {concept.price_point}

TARGET: {concept.target_behavior}"""

    def generate_subscription_response(
        self,
        persona: Persona,
        concept: SubscriptionConcept,
    ) -> str:
        """
        Generate free-text response about subscription intent.

        Uses GPT-4o with response_format to ensure valid output.

        Args:
            persona: The persona responding
            concept: The subscription concept being evaluated

        Returns:
            Free-text response explaining subscription intent (3-5 sentences)
        """
        persona_desc = self.generate_persona_description(persona)
        concept_desc = self.generate_concept_description(concept)

        user_prompt = f"""{persona_desc}

{concept_desc}

{self.question_template}

Please respond in 3-5 sentences explaining your reasoning. Return your response in JSON format:
{{"response": "your 3-5 sentence explanation here"}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=300,
        )

        # Parse JSON response
        content = response.choices[0].message.content
        try:
            data = json.loads(content)
            return data.get("response", content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return content

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding vector for text.

        Uses text-embedding-3-small model.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )

        return response.data[0].embedding

    def get_multiple_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for multiple texts in a single API call.

        More efficient than calling get_embedding multiple times.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=texts,
        )

        # Ensure embeddings are in same order as input
        embeddings = sorted(response.data, key=lambda x: x.index)
        return [emb.embedding for emb in embeddings]
