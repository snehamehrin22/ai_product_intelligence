"""
Quick test survey with 1 persona and 1 concept.

Tests the full pipeline without running all combinations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from forno_ssr.llm_client import LLMClient
from forno_ssr.personas import get_all_personas
from forno_ssr.concepts import get_all_concepts
from forno_ssr.anchors import get_all_anchor_sets
from forno_ssr.schemas import SyntheticResponse
from forno_ssr.ssr_engine import apply_ssr, aggregate_results


def main():
    """Run quick test survey."""
    print("=" * 70)
    print("FORNO SSR - QUICK TEST SURVEY")
    print("=" * 70)
    print()

    # Initialize
    print("Initializing...")
    client = LLMClient(temperature=0.5)
    personas = get_all_personas()
    concepts = get_all_concepts()
    anchor_sets = get_all_anchor_sets()
    print(f"✓ Using: {client.model}")
    print()

    # Select test data (first persona, first concept)
    test_persona = personas[0]
    test_concept = concepts[0]
    print(f"Test persona: {test_persona.persona_id} - {test_persona.age}yo {test_persona.role}")
    print(f"Test concept: {test_concept.concept_id} - {test_concept.name}")
    print()

    # Pre-compute anchor embeddings
    print("Computing anchor embeddings...")
    anchor_embeddings_by_set = {}
    for set_idx, anchor_set in enumerate(anchor_sets):
        anchor_texts = [anchor.statement for anchor in anchor_set]
        embeddings = client.get_multiple_embeddings(anchor_texts)

        anchor_embeddings = {}
        for anchor, embedding in zip(anchor_set, embeddings):
            anchor_embeddings[anchor.rating] = embedding

        anchor_embeddings_by_set[set_idx] = anchor_embeddings
    print(f"✓ Computed {len(anchor_sets)} anchor sets")
    print()

    # Generate responses
    print("Generating responses...")
    all_responses = []
    all_ssr_results = []
    samples = 2

    for sample_num in range(1, samples + 1):
        print(f"  Sample {sample_num}/{samples}...", end=" ")

        # Generate response
        response_text = client.generate_subscription_response(
            test_persona, test_concept
        )

        response = SyntheticResponse(
            persona_id=test_persona.persona_id,
            concept_id=test_concept.concept_id,
            response_text=response_text,
            sample_number=sample_num,
        )
        all_responses.append(response)

        # Get embedding
        response_embedding = client.get_embedding(response_text)

        # Apply SSR with both anchor sets
        for set_idx, anchor_embeddings in anchor_embeddings_by_set.items():
            ssr_result = apply_ssr(
                response_embedding=response_embedding,
                anchor_embeddings=anchor_embeddings,
                response=response,
                anchor_set_id=set_idx,
            )
            all_ssr_results.append(ssr_result)

        print("✓")

    print()

    # Aggregate
    print("Aggregating results...")
    aggregated = aggregate_results(
        all_ssr_results,
        test_persona.persona_id,
        test_concept.concept_id,
    )
    print(f"✓ Averaged across {len(all_ssr_results)} SSR results")
    print()

    # Display results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"Persona: {test_persona.age}yo {test_persona.role}")
    print(f"Concept: {test_concept.name}")
    print()
    print(f"Mean subscription intent: {aggregated.avg_mean_rating:.2f}/5.0")
    print(f"Std deviation: {aggregated.std_mean_rating:.3f}")
    print()
    print("Probability distribution:")
    for rating in range(1, 6):
        prob = aggregated.avg_probability_distribution[rating]
        bar = "█" * int(prob * 50)
        print(f"  {rating}: {prob:.2%} {bar}")
    print()
    print("Sample responses:")
    for i, resp in enumerate(aggregated.sample_responses[:2], 1):
        print(f"  {i}. \"{resp}\"")
    print()

    # Save test results
    print("Saving test results...")
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_file = data_dir / f"test_quick_{timestamp}.json"

    test_data = {
        "persona": test_persona.model_dump(),
        "concept": test_concept.model_dump(),
        "responses": [r.model_dump() for r in all_responses],
        "ssr_results": [r.model_dump() for r in all_ssr_results],
        "aggregated": aggregated.model_dump(),
    }

    with open(test_file, "w") as f:
        json.dump(test_data, f, indent=2)

    print(f"✓ Saved: {test_file.name}")
    print()

    print("=" * 70)
    print("Quick test complete! ✓")
    print()
    print("Next steps:")
    print("  1. Review results above")
    print("  2. Run full survey: python scripts/run_survey.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
