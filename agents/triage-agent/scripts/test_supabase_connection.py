"""Test Supabase connection."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.tools_supabase import get_supabase_client
import traceback

try:
    print("Testing Supabase connection...")
    client = get_supabase_client()
    print("✓ Client created successfully")

    # Test query
    print("\nTesting query to raw.processed_files...")
    result = client.schema('raw').table('processed_files').select('*').limit(1).execute()
    print(f"✓ Query successful, returned {len(result.data)} rows")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
