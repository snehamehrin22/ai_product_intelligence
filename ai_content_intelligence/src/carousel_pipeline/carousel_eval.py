"""
Carousel evaluation and comparison system.

Compares generated carousels against expected outputs and calculates match scores.
"""

import os
from typing import Dict, List, Tuple, Any
from difflib import SequenceMatcher
import json
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

from .schemas import DirectCarouselOutput, XMLCarouselSlide

load_dotenv()


def get_supabase_client() -> Client:
    """Get Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY required in .env")

    # Note: Schema is set to "case_studies_factory" in table operations
    return create_client(url, key)


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using sequence matching.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score (0-1)
    """
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def compare_slides(
    generated_slides: List[XMLCarouselSlide],
    expected_slides: List[Dict[str, Any]]
) -> Tuple[float, List[Dict]]:
    """
    Compare generated slides against expected slides.

    Args:
        generated_slides: List of XMLCarouselSlide objects
        expected_slides: List of expected slide dicts

    Returns:
        (similarity_score, differences_list)
    """
    if len(generated_slides) != len(expected_slides):
        slide_count_match = 0.0
    else:
        slide_count_match = 1.0

    slide_similarities = []
    differences = []

    for i, (gen_slide, exp_slide) in enumerate(zip(generated_slides, expected_slides)):
        # Compare text content
        gen_text = gen_slide.full_text
        exp_text = "\n".join(exp_slide.get("text_lines", []))

        text_sim = calculate_text_similarity(gen_text, exp_text)
        slide_similarities.append(text_sim)

        if text_sim < 0.8:  # Flag low similarity slides
            differences.append({
                "slide_index": i + 1,
                "similarity": text_sim,
                "generated": gen_text[:200],
                "expected": exp_text[:200],
                "issue": "content_mismatch"
            })

    # Calculate overall similarity
    if slide_similarities:
        avg_similarity = sum(slide_similarities) / len(slide_similarities)
    else:
        avg_similarity = 0.0

    # Weight slide count match
    overall_score = (slide_count_match * 0.3) + (avg_similarity * 0.7)

    return overall_score, differences


def evaluate_carousel(
    generated: DirectCarouselOutput,
    expected: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate generated carousel against expected output.

    Args:
        generated: Generated carousel
        expected: Expected carousel structure

    Returns:
        Evaluation results dict
    """
    # Compare structure
    structure_match = 1.0 if len(generated.slides) == len(expected.get("slides", [])) else 0.0

    # Compare content
    content_sim, differences = compare_slides(
        generated.slides,
        expected.get("slides", [])
    )

    # Compare title
    title_sim = calculate_text_similarity(
        generated.title,
        expected.get("title", "")
    )

    # Calculate overall match score
    match_score = (
        structure_match * 0.2 +
        content_sim * 0.6 +
        title_sim * 0.2
    )

    return {
        "match_score": match_score,
        "structure_match": structure_match,
        "content_similarity": content_sim,
        "title_similarity": title_sim,
        "differences": differences
    }


def store_eval_result(
    supabase: Client,
    research_name: str,
    pillar_id: str,
    generated: DirectCarouselOutput,
    expected: Dict[str, Any],
    evaluation: Dict[str, Any],
    iteration: int = 1,
    parent_eval_id: str = None
) -> str:
    """
    Store evaluation result in Supabase.

    Args:
        supabase: Supabase client
        research_name: Research file name
        pillar_id: Pillar identifier
        generated: Generated carousel
        expected: Expected carousel
        evaluation: Evaluation results
        iteration: Iteration number
        parent_eval_id: Parent evaluation ID (if this is a retry)

    Returns:
        Evaluation ID
    """
    data = {
        "research_file": str(generated.source_research) if generated.source_research else "",
        "research_name": research_name,
        "pillar_id": pillar_id,
        "expected_output": expected,
        "generated_output": json.loads(json.dumps(generated.model_dump(), default=str)),
        "iteration": iteration,
        "match_score": evaluation["match_score"],
        "structure_match": evaluation["structure_match"],
        "content_similarity": evaluation["content_similarity"],
        "differences": evaluation["differences"],
        "parent_eval_id": parent_eval_id
    }

    result = supabase.schema("case_studies_factory").table("carousel_evals").insert(data).execute()

    return result.data[0]["id"]


def get_expected_output(
    supabase: Client,
    research_name: str,
    pillar_id: str
) -> Dict[str, Any]:
    """
    Get expected output from Supabase.

    Args:
        supabase: Supabase client
        research_name: Research file name
        pillar_id: Pillar identifier

    Returns:
        Expected carousel dict
    """
    result = supabase.schema("case_studies_factory").table("expected_outputs").select("*").eq(
        "research_name", research_name
    ).eq(
        "pillar_id", pillar_id
    ).execute()

    if not result.data:
        raise ValueError(f"No expected output found for {research_name} / {pillar_id}")

    return result.data[0]["carousel_data"]


def store_expected_output(
    supabase: Client,
    research_name: str,
    pillar_id: str,
    carousel_data: Dict[str, Any],
    source: str = "manual",
    notes: str = None
):
    """
    Store expected output in Supabase.

    Args:
        supabase: Supabase client
        research_name: Research file name
        pillar_id: Pillar identifier
        carousel_data: Expected carousel structure
        source: Source of this gold standard
        notes: Optional notes
    """
    data = {
        "research_name": research_name,
        "pillar_id": pillar_id,
        "carousel_data": carousel_data,
        "source": source,
        "notes": notes
    }

    supabase.schema("case_studies_factory").table("expected_outputs").upsert(data).execute()


def analyze_failures(
    differences: List[Dict]
) -> Dict[str, Any]:
    """
    Analyze what's failing in the generated carousel.

    Args:
        differences: List of difference dicts

    Returns:
        Analysis with suggested prompt adjustments
    """
    issues = {
        "content_mismatch": [],
        "tone_issues": [],
        "length_issues": [],
        "structure_issues": []
    }

    for diff in differences:
        if diff.get("issue") == "content_mismatch":
            issues["content_mismatch"].append({
                "slide": diff["slide_index"],
                "generated": diff["generated"],
                "expected": diff["expected"]
            })

    # Suggest prompt adjustments
    adjustments = []

    if len(issues["content_mismatch"]) > 3:
        adjustments.append({
            "component": "instructions",
            "change": "Emphasize staying closer to research facts",
            "reason": "Multiple slides deviated from expected content"
        })

    return {
        "issues": issues,
        "suggested_adjustments": adjustments
    }
