"""Check database statistics and what's been processed."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.tools_supabase import get_supabase_client, get_processing_stats

client = get_supabase_client()

# Get stats
stats = get_processing_stats(client)

print("\n" + "="*80)
print("DATABASE STATISTICS")
print("="*80)
print(f"Total files processed: {stats['total_files']}")
print(f"Total triage items: {stats['total_items']}")
print(f"Total insights: {stats['total_insights']}")

print("\n" + "-"*80)
print("RECENT FILES:")
print("-"*80)
for file in stats['recent_files']:
    print(f"  {file['file_path']:50} | Items: {file['item_count']:3} | {file['processed_at']}")

# Get sample triage items
print("\n" + "-"*80)
print("SAMPLE TRIAGE ITEMS (latest 5):")
print("-"*80)
result = client.schema('raw').table('triage_items').select('id,source_file,type,domain').order('created_at', desc=True).limit(5).execute()
for item in result.data:
    print(f"  {item['id']:6} | {item['source_file']:40} | {item['type']:15} | {item['domain']}")

print("="*80 + "\n")
