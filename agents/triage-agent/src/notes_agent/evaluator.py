"""
LLM-based evaluator for triage quality assessment.
Uses a stronger model (GPT-4) to evaluate triage outputs.
"""
from typing import List
from .schemas import TriageItem, TriageEvaluation, ItemEvaluation
from .llm_clients import call_openai, parse_json_response
from pathlib import Path


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for
        model: Model name to determine encoding (default: gpt-4o)

    Returns:
        Number of tokens
    """
    try:
        import tiktoken
        if model.startswith("gpt-4"):
            encoding = tiktoken.encoding_for_model("gpt-4")
        elif model.startswith("gpt-3.5"):
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        else:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception as e:
        print(f"⚠️  Token counting failed: {e}")
        return 0


def load_evaluator_prompt() -> str:
    """Load the evaluation system prompt."""
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / "evaluator_system.txt"
    return prompt_path.read_text(encoding="utf-8")


def evaluate_triage_output(
    input_text: str,
    items: List[TriageItem],
    prompt_version: str = "unknown",
    model: str = "gpt-4o",
    temperature: float = 0.1
) -> TriageEvaluation:
    """
    Evaluate the quality of triage output using LLM-as-judge.

    Args:
        input_text: Original raw input text
        items: List of TriageItem objects produced
        prompt_version: Identifier for the prompt being evaluated
        model: Model to use for evaluation (default: gpt-4o)
        temperature: Sampling temperature

    Returns:
        TriageEvaluation object with scores and feedback

    Raises:
        ValueError: If evaluation fails
    """
    system_prompt = load_evaluator_prompt()

    # Format items for evaluation
    items_json = []
    for item in items:
        items_json.append({
            "id": item.id,
            "type": item.type,
            "domain": item.domain,
            "tags": item.tags,
            "raw_context": item.raw_context,
            "personal_or_work": item.personal_or_work,
            "niche_signal": item.niche_signal,
            "publishable": item.publishable
        })

    user_prompt = f"""Evaluate this triage output:

INPUT TEXT:
<<<
{input_text}
>>>

TRIAGE OUTPUT ({len(items)} items):
{items_json}

Return a JSON evaluation with:
1. Per-item scores (1-5) for each dimension
2. Overall assessment
3. Strengths and weaknesses
4. Recommendation (keep/revise/discard)

Return ONLY valid JSON matching the schema. No commentary."""

    print(f"🤖 Calling {model} for evaluation...")

    response = call_openai(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        max_tokens=3000
    )

    try:
        data = parse_json_response(response)

        # Calculate overall score
        if "item_evaluations" in data:
            all_scores = []
            for item_eval in data["item_evaluations"]:
                scores = [
                    item_eval["completeness"],
                    item_eval["classification_accuracy"],
                    item_eval["granularity"],
                    item_eval["tag_quality"],
                    item_eval["niche_signal_accuracy"],
                    item_eval["publishability_accuracy"]
                ]
                all_scores.extend(scores)

            data["overall_score"] = sum(all_scores) / len(all_scores) if all_scores else 0.0

        # Add metadata
        data["prompt_version"] = prompt_version
        data["input_text"] = input_text
        data["num_items"] = len(items)

        # Validate with Pydantic
        evaluation = TriageEvaluation(**data)

        print(f"✓ Evaluation complete: {evaluation.overall_score:.2f}/5.0\n")
        return evaluation

    except Exception as e:
        print(f"❌ Error parsing evaluation response: {e}")
        print(f"Raw response preview: {response[:500]}...")
        raise ValueError(f"Failed to parse evaluation response: {e}")


def compare_prompts(
    input_text: str,
    prompt1_items: List[TriageItem],
    prompt2_items: List[TriageItem],
    prompt1_version: str = "prompt1",
    prompt2_version: str = "prompt2"
) -> tuple:
    """
    Compare two prompt outputs side-by-side.

    Args:
        input_text: Original input text
        prompt1_items: Items from first prompt
        prompt2_items: Items from second prompt
        prompt1_version: Label for first prompt
        prompt2_version: Label for second prompt

    Returns:
        Tuple of (eval1, eval2)
    """
    print(f"\n{'='*80}")
    print(f"COMPARING PROMPTS: {prompt1_version} vs {prompt2_version}")
    print(f"{'='*80}\n")

    print(f"Evaluating {prompt1_version}...")
    eval1 = evaluate_triage_output(input_text, prompt1_items, prompt1_version)

    print(f"\nEvaluating {prompt2_version}...")
    eval2 = evaluate_triage_output(input_text, prompt2_items, prompt2_version)

    # Print comparison
    print(f"\n{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}\n")

    print(f"{prompt1_version}:")
    print(f"  Overall Score: {eval1.overall_score:.2f}/5.0")
    print(f"  Items: {eval1.num_items}")
    print(f"  Recommendation: {eval1.recommendation}")
    print(f"  Strengths: {eval1.strengths}")
    print(f"  Weaknesses: {eval1.weaknesses}\n")

    print(f"{prompt2_version}:")
    print(f"  Overall Score: {eval2.overall_score:.2f}/5.0")
    print(f"  Items: {eval2.num_items}")
    print(f"  Recommendation: {eval2.recommendation}")
    print(f"  Strengths: {eval2.strengths}")
    print(f"  Weaknesses: {eval2.weaknesses}\n")

    winner = prompt1_version if eval1.overall_score > eval2.overall_score else prompt2_version
    print(f"🏆 Winner: {winner}\n")
    print(f"{'='*80}\n")

    return eval1, eval2
