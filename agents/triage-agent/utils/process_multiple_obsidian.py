"""
Process multiple Obsidian files and consolidate results in Google Sheets.
Accumulates all triage items and insights across files.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.layer1_triage import triage_braindump
from notes_agent.llm_clients import call_openrouter, parse_json_response
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

# Sheet IDs
TRIAGE_SHEET_ID = "1rPG6lOnKNKUPhyzjJYwBI-AgpIUWcmhSAd6TOLZNOIw"
INSIGHT_SHEET_ID = "1Y_CSqhjYUcd09LKqKzyqvzisr9g_DIuW52mxyhOxLc8"


def load_layer2_prompt() -> str:
    """Load Layer 2 insight generation prompt."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "layer2_insight_generation.txt"
    return prompt_path.read_text(encoding="utf-8")


def count_tokens(text: str) -> int:
    """Rough token count (4 chars ≈ 1 token)."""
    return len(text) // 4


def run_layer1(input_text: str, date: str, starting_id: int, source_file: str):
    """Run Layer 1 triage."""
    print(f"\n{'─'*80}")
    print(f"Processing: {source_file}")
    print(f"{'─'*80}\n")

    items = triage_braindump(
        raw_text=input_text,
        date=date,
        starting_id=starting_id
    )

    print(f"✓ Generated {len(items)} triage items\n")
    return items


def run_layer2_batch(triage_items: list, date: str, insight_counter: int):
    """Run Layer 2 insight generation."""
    # Filter items
    skip_types = {"Task", "Technical", "Config"}
    items_to_process = [item for item in triage_items if item.type not in skip_types]

    if not items_to_process:
        return [], insight_counter

    print(f"  Generating insights from {len(items_to_process)} items...")

    system_prompt = load_layer2_prompt()

    # Build user prompt
    triage_json = []
    for item in items_to_process:
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
- Return a valid JSON object with an "insights" key containing an array
- Format: {{"insights": [...]}}
- Each insight must have: insight_id, linked_triage_ids, insight, tags, publishable_angle, status
- No markdown code blocks
- If no insights found, return: {{"insights": []}}

Generate insights following the rules in the system prompt. Return the JSON object now:"""

    # Call LLM
    try:
        response = call_openrouter(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="openai/gpt-4o-mini",
            temperature=0.3,
            max_tokens=8000,
            response_format={"type": "json_object"}
        )

        data = parse_json_response(response)

        # Handle both array and object with "insights" key
        if isinstance(data, list):
            insights = data
        elif isinstance(data, dict) and "insights" in data:
            insights = data["insights"]
        else:
            print(f"  ⚠️  Unexpected format, no insights generated")
            return [], insight_counter

        print(f"  ✓ Generated {len(insights)} insights\n")
        return insights, insight_counter + len(insights)

    except Exception as e:
        print(f"  ❌ Error: {e}\n")
        return [], insight_counter


def write_to_sheets(all_triage_items, all_insights):
    """Write all accumulated data to Google Sheets."""
    # Auth
    creds_path = Path(__file__).parent.parent / "config" / "google_service_account.json"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(creds_path), scope)
    client = gspread.authorize(creds)

    # Write Triage Items
    print(f"\n📊 Writing {len(all_triage_items)} triage items to sheet...")
    triage_sheet = client.open_by_key(TRIAGE_SHEET_ID).sheet1
    triage_sheet.clear()

    # Headers
    metadata = [
        ["TRIAGE ITEMS - Multiple Files"],
        [f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
        [f"Total Items: {len(all_triage_items)}"],
        [""],
        ["ID", "Source File", "Date", "Personal/Work", "Domain", "Type", "Tags", "Niche Signal", "Publishable", "Raw Context"]
    ]

    rows = []
    for item, source in all_triage_items:
        rows.append([
            item.id,
            source,
            item.date,
            item.personal_or_work,
            item.domain,
            item.type,
            item.tags,
            "TRUE" if item.niche_signal else "FALSE",
            "TRUE" if item.publishable else "FALSE",
            item.raw_context
        ])

    triage_sheet.update(range_name='A1', values=metadata + rows)
    print(f"✓ Triage: https://docs.google.com/spreadsheets/d/{TRIAGE_SHEET_ID}")

    # Write Insights
    print(f"\n📊 Writing {len(all_insights)} insights to sheet...")
    insight_sheet = client.open_by_key(INSIGHT_SHEET_ID).sheet1
    insight_sheet.clear()

    metadata = [
        ["INSIGHTS - Multiple Files"],
        [f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
        [f"Total Insights: {len(all_insights)}"],
        [""],
        ["Insight ID", "Linked Triage IDs", "Insight Text", "Tags", "Publishable Angle", "Status"]
    ]

    rows = []
    for ins in all_insights:
        rows.append([
            ins.get("insight_id", ""),
            ins.get("linked_triage_ids", ""),
            ins.get("insight", ""),
            ins.get("tags", ""),
            ins.get("publishable_angle", ""),
            ins.get("status", "Draft")
        ])

    insight_sheet.update(range_name='A1', values=metadata + rows)
    print(f"✓ Insights: https://docs.google.com/spreadsheets/d/{INSIGHT_SHEET_ID}")


def main():
    # Obsidian files to process
    obsidian_path = Path("/Users/snehamehrin/Desktop/obsidian_vaults/obsidian/Personal Context/journal_notes")
    files = [
        "Feb 20th.md",
        "Feb 14th.md",
        "Feb 13th.md",
        "Feb 12th.md",
        "23rd Jan 2f1c9002459880c997b5c973dfc0a03a.md"
    ]

    print(f"\n{'='*80}")
    print(f"PROCESSING {len(files)} OBSIDIAN FILES")
    print(f"{'='*80}\n")

    all_triage_items = []  # List of (item, source_file) tuples
    all_insights = []
    triage_id_counter = 1
    insight_id_counter = 1

    for filename in files:
        file_path = obsidian_path / filename

        if not file_path.exists():
            print(f"⏭️  Skipping {filename} (not found)")
            continue

        # Read file
        input_text = file_path.read_text(encoding='utf-8').strip()
        date = datetime.now().strftime("%Y-%m-%d")

        # Layer 1: Triage
        items = run_layer1(input_text, date, triage_id_counter, filename)

        # Store with source file
        for item in items:
            all_triage_items.append((item, filename))

        # Layer 2: Insights
        insights, insight_id_counter = run_layer2_batch(items, date, insight_id_counter)
        all_insights.extend(insights)

        triage_id_counter += len(items)

    # Write everything to sheets
    write_to_sheets(all_triage_items, all_insights)

    # Summary
    print(f"\n{'='*80}")
    print("COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Total triage items: {len(all_triage_items)}")
    print(f"✓ Total insights: {len(all_insights)}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
