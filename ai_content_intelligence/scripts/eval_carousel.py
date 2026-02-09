"""
Carousel evaluation CLI.

Workflow:
1. Generate carousel
2. Compare against expected output
3. If match score < threshold, iterate prompt
4. Repeat until approved or max iterations reached

Usage:
    # Store expected output first
    python scripts/eval_carousel.py store-expected \
      --research "Superhuman" \
      --pillar pillar_01 \
      --expected-file "/path/to/expected_carousel.json"

    # Run eval loop
    python scripts/eval_carousel.py eval \
      --research "/path/to/Superhuman.md" \
      --pillar pillar_01 \
      --max-iterations 5 \
      --threshold 0.85
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.carousel_pipeline.multi_pillar_generator import generate_carousel_for_pillar
from src.carousel_pipeline.carousel_eval import (
    get_supabase_client,
    evaluate_carousel,
    store_eval_result,
    get_expected_output,
    store_expected_output
)
from src.carousel_pipeline.prompt_iterator import iterate_prompt
from src.carousel_pipeline.prompt_builder import load_prompt_template

load_dotenv()


def store_expected_command(args):
    """Store expected output in Supabase."""
    research_name = args.get("research")
    pillar_id = args.get("pillar")
    expected_file = args.get("expected_file")

    if not all([research_name, pillar_id, expected_file]):
        print("❌ Missing required arguments: --research, --pillar, --expected-file")
        sys.exit(1)

    # Load expected carousel
    expected_path = Path(expected_file)
    if not expected_path.exists():
        print(f"❌ Expected file not found: {expected_file}")
        sys.exit(1)

    expected_data = json.loads(expected_path.read_text(encoding="utf-8"))

    # Store in Supabase
    supabase = get_supabase_client()
    store_expected_output(
        supabase=supabase,
        research_name=research_name,
        pillar_id=pillar_id,
        carousel_data=expected_data,
        source="manual",
        notes="Gold standard for eval"
    )

    print(f"✅ Expected output stored:")
    print(f"   Research: {research_name}")
    print(f"   Pillar: {pillar_id}")
    print(f"   Source: {expected_file}")


def eval_command(args):
    """Run evaluation loop."""
    research_path = args.get("research")
    pillar_id = args.get("pillar")
    max_iterations = int(args.get("max_iterations", 5))
    threshold = float(args.get("threshold", 0.85))

    if not all([research_path, pillar_id]):
        print("❌ Missing required arguments: --research, --pillar")
        sys.exit(1)

    research_name = Path(research_path).stem
    supabase = get_supabase_client()

    print("\n" + "="*70)
    print("🔬 CAROUSEL EVALUATION LOOP")
    print("="*70)
    print(f"\nResearch: {research_name}")
    print(f"Pillar: {pillar_id}")
    print(f"Target threshold: {threshold}")
    print(f"Max iterations: {max_iterations}")

    # Get expected output
    try:
        expected = get_expected_output(supabase, research_name, pillar_id)
        print(f"\n✓ Expected output loaded")
    except ValueError as e:
        print(f"\n❌ {e}")
        print("   Run 'store-expected' command first")
        sys.exit(1)

    # Load current prompt
    current_prompt = load_prompt_template()
    current_version = 1
    parent_eval_id = None

    # Iteration loop
    for iteration in range(1, max_iterations + 1):
        print("\n" + "-"*70)
        print(f"ITERATION {iteration}/{max_iterations}")
        print("-"*70)

        # Generate carousel
        print(f"\n🤖 Generating carousel...")
        carousel = generate_carousel_for_pillar(
            research_path=research_path,
            pillar_id=pillar_id,
            use_chatgpt_tightening=False  # Eval on Claude output only
        )

        # Evaluate
        print(f"\n📊 Evaluating...")
        evaluation = evaluate_carousel(carousel, expected)

        match_score = evaluation["match_score"]
        print(f"\n   Match score: {match_score:.2f}")
        print(f"   Structure: {evaluation['structure_match']:.2f}")
        print(f"   Content: {evaluation['content_similarity']:.2f}")
        print(f"   Differences: {len(evaluation['differences'])}")

        # Store in Supabase
        eval_id = store_eval_result(
            supabase=supabase,
            research_name=research_name,
            pillar_id=pillar_id,
            generated=carousel,
            expected=expected,
            evaluation=evaluation,
            iteration=iteration,
            parent_eval_id=parent_eval_id
        )
        print(f"   ✓ Eval stored: {eval_id}")

        # Check if threshold met
        if match_score >= threshold:
            print(f"\n✅ SUCCESS! Match score {match_score:.2f} >= {threshold}")
            print(f"   Iterations needed: {iteration}")
            break

        # If not last iteration, iterate prompt
        if iteration < max_iterations:
            print(f"\n🔄 Score below threshold. Iterating prompt...")

            iteration_result = iterate_prompt(
                pillar_id=pillar_id,
                expected=expected,
                generated=json.loads(json.dumps(carousel.model_dump(), default=str)),
                evaluation=evaluation,
                current_prompt=current_prompt,
                current_version=current_version
            )

            current_prompt = iteration_result["new_prompt"]
            current_version = iteration_result["version"]
            parent_eval_id = eval_id

            print(f"\n   Adjustments made:")
            for key, value in iteration_result["analysis"].get("prompt_adjustments", {}).items():
                print(f"     • {key}: {value[:100]}...")
        else:
            print(f"\n⚠️  Max iterations reached. Final score: {match_score:.2f}")
            print(f"   Manual review needed.")

    print("\n" + "="*70)
    print("EVALUATION COMPLETE")
    print("="*70)


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/eval_carousel.py store-expected --research <name> --pillar <id> --expected-file <path>")
        print("  python scripts/eval_carousel.py eval --research <path> --pillar <id> [--max-iterations 5] [--threshold 0.85]")
        sys.exit(1)

    command = sys.argv[1]

    # Parse arguments
    args = {}
    i = 2
    while i < len(sys.argv):
        if sys.argv[i].startswith("--"):
            key = sys.argv[i][2:]
            if i + 1 < len(sys.argv):
                value = sys.argv[i + 1]
                args[key] = value
                i += 2
            else:
                i += 1
        else:
            i += 1

    # Route command
    if command == "store-expected":
        store_expected_command(args)
    elif command == "eval":
        eval_command(args)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
