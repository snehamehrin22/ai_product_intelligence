"""
Test the full pipeline: Obsidian → Layer 1 (Triage) → Layer 2 (Insights) → Google Sheets

Usage:
    python scripts/test_obsidian_pipeline.py --input "path/to/obsidian/file.md"
"""
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.layer1_triage import triage_braindump
from notes_agent.llm_clients import call_openrouter, parse_json_response
from notes_agent.tools_sheets import write_triage_items_to_sheet

load_dotenv()

# Sheet IDs
TRIAGE_SHEET_ID = "1rPG6lOnKNKUPhyzjJYwBI-AgpIUWcmhSAd6TOLZNOIw"
INSIGHT_SHEET_ID = "1Y_CSqhjYUcd09LKqKzyqvzisr9g_DIuW52mxyhOxLc8"


def load_layer1_prompt() -> str:
    """Load Layer 1 triage prompt."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "layer1_triage_system.txt"
    return prompt_path.read_text(encoding="utf-8")


def load_layer2_prompt() -> str:
    """Load Layer 2 insight generation prompt."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "layer2_insight_generation.txt"
    return prompt_path.read_text(encoding="utf-8")


def count_tokens(text: str) -> int:
    """Rough token count (4 chars ≈ 1 token)."""
    return len(text) // 4


def run_layer1(input_text: str, date: str) -> tuple:
    """
    Run Layer 1 triage.
    Returns: (triage_items, prompt_used, tokens_used)
    """
    print(f"\n{'='*80}")
    print("LAYER 1: TRIAGE")
    print(f"{'='*80}\n")

    prompt = load_layer1_prompt()
    input_tokens = count_tokens(prompt) + count_tokens(input_text)

    print(f"📊 Input tokens: {input_tokens:,}")

    items = triage_braindump(
        raw_text=input_text,
        date=date,
        starting_id=1
    )

    output_tokens = count_tokens(json.dumps([item.model_dump() for item in items]))
    total_tokens = input_tokens + output_tokens

    print(f"📊 Output tokens: {output_tokens:,}")
    print(f"📊 Total tokens: {total_tokens:,}")
    print(f"✓ Generated {len(items)} triage items\n")

    return items, prompt, total_tokens


def run_layer2(triage_items: list, date: str) -> tuple:
    """
    Run Layer 2 insight generation with batching.
    Returns: (insights, prompt_used, tokens_used)
    """
    print(f"\n{'='*80}")
    print("LAYER 2: INSIGHT GENERATION")
    print(f"{'='*80}\n")

    # Filter items (skip Tasks, Technical)
    skip_types = {"Task", "Technical", "Config"}
    items_to_process = [item for item in triage_items if item.type not in skip_types]

    print(f"Processing {len(items_to_process)} items (skipped {len(triage_items) - len(items_to_process)} tasks/technical)")

    if not items_to_process:
        print("⏭️  No items to process for insights")
        return [], "", 0

    # Load prompt
    system_prompt = load_layer2_prompt()

    # Batch processing: split into chunks of 15 items
    BATCH_SIZE = 15
    all_insights = []
    total_tokens_used = 0
    insight_counter = 1

    num_batches = (len(items_to_process) + BATCH_SIZE - 1) // BATCH_SIZE  # Ceiling division

    if num_batches > 1:
        print(f"📦 Splitting into {num_batches} batches of up to {BATCH_SIZE} items each\n")

    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(items_to_process))
        batch_items = items_to_process[start_idx:end_idx]

        if num_batches > 1:
            print(f"{'─'*80}")
            print(f"BATCH {batch_num + 1}/{num_batches} (items {start_idx + 1}-{end_idx})")
            print(f"{'─'*80}\n")

        # Build user prompt for this batch
        triage_json = []
        for item in batch_items:
            triage_json.append({
                "id": item.id,
                "date": item.date,
                "raw_context": item.raw_context,
                "personal_or_work": item.personal_or_work,
                "domain": item.domain,
                "type": item.type,
                "tags": item.tags,
                "niche_signal": item.niche_signal,
                "publishable": item.publishable
            })

        user_prompt = f"""Date: {date}
Starting Insight ID: I{insight_counter:03d}

TRIAGE ITEMS TO ANALYZE:
{json.dumps(triage_json, indent=2, ensure_ascii=False)}

CRITICAL JSON FORMATTING RULES:
- Return ONLY a valid JSON array
- No markdown code blocks (no ```json or ```)
- No explanatory text before or after
- Start with [ and end with ]
- Each insight must be a complete valid JSON object
- If you run out of tokens, close all open brackets/braces first

Generate insights following the rules in the system prompt. Return the JSON array now:"""

        input_tokens = count_tokens(system_prompt) + count_tokens(user_prompt)
        print(f"📊 Input tokens: {input_tokens:,}")

        # Call LLM
        print(f"🤖 Calling openai/gpt-4o-mini (via OpenRouter) for insight generation...")
        response = call_openrouter(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="openai/gpt-4o-mini",
            temperature=0.3,
            max_tokens=8000,
            response_format={"type": "json_object"}  # Guarantees valid JSON
        )

        # Parse response
        try:
            data = parse_json_response(response)

            # Handle both array and object with "insights" key (like Layer 1)
            if isinstance(data, list):
                batch_insights = data
            elif isinstance(data, dict) and "insights" in data:
                batch_insights = data["insights"]
            else:
                raise ValueError(f"Unexpected response format: {type(data)}")

            output_tokens = count_tokens(response)
            batch_tokens = input_tokens + output_tokens
            total_tokens_used += batch_tokens

            print(f"📊 Output tokens: {output_tokens:,}")
            print(f"📊 Batch tokens: {batch_tokens:,}")
            print(f"✓ Generated {len(batch_insights)} insights from this batch\n")

            all_insights.extend(batch_insights)
            insight_counter += len(batch_insights)

        except Exception as e:
            print(f"❌ Error parsing batch {batch_num + 1}: {e}")
            print(f"Raw response preview: {response[:500]}...")
            # Continue with next batch instead of failing completely
            continue

    print(f"{'='*80}")
    print(f"✓ Total insights generated: {len(all_insights)}")
    print(f"📊 Total tokens used: {total_tokens_used:,}\n")

    return all_insights, system_prompt, total_tokens_used


def write_triage_to_sheet(items: list, prompt: str, tokens: int, sheet_id: str):
    """Write triage items to Google Sheet with metadata."""
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # Auth
    creds_path = Path(__file__).parent.parent / "config" / "google_service_account.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(creds_path), scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id).sheet1

    # Clear existing
    sheet.clear()

    # Metadata header
    metadata = [
        ["LAYER 1: TRIAGE - Test Run"],
        [f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
        [f"Model: deepseek-chat"],
        [f"Total Tokens: {tokens:,}"],
        [f"Items Generated: {len(items)}"],
        [""],
        ["PROMPT USED:"],
        [prompt[:500] + "..." if len(prompt) > 500 else prompt],
        [""],
        ["=" * 50],
        [""]
    ]

    # Column headers
    headers = ["ID", "Date", "Personal/Work", "Domain", "Type", "Tags", "Niche Signal", "Publishable", "Raw Context"]

    # Data rows
    rows = []
    for item in items:
        rows.append([
            item.id,
            item.date,
            item.personal_or_work,
            item.domain,
            item.type,
            item.tags,
            "TRUE" if item.niche_signal else "FALSE",
            "TRUE" if item.publishable else "FALSE",
            item.raw_context
        ])

    # Write all
    all_data = metadata + [headers] + rows
    sheet.update(range_name='A1', values=all_data)

    print(f"✓ Triage written to: https://docs.google.com/spreadsheets/d/{sheet_id}\n")


def write_insights_to_sheet(insights: list, prompt: str, tokens: int, sheet_id: str):
    """Write insights to Google Sheet with metadata."""
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # Auth
    creds_path = Path(__file__).parent.parent / "config" / "google_service_account.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(creds_path), scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id).sheet1

    # Clear existing
    sheet.clear()

    # Metadata header
    metadata = [
        ["LAYER 2: INSIGHT GENERATION - Test Run"],
        [f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
        [f"Model: deepseek-chat"],
        [f"Total Tokens: {tokens:,}"],
        [f"Insights Generated: {len(insights)}"],
        [""],
        ["PROMPT USED:"],
        [prompt[:500] + "..." if len(prompt) > 500 else prompt],
        [""],
        ["=" * 50],
        [""]
    ]

    # Column headers
    headers = ["Insight ID", "Linked Triage IDs", "Insight Text", "Tags", "Publishable Angle", "Status"]

    # Data rows
    rows = []
    for ins in insights:
        rows.append([
            ins.get("insight_id", ""),
            ins.get("linked_triage_ids", ""),
            ins.get("insight", ""),
            ins.get("tags", ""),
            ins.get("publishable_angle", ""),
            ins.get("status", "Draft")
        ])

    # Write all
    all_data = metadata + [headers] + rows
    sheet.update(range_name='A1', values=all_data)

    print(f"✓ Insights written to: https://docs.google.com/spreadsheets/d/{sheet_id}\n")


def main():
    parser = argparse.ArgumentParser(description="Test Obsidian → Triage → Insights → Sheets pipeline")
    parser.add_argument('--input', required=True, help='Path to Obsidian markdown file')
    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        return

    input_text = input_path.read_text(encoding='utf-8').strip()
    date = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'='*80}")
    print(f"OBSIDIAN → TRIAGE → INSIGHTS PIPELINE")
    print(f"{'='*80}")
    print(f"Input: {input_path.name}")
    print(f"Date: {date}\n")

    # Layer 1: Triage
    triage_items, layer1_prompt, layer1_tokens = run_layer1(input_text, date)

    # Write Layer 1 to sheet
    write_triage_to_sheet(triage_items, layer1_prompt, layer1_tokens, TRIAGE_SHEET_ID)

    # Layer 2: Insights
    insights, layer2_prompt, layer2_tokens = run_layer2(triage_items, date)

    # Write Layer 2 to sheet
    if insights:
        write_insights_to_sheet(insights, layer2_prompt, layer2_tokens, INSIGHT_SHEET_ID)

    # Summary
    print(f"\n{'='*80}")
    print("PIPELINE COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Layer 1: {len(triage_items)} triage items → {layer1_tokens:,} tokens")
    print(f"✓ Layer 2: {len(insights)} insights → {layer2_tokens:,} tokens")
    print(f"✓ Total: {layer1_tokens + layer2_tokens:,} tokens\n")
    print(f"📊 View results:")
    print(f"   Triage: https://docs.google.com/spreadsheets/d/{TRIAGE_SHEET_ID}")
    print(f"   Insights: https://docs.google.com/spreadsheets/d/{INSIGHT_SHEET_ID}\n")


if __name__ == '__main__':
    main()
