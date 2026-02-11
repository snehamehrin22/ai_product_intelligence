"""Quick test of Google Sheets integration."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from notes_agent.tools_sheets import write_triage_items_to_sheet
from notes_agent.schemas import TriageItem
import os
from dotenv import load_dotenv

load_dotenv()

# Create a sample item
sample = TriageItem(
    id="T001",
    date="2025-02-11",
    raw_context="Testing Google Sheets integration - this is a sample triage item",
    personal_or_work="Work",
    domain="Testing",
    type="Task",
    tags="test, google-sheets, integration",
    niche_signal=False,
    publishable=False
)

print("🧪 Testing Google Sheets integration...\n")

sheet_id = os.getenv('GOOGLE_SHEET_PROMPT1_ID')
print(f"📊 Sheet ID: {sheet_id}\n")

try:
    url = write_triage_items_to_sheet(
        items=[sample],
        sheet_id=sheet_id,
        clear_existing=True
    )
    print(f"\n✅ Success! Check your sheet: {url}")
except Exception as e:
    print(f"\n❌ Error: {e}")
