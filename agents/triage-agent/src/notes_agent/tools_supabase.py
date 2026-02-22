"""
Supabase integration for triage agent.
Handles duplicate detection and storage of triage items and insights.
"""
import hashlib
import os
from typing import List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from .schemas import TriageItem

load_dotenv()


def get_supabase_client() -> Client:
    """Create and return Supabase client configured for 'raw' schema."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    # Create client
    client = create_client(url, key)

    return client


def compute_file_hash(file_path: str) -> str:
    """
    Compute SHA256 hash of file contents.
    Used to detect if file content has changed.
    """
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def is_file_processed(client: Client, file_path: str, file_hash: str) -> bool:
    """
    Check if file has already been processed.

    Returns:
        True if file exists with same hash (skip processing)
        False if file is new or content changed (process it)
    """
    try:
        result = client.schema('raw').table('processed_files').select('file_hash').eq('file_path', file_path).execute()

        if not result.data:
            # File never processed
            return False

        stored_hash = result.data[0]['file_hash']

        if stored_hash == file_hash:
            # Same content, already processed
            return True
        else:
            # Content changed, reprocess
            print(f"  ⚠️  File content changed, will reprocess")
            return False

    except Exception as e:
        print(f"  ⚠️  Error checking file status: {e}")
        return False


def mark_file_processed(client: Client, file_path: str, file_hash: str, item_count: int):
    """
    Mark file as processed in database.
    Updates existing record if file was reprocessed.
    """
    try:
        # Try to upsert (insert or update)
        data = {
            'file_path': file_path,
            'file_hash': file_hash,
            'item_count': item_count
        }

        # Upsert: insert if new, update if exists
        client.schema('raw').table('processed_files').upsert(data, on_conflict='file_path').execute()

    except Exception as e:
        raise Exception(f"Failed to mark file as processed: {e}")


def write_triage_items(
    client: Client,
    items: List[TriageItem],
    source_file: str
) -> int:
    """
    Write triage items to Supabase.

    Args:
        client: Supabase client
        items: List of TriageItem objects
        source_file: Source file path

    Returns:
        Number of items written
    """
    if not items:
        return 0

    try:
        # Convert items to dict format for Supabase
        records = []
        for item in items:
            records.append({
                'id': item.id,
                'source_file': source_file,
                'date': item.date,
                'raw_context': item.raw_context,
                'personal_or_work': item.personal_or_work,
                'domain': item.domain,
                'type': item.type,
                'tags': item.tags,
                'niche_signal': item.niche_signal,
                'publishable': item.publishable
            })

        # Delete existing items from this file (if reprocessing)
        client.schema('raw').table('triage_items').delete().eq('source_file', source_file).execute()

        # Insert new items
        client.schema('raw').table('triage_items').insert(records).execute()

        return len(records)

    except Exception as e:
        raise Exception(f"Failed to write triage items: {e}")


def write_insights(client: Client, insights: List[dict]) -> int:
    """
    Write insights to Supabase.

    Args:
        client: Supabase client
        insights: List of insight dicts

    Returns:
        Number of insights written
    """
    if not insights:
        return 0

    try:
        # Convert insights to Supabase format
        records = []
        for ins in insights:
            records.append({
                'insight_id': ins.get('insight_id', ''),
                'linked_triage_ids': ins.get('linked_triage_ids', ''),
                'insight': ins.get('insight', ''),
                'tags': ins.get('tags', ''),
                'publishable_angle': ins.get('publishable_angle', None),
                'status': ins.get('status', 'Draft')
            })

        # Upsert insights (update if exists, insert if new)
        client.schema('raw').table('insights').upsert(records, on_conflict='insight_id').execute()

        return len(records)

    except Exception as e:
        raise Exception(f"Failed to write insights: {e}")


def get_all_triage_items(client: Client, limit: Optional[int] = None) -> List[dict]:
    """
    Fetch all triage items from Supabase.

    Args:
        client: Supabase client
        limit: Max number of items to fetch (None = all)

    Returns:
        List of triage items as dicts
    """
    try:
        query = client.schema('raw').table('triage_items').select('*').order('created_at', desc=True)

        if limit:
            query = query.limit(limit)

        result = query.execute()
        return result.data

    except Exception as e:
        raise Exception(f"Failed to fetch triage items: {e}")


def get_processing_stats(client: Client) -> dict:
    """
    Get statistics about processed files and items.

    Returns:
        Dict with stats: total_files, total_items, total_insights, etc.
    """
    try:
        # Count processed files
        files_result = client.schema('raw').table('processed_files').select('id', count='exact').execute()
        total_files = files_result.count

        # Count triage items
        items_result = client.schema('raw').table('triage_items').select('id', count='exact').execute()
        total_items = items_result.count

        # Count insights
        insights_result = client.schema('raw').table('insights').select('insight_id', count='exact').execute()
        total_insights = insights_result.count

        # Get recent files
        recent_files = client.schema('raw').table('processed_files').select('file_path,processed_at,item_count').order('processed_at', desc=True).limit(5).execute()

        return {
            'total_files': total_files,
            'total_items': total_items,
            'total_insights': total_insights,
            'recent_files': recent_files.data
        }

    except Exception as e:
        raise Exception(f"Failed to get stats: {e}")
