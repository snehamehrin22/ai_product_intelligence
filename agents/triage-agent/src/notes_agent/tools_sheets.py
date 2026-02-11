"""
Google Sheets integration for triage output.
Used for intermediate testing and validation.
"""
from pathlib import Path
from typing import List, Optional
import gspread
from google.oauth2.service_account import Credentials
from .schemas import TriageItem
import os


# Google Sheets API scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def get_sheets_client() -> gspread.Client:
    """
    Authenticate and return Google Sheets client.

    Returns:
        Authenticated gspread client

    Raises:
        FileNotFoundError: If service account JSON not found
        ValueError: If authentication fails
    """
    # Get credentials path from environment or use default
    creds_path = os.getenv(
        'GOOGLE_SERVICE_ACCOUNT_PATH',
        str(Path(__file__).parent.parent.parent / 'config' / 'google_service_account.json')
    )

    if not Path(creds_path).exists():
        raise FileNotFoundError(
            f"Google service account JSON not found at: {creds_path}\n"
            "Please add your credentials or set GOOGLE_SERVICE_ACCOUNT_PATH"
        )

    try:
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        raise ValueError(f"Failed to authenticate with Google Sheets: {e}")


def write_triage_items_to_sheet(
    items: List[TriageItem],
    sheet_id: str,
    worksheet_name: str = "Sheet1",
    clear_existing: bool = False
) -> str:
    """
    Write triage items to a Google Sheet.

    Args:
        items: List of TriageItem objects to write
        sheet_id: Google Sheet ID (from URL)
        worksheet_name: Name of the worksheet/tab (default: "Sheet1")
        clear_existing: If True, clear existing data before writing

    Returns:
        URL of the Google Sheet

    Raises:
        ValueError: If sheet not found or write fails
    """
    if not items:
        print("⚠️  No items to write to sheet")
        return ""

    client = get_sheets_client()

    try:
        # Open the spreadsheet by ID
        sheet = client.open_by_key(sheet_id)
        print(f"✓ Opened sheet: {sheet.title}")

        # Get or create worksheet
        try:
            worksheet = sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=100, cols=10)

        # Clear existing data if requested
        if clear_existing:
            worksheet.clear()

        # Prepare header row
        headers = [
            'ID',
            'Date',
            'Personal/Work',
            'Domain',
            'Type',
            'Tags',
            'Niche Signal',
            'Publishable',
            'Raw Context'
        ]

        # Prepare data rows
        rows = [headers]
        for item in items:
            rows.append([
                item.id,
                item.date,
                item.personal_or_work,
                item.domain,
                item.type,
                item.tags,
                'TRUE' if item.niche_signal else 'FALSE',
                'TRUE' if item.publishable else 'FALSE',
                item.raw_context
            ])

        # Write to sheet
        worksheet.update('A1', rows)

        # Format header row (bold)
        worksheet.format('A1:I1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })

        # Auto-resize columns
        worksheet.columns_auto_resize(0, len(headers) - 1)

        print(f"✓ Wrote {len(items)} items to '{sheet.title}' → '{worksheet_name}'")
        print(f"  URL: {sheet.url}")

        return sheet.url

    except Exception as e:
        raise ValueError(f"Failed to write to Google Sheet: {e}")


def create_test_sheets(
    prompt1_name: str = "Triage Prompt1 Testing",
    prompt2_name: str = "Triage Prompt2 Testing"
) -> tuple[str, str]:
    """
    Create two test sheets for prompt validation.

    Args:
        prompt1_name: Name for first test sheet
        prompt2_name: Name for second test sheet

    Returns:
        Tuple of (prompt1_url, prompt2_url)
    """
    client = get_sheets_client()

    urls = []
    for name in [prompt1_name, prompt2_name]:
        try:
            sheet = client.open(name)
            print(f"✓ Sheet already exists: {name}")
        except gspread.SpreadsheetNotFound:
            sheet = client.create(name)
            print(f"✓ Created new sheet: {name}")

        urls.append(sheet.url)

    return tuple(urls)


def append_to_sheet(
    items: List[TriageItem],
    sheet_id: str,
    worksheet_name: str = "Sheet1"
) -> str:
    """
    Append triage items to existing sheet (doesn't overwrite).

    Args:
        items: List of TriageItem objects to append
        sheet_id: Google Sheet ID (from URL)
        worksheet_name: Name of the worksheet/tab

    Returns:
        URL of the Google Sheet
    """
    if not items:
        return ""

    client = get_sheets_client()

    try:
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(worksheet_name)

        # Prepare data rows (no headers)
        rows = []
        for item in items:
            rows.append([
                item.id,
                item.date,
                item.personal_or_work,
                item.domain,
                item.type,
                item.tags,
                'TRUE' if item.niche_signal else 'FALSE',
                'TRUE' if item.publishable else 'FALSE',
                item.raw_context
            ])

        # Append to sheet
        worksheet.append_rows(rows)

        print(f"✓ Appended {len(items)} items to '{sheet.title}' → '{worksheet_name}'")

        return sheet.url

    except Exception as e:
        raise ValueError(f"Failed to append to Google Sheet: {e}")
