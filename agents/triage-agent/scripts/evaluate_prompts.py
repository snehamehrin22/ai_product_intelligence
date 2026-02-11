"""
Script to evaluate and compare two prompt variants.
Run this after generating outputs from both prompt worktrees.

Usage:
    python scripts/evaluate_prompts.py --input tests/inputs/sample_01.txt
"""
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.layer1_triage import triage_braindump
from notes_agent.evaluator import evaluate_triage_output, compare_prompts
from notes_agent.tools_sheets import write_triage_items_to_sheet
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    """Evaluate triage outputs and optionally write to Google Sheets."""
    parser = argparse.ArgumentParser(description="Evaluate triage prompt quality")
    parser.add_argument('--input', required=True, help='Input file to test')
    parser.add_argument('--prompt1-output', help='JSON file with prompt1 triage output')
    parser.add_argument('--prompt2-output', help='JSON file with prompt2 triage output')
    parser.add_argument('--compare', action='store_true', help='Compare two prompt outputs')
    parser.add_argument('--to-sheets', action='store_true', help='Write evaluation to Google Sheets')
    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return

    input_text = input_path.read_text(encoding='utf-8').strip()

    print(f"\n{'='*80}")
    print(f"TRIAGE EVALUATION")
    print(f"{'='*80}\n")
    print(f"Input: {input_path.name}")
    print(f"Preview: {input_text[:150]}...\n")

    if args.compare:
        # Compare mode: load two outputs
        if not args.prompt1_output or not args.prompt2_output:
            print("❌ --compare requires both --prompt1-output and --prompt2-output")
            return

        # Load outputs
        with open(args.prompt1_output, 'r') as f:
            prompt1_data = json.load(f)
        with open(args.prompt2_output, 'r') as f:
            prompt2_data = json.load(f)

        from notes_agent.schemas import TriageItem
        prompt1_items = [TriageItem(**item) for item in prompt1_data]
        prompt2_items = [TriageItem(**item) for item in prompt2_data]

        eval1, eval2 = compare_prompts(
            input_text=input_text,
            prompt1_items=prompt1_items,
            prompt2_items=prompt2_items,
            prompt1_version="prompt1",
            prompt2_version="prompt2"
        )

        # Optionally write to sheets
        if args.to_sheets:
            # TODO: Implement evaluation results in sheets
            print("📊 Google Sheets output for evaluations coming soon...")

    else:
        # Single evaluation mode
        print("🤖 Running triage...")
        items = triage_braindump(
            raw_text=input_text,
            date=datetime.now().strftime("%Y-%m-%d"),
            starting_id=1
        )

        print(f"\n✓ Generated {len(items)} triage items\n")

        # Evaluate
        evaluation = evaluate_triage_output(
            input_text=input_text,
            items=items,
            prompt_version="current"
        )

        # Print results
        print(f"\n{'='*80}")
        print(f"EVALUATION RESULTS")
        print(f"{'='*80}\n")
        print(f"Overall Score: {evaluation.overall_score:.2f}/5.0")
        print(f"Items Extracted: {evaluation.num_items}")
        print(f"Recommendation: {evaluation.recommendation}\n")
        print(f"Strengths:")
        print(f"  {evaluation.strengths}\n")
        print(f"Weaknesses:")
        print(f"  {evaluation.weaknesses}\n")

        print(f"Per-item scores:")
        for item_eval in evaluation.item_evaluations:
            print(f"\n  [{item_eval.item_id}]")
            print(f"    Completeness: {item_eval.completeness}/5")
            print(f"    Classification: {item_eval.classification_accuracy}/5")
            print(f"    Granularity: {item_eval.granularity}/5")
            print(f"    Tags: {item_eval.tag_quality}/5")
            print(f"    Niche Signal: {item_eval.niche_signal_accuracy}/5")
            print(f"    Publishable: {item_eval.publishability_accuracy}/5")
            print(f"    Reasoning: {item_eval.reasoning}")

        print(f"\n{'='*80}\n")

        # Save evaluation
        output_path = Path(__file__).parent.parent / "tests" / "evaluation_results.json"
        with open(output_path, 'w') as f:
            json.dump(evaluation.model_dump(), f, indent=2)
        print(f"💾 Saved evaluation to: {output_path}\n")


if __name__ == '__main__':
    main()
