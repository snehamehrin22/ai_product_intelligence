"""Generate comprehensive summary of processed Obsidian files."""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.tools_supabase import get_supabase_client

client = get_supabase_client()

print("\n" + "="*80)
print("OBSIDIAN → SUPABASE PROCESSING SUMMARY")
print("="*80)

# File stats
files_result = client.schema('raw').table('processed_files').select('*').execute()
total_files = len(files_result.data)
total_items_from_files = sum(f['item_count'] for f in files_result.data)

print(f"\n📁 FILES PROCESSED: {total_files}")
print(f"   Total items from files: {total_items_from_files}")

# Triage items stats
items_result = client.schema('raw').table('triage_items').select('*').execute()
total_items = len(items_result.data)

print(f"\n📊 TRIAGE ITEMS: {total_items}")

# Type distribution
types = [item['type'] for item in items_result.data if item.get('type')]
type_counts = Counter(types)
print(f"\n   By Type:")
for type_name, count in type_counts.most_common():
    print(f"      {type_name:25} {count:4}")

# Domain distribution
domains = [item['domain'] for item in items_result.data if item.get('domain')]
domain_counts = Counter(domains)
print(f"\n   By Domain:")
for domain, count in domain_counts.most_common(10):
    print(f"      {domain:25} {count:4}")

# Niche signals
niche_signals = sum(1 for item in items_result.data if item.get('niche_signal'))
publishable = sum(1 for item in items_result.data if item.get('publishable'))

print(f"\n   Niche Signals: {niche_signals} ({niche_signals/total_items*100:.1f}%)")
print(f"   Publishable: {publishable} ({publishable/total_items*100:.1f}%)")

# Personal vs Work
personal_work = [item['personal_or_work'] for item in items_result.data if item.get('personal_or_work')]
pw_counts = Counter(personal_work)
print(f"\n   Personal vs Work:")
for pw, count in pw_counts.items():
    print(f"      {pw:25} {count:4}")

# Insights
insights_result = client.schema('raw').table('insights').select('*').execute()
total_insights = len(insights_result.data)

print(f"\n💡 INSIGHTS GENERATED: {total_insights}")

# Recent files
print(f"\n📄 RECENT FILES (last 10):")
recent = client.schema('raw').table('processed_files').select('file_path,item_count,processed_at').order('processed_at', desc=True).limit(10).execute()
for file in recent.data:
    print(f"   {file['file_path']:50} {file['item_count']:3} items")

print("\n" + "="*80 + "\n")
