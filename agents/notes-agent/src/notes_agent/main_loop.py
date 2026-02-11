"""
Main orchestration loop - deterministic control flow.
Python controls everything. LLM only does reasoning (split, classify).
"""
import time
from typing import List
from .schemas import NotionEntry, CognitiveBlock
from .splitter import split_into_blocks
from .classifiers.llm_classifier import classify_block
from .enforcement import should_save
from .logging_utils import log_decision, log_metrics, log_entry_processed
from . import tools


def process_single_entry(entry: NotionEntry) -> tuple[int, int, int]:
    """
    Process a single Notion entry: split → classify → save.

    Args:
        entry: NotionEntry to process

    Returns:
        Tuple of (blocks_processed, blocks_saved, errors)
    """
    start_time = time.time()

    print(f"\n{'='*80}")
    print(f"Processing entry: {entry.id}")
    print(f"Created: {entry.created_time}")
    print(f"Content preview: {entry.content[:100]}...")
    print(f"{'='*80}\n")

    # Step 1: Split into cognitive blocks
    print("🔪 Splitting into blocks...")
    try:
        blocks = split_into_blocks(entry.content)
        print(f"✓ Split into {len(blocks)} blocks\n")
    except Exception as e:
        print(f"❌ Error splitting entry: {e}")
        return 0, 0, 1

    # Step 2: Classify each block
    blocks_processed = 0
    blocks_saved = 0
    errors = 0

    for block in blocks:
        blocks_processed += 1
        print(f"[{block.block_id}] {block.block_name}")
        print(f"  Text: {block.block_text[:80]}...")

        try:
            # Classify
            classification = classify_block(block)

            # Enforce confidence threshold
            save_it, reason = should_save(classification, confidence_threshold=0.7)

            if save_it:
                # Write to Supabase
                success = tools.write_classification_to_supabase(
                    notion_entry_id=entry.id,
                    block_name=block.block_name,
                    classification=classification
                )

                if success:
                    blocks_saved += 1
                    print(f"  ✓ Saved (confidence: {classification.confidence})")
                    log_decision(block.block_id, block.block_text, classification, True, reason)
                else:
                    print(f"  ⚠️ Write failed but no error raised")
                    log_decision(block.block_id, block.block_text, classification, False, "write_failed")
            else:
                print(f"  ⏭️  Skipped: {reason}")
                log_decision(block.block_id, block.block_text, classification, False, reason)

        except Exception as e:
            errors += 1
            print(f"  ❌ Error: {e}")
            log_decision(block.block_id, block.block_text, None, False, "classification_error", str(e))

        print()

    # Step 3: Mark entry as processed
    try:
        tools.mark_entry_as_processed(entry.id, len(blocks))
        print(f"✓ Marked entry as processed\n")
    except Exception as e:
        print(f"⚠️ Could not mark as processed: {e}\n")

    # Log completion
    duration = time.time() - start_time
    log_entry_processed(entry.id, len(blocks), duration)

    return blocks_processed, blocks_saved, errors


def run_pipeline(limit: int = 10) -> None:
    """
    Main pipeline: Fetch → Process → Log.

    Args:
        limit: Maximum number of entries to fetch
    """
    print("\n" + "="*80)
    print("NOTES AGENT PIPELINE")
    print("="*80)

    # Fetch latest entries from Notion
    print(f"\n📥 Fetching up to {limit} entries from Notion...")
    try:
        entries = tools.fetch_latest_notion_entries(limit=limit)
        print(f"✓ Found {len(entries)} entries\n")
    except Exception as e:
        print(f"❌ Error fetching from Notion: {e}")
        return

    # Filter out already processed
    print("🔍 Checking for already processed entries...")
    unprocessed_entries = []
    for entry in entries:
        if tools.check_already_processed(entry.id):
            print(f"  ⏭️  Skipping {entry.id} (already processed)")
        else:
            unprocessed_entries.append(entry)

    print(f"✓ {len(unprocessed_entries)} unprocessed entries\n")

    if not unprocessed_entries:
        print("🎉 All entries already processed!")
        return

    # Process each entry
    total_blocks = 0
    total_saved = 0
    total_errors = 0

    for entry in unprocessed_entries:
        blocks, saved, errors = process_single_entry(entry)
        total_blocks += blocks
        total_saved += saved
        total_errors += errors

    # Log final metrics
    print("="*80)
    print("PIPELINE COMPLETE")
    print("="*80)
    print(f"Entries processed: {len(unprocessed_entries)}")
    print(f"Total blocks: {total_blocks}")
    print(f"Blocks saved: {total_saved}")
    print(f"Blocks skipped: {total_blocks - total_saved - total_errors}")
    print(f"Errors: {total_errors}")
    print(f"Save rate: {(total_saved / total_blocks * 100):.1f}%" if total_blocks > 0 else "0%")
    print("="*80 + "\n")

    log_metrics(
        total_entries=len(unprocessed_entries),
        total_blocks=total_blocks,
        blocks_saved=total_saved,
        blocks_skipped=total_blocks - total_saved - total_errors,
        errors=total_errors
    )
