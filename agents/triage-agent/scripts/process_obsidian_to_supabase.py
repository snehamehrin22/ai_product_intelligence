"""
Process Obsidian files to Supabase with duplicate detection.
Only processes files that haven't been processed or have changed.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.layer1_triage import triage_braindump
from notes_agent.llm_clients import call_openrouter, parse_json_response
from notes_agent.tools_supabase import (
    get_supabase_client,
    compute_file_hash,
    is_file_processed,
    mark_file_processed,
    write_triage_items,
    write_insights,
    get_processing_stats
)

load_dotenv()


def load_layer2_prompt() -> str:
    """Load Layer 2 insight generation prompt."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "layer2_insight_generation.txt"
    return prompt_path.read_text(encoding="utf-8")


def run_layer1(input_text: str, date: str, starting_id: int, source_file: str):
    """Run Layer 1 triage."""
    print(f"  🤖 Running triage...")

    items = triage_braindump(
        raw_text=input_text,
        date=date,
        starting_id=starting_id
    )

    print(f"  ✓ Generated {len(items)} triage items")
    return items


def run_layer2(triage_items: list, date: str, insight_counter: int):
    """Run Layer 2 insight generation."""
    # Filter items
    skip_types = {"Task", "Technical", "Config"}
    items_to_process = [item for item in triage_items if item.type not in skip_types]

    if not items_to_process:
        print(f"  ⏭️  No items to process for insights")
        return [], insight_counter

    print(f"  🤖 Generating insights from {len(items_to_process)} items...")

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

        print(f"  ✓ Generated {len(insights)} insights")
        return insights, insight_counter + len(insights)

    except Exception as e:
        print(f"  ❌ Error generating insights: {e}")
        return [], insight_counter


def main():
    # Obsidian path
    obsidian_path = Path("/Users/snehamehrin/Desktop/obsidian_vaults/obsidian/Personal Context/journal_notes")

    # Get ALL markdown files (sorted by modification time, newest first)
    md_files = sorted(obsidian_path.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not md_files:
        print("❌ No markdown files found in Obsidian vault")
        return

    print(f"\n{'='*80}")
    print(f"OBSIDIAN → SUPABASE PIPELINE")
    print(f"{'='*80}\n")

    # Initialize Supabase client
    try:
        client = get_supabase_client()
        print(f"✓ Connected to Supabase\n")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return

    # Get current max IDs from database to avoid duplicates
    try:
        # Query max triage ID from database
        result = client.schema('raw').table('triage_items').select('id').order('id', desc=True).limit(1).execute()
        if result.data and len(result.data) > 0:
            # Extract number from ID like "T123" -> 123
            max_id_str = result.data[0]['id']
            max_id_num = int(max_id_str.replace('T', ''))
            triage_id_counter = max_id_num + 1
        else:
            triage_id_counter = 1

        # Query max insight ID
        result = client.schema('raw').table('insights').select('insight_id').order('insight_id', desc=True).limit(1).execute()
        if result.data and len(result.data) > 0:
            max_insight_str = result.data[0]['insight_id']
            max_insight_num = int(max_insight_str.replace('I', ''))
            insight_id_counter = max_insight_num + 1
        else:
            insight_id_counter = 1

        print(f"📊 Starting from: T{triage_id_counter:03d}, I{insight_id_counter:03d}\n")
    except Exception as e:
        print(f"⚠️  Could not fetch max IDs: {e}")
        # If no data yet, start from 1
        triage_id_counter = 1
        insight_id_counter = 1

    processed_count = 0
    skipped_count = 0
    total_items = 0
    total_insights = 0

    # Process each file
    for file_path in md_files:
        filename = file_path.name

        print(f"{'─'*80}")
        print(f"📄 {filename}")
        print(f"{'─'*80}")

        # Compute file hash
        file_hash = compute_file_hash(str(file_path))

        # Check if already processed
        if is_file_processed(client, filename, file_hash):
            print(f"  ⏭️  Already processed (unchanged)\n")
            skipped_count += 1
            continue

        # Read file
        try:
            input_text = file_path.read_text(encoding='utf-8').strip()
        except Exception as e:
            print(f"  ❌ Error reading file: {e}\n")
            continue

        date = datetime.now().strftime("%Y-%m-%d")

        # Layer 1: Triage
        try:
            items = run_layer1(input_text, date, triage_id_counter, filename)

            # IMPORTANT: Mark file as processed FIRST (required for foreign key)
            mark_file_processed(client, filename, file_hash, len(items))
            print(f"  ✓ Marked file as processed")

            # Then write triage items
            write_triage_items(client, items, filename)
            print(f"  ✓ Saved {len(items)} items to Supabase")

            total_items += len(items)
            triage_id_counter += len(items)

        except Exception as e:
            print(f"  ❌ Error in Layer 1: {e}\n")
            continue

        # Layer 2: Insights
        try:
            insights, insight_id_counter = run_layer2(items, date, insight_id_counter)

            if insights:
                write_insights(client, insights)
                print(f"  ✓ Saved {len(insights)} insights to Supabase")
                total_insights += len(insights)

        except Exception as e:
            print(f"  ⚠️  Error in Layer 2: {e}")

        processed_count += 1
        print()

    # Final stats
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"✓ Processed: {processed_count} files")
    print(f"⏭️  Skipped: {skipped_count} files (already processed)")
    print(f"📊 Total triage items: {total_items}")
    print(f"💡 Total insights: {total_insights}")

    # Get database stats
    try:
        stats = get_processing_stats(client)
        print(f"\n{'─'*80}")
        print("DATABASE STATS")
        print(f"{'─'*80}")
        print(f"Total files in DB: {stats['total_files']}")
        print(f"Total triage items in DB: {stats['total_items']}")
        print(f"Total insights in DB: {stats['total_insights']}")
    except Exception as e:
        print(f"⚠️  Could not fetch stats: {e}")

    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
