#!/usr/bin/env python3
"""
Daily automated sync of Obsidian notes to Supabase.

This script:
1. Finds the latest Obsidian markdown file
2. Checks if it's already been processed in Supabase
3. If new/changed, processes it through the triage pipeline
4. Logs all activity for monitoring

Designed to run via cron daily at 10:00 AM.
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.layer1_triage import triage_braindump
from notes_agent.llm_clients import call_openrouter, parse_json_response
from notes_agent.tools_supabase import (
    get_supabase_client,
    compute_file_hash,
    is_file_processed,
    mark_file_processed,
    write_triage_items,
    write_insights
)

# Load environment variables
load_dotenv()

# Setup logging
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f'daily_sync_{datetime.now().strftime("%Y%m%d")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_layer2_prompt() -> str:
    """Load Layer 2 insight generation prompt."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "layer2_insight_generation.txt"
    return prompt_path.read_text(encoding="utf-8")


def find_latest_obsidian_file() -> Path | None:
    """Find the most recently modified Obsidian markdown file."""
    obsidian_path = Path("/Users/snehamehrin/Desktop/obsidian_vaults/obsidian/Personal Context/journal_notes")

    if not obsidian_path.exists():
        logger.error(f"Obsidian vault not found: {obsidian_path}")
        return None

    md_files = list(obsidian_path.glob("*.md"))

    if not md_files:
        logger.warning("No markdown files found in Obsidian vault")
        return None

    # Sort by modification time, newest first
    latest_file = max(md_files, key=lambda p: p.stat().st_mtime)

    logger.info(f"Latest file: {latest_file.name}")
    logger.info(f"Modified: {datetime.fromtimestamp(latest_file.stat().st_mtime)}")

    return latest_file


def run_layer1(input_text: str, date: str, starting_id: int, source_file: str):
    """Run Layer 1 triage."""
    logger.info(f"Running Layer 1 triage...")

    items = triage_braindump(
        raw_text=input_text,
        date=date,
        starting_id=starting_id
    )

    logger.info(f"Generated {len(items)} triage items")
    return items


def run_layer2(triage_items: list, date: str, insight_counter: int):
    """Run Layer 2 insight generation."""
    # Filter items
    skip_types = {"Task", "Technical", "Config"}
    items_to_process = [item for item in triage_items if item.type not in skip_types]

    if not items_to_process:
        logger.info("No items to process for insights (all filtered)")
        return [], insight_counter

    logger.info(f"Generating insights from {len(items_to_process)} items...")

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
            logger.warning("Unexpected format, no insights generated")
            return [], insight_counter

        logger.info(f"Generated {len(insights)} insights")
        return insights, insight_counter + len(insights)

    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return [], insight_counter


def get_next_id_counters(client):
    """Get the next available ID counters from the database."""
    try:
        # Query max triage ID
        result = client.schema('raw').table('triage_items').select('id').order('id', desc=True).limit(1).execute()
        if result.data and len(result.data) > 0:
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

        logger.info(f"Next IDs: T{triage_id_counter:03d}, I{insight_id_counter:03d}")
        return triage_id_counter, insight_id_counter

    except Exception as e:
        logger.warning(f"Could not fetch max IDs: {e}. Starting from T001, I001")
        return 1, 1


def main():
    """Main execution function."""
    logger.info("=" * 80)
    logger.info("DAILY OBSIDIAN SYNC STARTED")
    logger.info("=" * 80)

    # Step 1: Find latest file
    latest_file = find_latest_obsidian_file()
    if not latest_file:
        logger.error("No file to process. Exiting.")
        return 1

    filename = latest_file.name

    # Step 2: Connect to Supabase
    try:
        client = get_supabase_client()
        logger.info("Connected to Supabase")
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return 1

    # Step 3: Check if file already processed
    file_hash = compute_file_hash(str(latest_file))

    if is_file_processed(client, filename, file_hash):
        logger.info(f"File '{filename}' already processed (unchanged). Nothing to do.")
        logger.info("=" * 80)
        return 0

    logger.info(f"File '{filename}' is new or changed. Processing...")

    # Step 4: Read file content
    try:
        input_text = latest_file.read_text(encoding='utf-8').strip()
        logger.info(f"Read {len(input_text)} characters from file")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return 1

    # Step 5: Get next ID counters
    triage_id_counter, insight_id_counter = get_next_id_counters(client)

    date = datetime.now().strftime("%Y-%m-%d")

    # Step 6: Run Layer 1 (Triage)
    try:
        items = run_layer1(input_text, date, triage_id_counter, filename)

        # Mark file as processed FIRST (required for foreign key)
        mark_file_processed(client, filename, file_hash, len(items))
        logger.info("Marked file as processed in database")

        # Write triage items
        write_triage_items(client, items, filename)
        logger.info(f"Saved {len(items)} triage items to Supabase")

    except Exception as e:
        logger.error(f"Error in Layer 1: {e}")
        return 1

    # Step 7: Run Layer 2 (Insights)
    try:
        insights, _ = run_layer2(items, date, insight_id_counter)

        if insights:
            write_insights(client, insights)
            logger.info(f"Saved {len(insights)} insights to Supabase")
        else:
            logger.info("No insights generated")

    except Exception as e:
        logger.warning(f"Error in Layer 2 (non-critical): {e}")

    # Final summary
    logger.info("=" * 80)
    logger.info("SYNC COMPLETED SUCCESSFULLY")
    logger.info(f"File: {filename}")
    logger.info(f"Triage items: {len(items)}")
    logger.info(f"Insights: {len(insights) if insights else 0}")
    logger.info("=" * 80)

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
