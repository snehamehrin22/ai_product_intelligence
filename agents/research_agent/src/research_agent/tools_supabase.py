"""
Supabase integration for fetching observations.
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> Client:
    """Create and return Supabase client configured for 'raw' schema."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    client = create_client(url, key)
    return client


def get_observation(observation_id: str) -> Optional[dict]:
    """
    Fetch an observation from Supabase by ID.

    Args:
        observation_id: The triage item ID (e.g., 'T042')

    Returns:
        Observation dict or None if not found
    """
    client = get_supabase_client()

    try:
        result = client.schema('raw').table('triage_items').select('*').eq('id', observation_id).execute()

        if not result.data:
            return None

        return result.data[0]

    except Exception as e:
        raise Exception(f"Failed to fetch observation {observation_id}: {e}")
