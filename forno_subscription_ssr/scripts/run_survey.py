"""
Run Forno Cultura subscription SSR survey.

Generates synthetic responses from all personas for all concepts,
applies SSR methodology, and saves results.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
from tqdm import tqdm

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from forno_ssr.llm_client import LLMClient
from forno_ssr.personas import get_all_personas
from forno_ssr.concepts import get_all_concepts
from forno_ssr.anchors import get_all_anchor_sets
from forno_ssr.schemas import SyntheticResponse
from forno_ssr.ssr_engine import apply_ssr, batch_aggregate_results


def main():
    """Run the full survey."""
    print("=" * 70)
    print("FORNO CULTURA SUBSCRIPTION SSR SURVEY")
    print("=" * 70)
    print()

    # Initialize client
    print("Initializing LLM client...")
    client = LLMClient(temperature=0.5)
    print(f"✓ Using model: {client.model}")
    print(f"✓ Embedding model: {client.embedding_model}")
    print()

    # Load data
    print("Loading survey data...")
    personas = get_all_personas()
    concepts = get_all_concepts()
    anchor_sets = get_all_anchor_sets()
    print(f"✓ Loaded {len(personas)} personas")
    print(f"✓ Loaded {len(concepts)} concepts")
    print(f"✓ Loaded {len(anchor_sets)} anchor sets")
    print(f"✓ Total combinations: {len(personas)} × {len(concepts)} = {len(personas) * len(concepts)}")
    print()

    # Pre-compute anchor embeddings (do once for efficiency)
    print("Computing anchor embeddings...")
    anchor_embeddings_by_set = {}
    for set_idx, anchor_set in enumerate(anchor_sets):
        anchor_texts = [anchor.statement for anchor in anchor_set]
        embeddings = client.get_multiple_embeddings(anchor_texts)

        # Map rating to embedding
        anchor_embeddings = {}
        for anchor, embedding in zip(anchor_set, embeddings):
            anchor_embeddings[anchor.rating] = embedding

        anchor_embeddings_by_set[set_idx] = anchor_embeddings
    print(f"✓ Computed embeddings for {len(anchor_sets)} anchor sets")
    print()

    # Run survey
    print("Running survey...")
    print("-" * 70)

    all_responses = []
    all_ssr_results = []
    samples_per_combo = 2  # Like the paper

    total_iterations = len(personas) * len(concepts) * samples_per_combo
    with tqdm(total=total_iterations, desc="Generating responses") as pbar:
        for persona in personas:
            for concept in concepts:
                # Generate multiple samples per combination
                for sample_num in range(1, samples_per_combo + 1):
                    # Generate free-text response
                    response_text = client.generate_subscription_response(
                        persona, concept
                    )

                    # Create SyntheticResponse object
                    response = SyntheticResponse(
                        persona_id=persona.persona_id,
                        concept_id=concept.concept_id,
                        response_text=response_text,
                        sample_number=sample_num,
                    )
                    all_responses.append(response)

                    # Get response embedding
                    response_embedding = client.get_embedding(response_text)

                    # Apply SSR for each anchor set
                    for set_idx, anchor_embeddings in anchor_embeddings_by_set.items():
                        ssr_result = apply_ssr(
                            response_embedding=response_embedding,
                            anchor_embeddings=anchor_embeddings,
                            response=response,
                            anchor_set_id=set_idx,
                        )
                        all_ssr_results.append(ssr_result)

                    pbar.update(1)

    print(f"✓ Generated {len(all_responses)} responses")
    print(f"✓ Created {len(all_ssr_results)} SSR results")
    print()

    # Aggregate results
    print("Aggregating results across samples and anchor sets...")
    aggregated_results = batch_aggregate_results(all_ssr_results)
    print(f"✓ Created {len(aggregated_results)} aggregated results")
    print()

    # Save results
    print("Saving results...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    # Save raw responses
    responses_file = data_dir / f"responses_{timestamp}.json"
    with open(responses_file, "w") as f:
        responses_data = [r.model_dump() for r in all_responses]
        json.dump(responses_data, f, indent=2)
    print(f"✓ Saved responses: {responses_file.name}")

    # Save all SSR results
    ssr_file = data_dir / f"ssr_results_{timestamp}.json"
    with open(ssr_file, "w") as f:
        ssr_data = [r.model_dump() for r in all_ssr_results]
        json.dump(ssr_data, f, indent=2)
    print(f"✓ Saved SSR results: {ssr_file.name}")

    # Save aggregated results as CSV
    agg_csv_file = data_dir / f"aggregated_results_{timestamp}.csv"
    agg_rows = []
    for agg in aggregated_results:
        row = {
            "persona_id": agg.persona_id,
            "concept_id": agg.concept_id,
            "mean_rating": agg.avg_mean_rating,
            "std_rating": agg.std_mean_rating,
            "prob_1": agg.avg_probability_distribution[1],
            "prob_2": agg.avg_probability_distribution[2],
            "prob_3": agg.avg_probability_distribution[3],
            "prob_4": agg.avg_probability_distribution[4],
            "prob_5": agg.avg_probability_distribution[5],
        }
        agg_rows.append(row)

    df_agg = pd.DataFrame(agg_rows)
    df_agg.to_csv(agg_csv_file, index=False)
    print(f"✓ Saved aggregated CSV: {agg_csv_file.name}")

    # Save aggregated results as JSON
    agg_json_file = data_dir / f"aggregated_results_{timestamp}.json"
    with open(agg_json_file, "w") as f:
        agg_data = [a.model_dump() for a in aggregated_results]
        json.dump(agg_data, f, indent=2)
    print(f"✓ Saved aggregated JSON: {agg_json_file.name}")
    print()

    # Print summary statistics
    print("=" * 70)
    print("SURVEY SUMMARY")
    print("=" * 70)
    print()

    # Overall statistics
    all_mean_ratings = [agg.avg_mean_rating for agg in aggregated_results]
    print(f"Overall mean rating: {sum(all_mean_ratings) / len(all_mean_ratings):.2f}")
    print(f"Rating range: {min(all_mean_ratings):.2f} - {max(all_mean_ratings):.2f}")
    print()

    # By concept
    print("Mean ratings by concept:")
    for concept in concepts:
        concept_ratings = [
            agg.avg_mean_rating
            for agg in aggregated_results
            if agg.concept_id == concept.concept_id
        ]
        avg = sum(concept_ratings) / len(concept_ratings)
        print(f"  {concept.name}: {avg:.2f}")
    print()

    print("=" * 70)
    print(f"Survey complete! Results saved to {data_dir}/")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Run: python scripts/analyze_results.py")
    print("  2. Review visualizations and analysis")


if __name__ == "__main__":
    main()
