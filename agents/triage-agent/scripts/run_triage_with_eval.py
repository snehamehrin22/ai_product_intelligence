"""
Complete chained workflow: Triage → Google Sheets → Evaluation

This script:
1. Runs triage on input
2. Writes results to Google Sheets with prompt version label
3. Evaluates the output quality
4. Writes evaluation to separate sheet tab

Usage:
    python scripts/run_triage_with_eval.py \
        --input tests/inputs/sample_01.txt \
        --prompt-version "prompt1" \
        --sheet-id YOUR_SHEET_ID
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.layer1_triage import triage_braindump
from notes_agent.tools_sheets import write_triage_items_to_sheet, write_evaluation_to_sheet
from notes_agent.evaluator import evaluate_triage_output, count_tokens

load_dotenv()


def load_prompt() -> str:
    """Load the triage system prompt."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "layer1_triage_system.txt"
    return prompt_path.read_text(encoding="utf-8")


def main():
    """Run complete workflow: triage → sheets → evaluation."""
    parser = argparse.ArgumentParser(description="Complete triage workflow with evaluation")
    parser.add_argument('--input', required=True, help='Input file to process')
    parser.add_argument('--prompt-version', default='unknown', help='Label for this prompt (e.g., "prompt1", "v2.3")')
    parser.add_argument('--sheet-id', help='Google Sheet ID (default: from .env GOOGLE_SHEET_PROMPT1_ID)')
    parser.add_argument('--no-eval', action='store_true', help='Skip evaluation step')
    args = parser.parse_args()

    # Get sheet ID
    sheet_id = args.sheet_id or os.getenv('GOOGLE_SHEET_PROMPT1_ID')
    if not sheet_id or sheet_id == 'your-sheet-id-here':
        print("❌ Please provide --sheet-id or set GOOGLE_SHEET_PROMPT1_ID in .env")
        return

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return

    input_text = input_path.read_text(encoding='utf-8').strip()

    # Load prompt and calculate tokens
    try:
        prompt_text = load_prompt()
        prompt_tokens = count_tokens(prompt_text)
        input_tokens = count_tokens(input_text)
    except Exception as e:
        print(f"⚠️  Could not load prompt or count tokens: {e}\n")
        prompt_text = None
        prompt_tokens = 0
        input_tokens = 0

    print(f"\n{'='*80}")
    print(f"COMPLETE TRIAGE WORKFLOW")
    print(f"{'='*80}\n")
    print(f"Input: {input_path.name}")
    print(f"Prompt Version: {args.prompt_version}")
    print(f"Sheet ID: {sheet_id}\n")

    # Show prompt preview and token counts
    if prompt_text:
        print(f"{'─'*80}")
        print("PROMPT BEING USED:")
        print(f"{'─'*80}")
        # Show first 500 chars of prompt
        preview = prompt_text[:500].replace('\n', ' ')
        print(f"{preview}...\n")
        print(f"📊 Token Counts:")
        print(f"   Prompt: {prompt_tokens:,} tokens")
        print(f"   Input:  {input_tokens:,} tokens")
        print(f"   Total:  {prompt_tokens + input_tokens:,} tokens\n")

    # Step 1: Run triage
    print(f"{'─'*80}")
    print("STEP 1: Running triage...")
    print(f"{'─'*80}\n")

    items = triage_braindump(
        raw_text=input_text,
        date=datetime.now().strftime("%Y-%m-%d"),
        starting_id=1
    )

    # Calculate output tokens
    import json
    output_text = json.dumps([item.dict() for item in items])
    output_tokens = count_tokens(output_text)

    print(f"\n✓ Generated {len(items)} triage items")
    print(f"📊 Output: {output_tokens:,} tokens")
    print(f"📊 Total tokens used: {prompt_tokens + input_tokens + output_tokens:,} tokens\n")

    # Step 2: Write to Google Sheets
    print(f"{'─'*80}")
    print("STEP 2: Writing to Google Sheets...")
    print(f"{'─'*80}\n")

    try:
        url = write_triage_items_to_sheet(
            items=items,
            sheet_id=sheet_id,
            worksheet_name=args.prompt_version,  # Use prompt version as tab name
            clear_existing=True,
            prompt_version=args.prompt_version  # Add prompt label to sheet
        )
        print(f"\n✓ Sheet updated: {url}\n")
    except Exception as e:
        print(f"\n❌ Failed to write to sheets: {e}\n")
        return

    # Step 3: Evaluate
    if not args.no_eval:
        print(f"{'─'*80}")
        print("STEP 3: Evaluating triage quality...")
        print(f"{'─'*80}\n")

        try:
            evaluation = evaluate_triage_output(
                input_text=input_text,
                items=items,
                prompt_version=args.prompt_version
            )

            # Print summary
            print(f"\n{'='*80}")
            print("EVALUATION RESULTS")
            print(f"{'='*80}\n")
            print(f"Overall Score: {evaluation.overall_score:.2f}/5.0")
            print(f"Recommendation: {evaluation.recommendation}")
            print(f"Strengths: {evaluation.strengths}")
            print(f"Weaknesses: {evaluation.weaknesses}\n")

            # Write evaluation to sheets
            eval_url = write_evaluation_to_sheet(
                evaluation=evaluation,
                sheet_id=sheet_id,
                worksheet_name=f"Eval_{args.prompt_version}"
            )

            print(f"\n✓ Evaluation written to: {eval_url}\n")

        except Exception as e:
            print(f"\n❌ Evaluation failed: {e}\n")

    print(f"{'='*80}")
    print("WORKFLOW COMPLETE")
    print(f"{'='*80}\n")
    print(f"📊 View results: https://docs.google.com/spreadsheets/d/{sheet_id}\n")


if __name__ == '__main__':
    main()
