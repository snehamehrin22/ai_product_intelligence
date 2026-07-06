"""
Semantic Similarity Rating (SSR) engine.

Implementation of Maier et al. (2025) methodology for mapping
free-text responses to Likert scale distributions.
"""

import numpy as np
from typing import Dict, List
from collections import defaultdict

from .schemas import (
    LikertAnchor,
    SyntheticResponse,
    SSRResult,
    AggregatedResult,
)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity score (-1 to 1, typically 0 to 1 for embeddings)
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return float(dot_product / (norm_v1 * norm_v2))


def calculate_similarities(
    response_embedding: List[float],
    anchor_embeddings: Dict[int, List[float]],
) -> Dict[int, float]:
    """
    Calculate cosine similarity between response and all anchors.

    Args:
        response_embedding: Embedding vector of the free-text response
        anchor_embeddings: Dict mapping rating (1-5) to anchor embedding

    Returns:
        Dict mapping rating to similarity score
    """
    similarities = {}
    for rating, anchor_emb in anchor_embeddings.items():
        similarities[rating] = cosine_similarity(response_embedding, anchor_emb)

    return similarities


def similarities_to_distribution(
    similarities: Dict[int, float],
    epsilon: float = 0.0,
) -> Dict[int, float]:
    """
    Convert similarity scores to probability distribution.

    Following Maier et al. (2025):
    1. Subtract minimum similarity (so lowest anchor has 0 contribution)
    2. Add small epsilon to prevent zero probabilities
    3. Normalize to sum to 1.0

    Args:
        similarities: Dict mapping rating to similarity score
        epsilon: Small value to add before normalization (default 0.0 per paper)

    Returns:
        Dict mapping rating to probability
    """
    # Subtract minimum similarity
    min_sim = min(similarities.values())
    adjusted_sims = {
        rating: sim - min_sim + epsilon
        for rating, sim in similarities.items()
    }

    # Normalize to probabilities
    total = sum(adjusted_sims.values())
    if total == 0:
        # Uniform distribution if all similarities are equal
        return {rating: 1.0 / len(similarities) for rating in similarities.keys()}

    probabilities = {
        rating: adj_sim / total
        for rating, adj_sim in adjusted_sims.items()
    }

    return probabilities


def calculate_mean_rating(distribution: Dict[int, float]) -> float:
    """
    Calculate expected value (mean) of probability distribution.

    Args:
        distribution: Dict mapping rating to probability

    Returns:
        Mean rating (1.0 to 5.0)
    """
    mean = sum(rating * prob for rating, prob in distribution.items())
    return round(mean, 2)


def calculate_mode_rating(distribution: Dict[int, float]) -> int:
    """
    Find most likely rating (mode) from distribution.

    Args:
        distribution: Dict mapping rating to probability

    Returns:
        Rating with highest probability
    """
    return max(distribution.items(), key=lambda x: x[1])[0]


def apply_ssr(
    response_embedding: List[float],
    anchor_embeddings: Dict[int, List[float]],
    response: SyntheticResponse,
    anchor_set_id: int,
) -> SSRResult:
    """
    Apply SSR methodology to map response to Likert distribution.

    Args:
        response_embedding: Embedding of the free-text response
        anchor_embeddings: Dict mapping rating to anchor embedding
        response: Original SyntheticResponse object
        anchor_set_id: Which anchor set was used

    Returns:
        SSRResult with probability distribution and summary stats
    """
    # Calculate similarities
    similarities = calculate_similarities(response_embedding, anchor_embeddings)

    # Convert to probability distribution
    distribution = similarities_to_distribution(similarities)

    # Calculate summary statistics
    mean_rating = calculate_mean_rating(distribution)
    mode_rating = calculate_mode_rating(distribution)

    return SSRResult(
        persona_id=response.persona_id,
        concept_id=response.concept_id,
        sample_number=response.sample_number,
        anchor_set_id=anchor_set_id,
        similarities=similarities,
        probability_distribution=distribution,
        mean_rating=mean_rating,
        mode_rating=mode_rating,
        response_text=response.response_text,
    )


def aggregate_results(
    ssr_results: List[SSRResult],
    persona_id: str,
    concept_id: str,
) -> AggregatedResult:
    """
    Aggregate SSR results across samples and anchor sets.

    Following the paper: average probability distributions and mean ratings
    across all samples and anchor sets for a given persona-concept pair.

    Args:
        ssr_results: List of SSRResult objects to aggregate
        persona_id: Persona identifier
        concept_id: Concept identifier

    Returns:
        AggregatedResult with averaged statistics
    """
    if not ssr_results:
        raise ValueError("No SSR results to aggregate")

    # Collect all distributions and mean ratings
    all_distributions = [r.probability_distribution for r in ssr_results]
    all_mean_ratings = [r.mean_rating for r in ssr_results]
    all_responses = [r.response_text for r in ssr_results]

    # Average probability distributions
    avg_distribution = {}
    for rating in range(1, 6):
        probs = [dist[rating] for dist in all_distributions]
        avg_distribution[rating] = round(np.mean(probs), 4)

    # Calculate mean and std of mean ratings
    avg_mean_rating = round(np.mean(all_mean_ratings), 2)
    std_mean_rating = round(np.std(all_mean_ratings), 3)

    return AggregatedResult(
        persona_id=persona_id,
        concept_id=concept_id,
        avg_probability_distribution=avg_distribution,
        avg_mean_rating=avg_mean_rating,
        std_mean_rating=std_mean_rating,
        sample_responses=all_responses,
    )


def batch_aggregate_results(
    all_ssr_results: List[SSRResult],
) -> List[AggregatedResult]:
    """
    Aggregate SSR results for all persona-concept pairs.

    Args:
        all_ssr_results: All SSR results from the survey

    Returns:
        List of AggregatedResult objects, one per persona-concept pair
    """
    # Group results by (persona_id, concept_id)
    grouped = defaultdict(list)
    for result in all_ssr_results:
        key = (result.persona_id, result.concept_id)
        grouped[key].append(result)

    # Aggregate each group
    aggregated = []
    for (persona_id, concept_id), results in grouped.items():
        agg_result = aggregate_results(results, persona_id, concept_id)
        aggregated.append(agg_result)

    return aggregated
