"""
Script to create the two test Google Sheets for prompt validation.
Run this once to set up the sheets, then share them with your team.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from notes_agent.tools_sheets import create_test_sheets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Create test sheets."""
    print("🔧 Setting up test Google Sheets...\n")

    # Get sheet names from environment
    prompt1_name = os.getenv('GOOGLE_SHEET_PROMPT1', 'Triage Prompt1 Testing')
    prompt2_name = os.getenv('GOOGLE_SHEET_PROMPT2', 'Triage Prompt2 Testing')

    try:
        url1, url2 = create_test_sheets(prompt1_name, prompt2_name)

        print("\n✅ Test sheets ready!\n")
        print(f"📊 Prompt1 Testing: {url1}")
        print(f"📊 Prompt2 Testing: {url2}")
        print("\n💡 Next steps:")
        print("   1. Open both sheets")
        print("   2. Share them with your team (if needed)")
        print("   3. Run test_layer1.py with --output-sheets flag")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check that config/google_service_account.json exists")
        print("   - Verify your service account has Google Sheets API enabled")
        print("   - Make sure you've granted necessary permissions")
        sys.exit(1)


if __name__ == '__main__':
    main()
