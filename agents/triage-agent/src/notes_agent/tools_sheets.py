"""
Google Sheets integration for triage output.
Used for intermediate testing and validation.
"""
from pathlib import Path
from typing import List, Optional
import gspread
from google.oauth2.service_account import Credentials
from .schemas import TriageItem, TriageEvaluation
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
    clear_existing: bool = False,
    prompt_version: Optional[str] = None
) -> str:
    """
    Write triage items to a Google Sheet.

    Args:
        items: List of TriageItem objects to write
        sheet_id: Google Sheet ID (from URL)
        worksheet_name: Name of the worksheet/tab (default: "Sheet1")
        clear_existing: If True, clear existing data before writing
        prompt_version: Optional label for which prompt was used (e.g., "prompt1", "v2.3")

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

        # Add metadata row if prompt version specified
        rows = []
        if prompt_version:
            rows.append(['Prompt Version:', prompt_version])
            rows.append([])  # Empty row

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
        rows.append(headers)
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

        # Format headers and metadata
        if prompt_version:
            # Format prompt version row (bold, highlighted)
            worksheet.format('A1:B1', {
                'textFormat': {'bold': True, 'fontSize': 11},
                'backgroundColor': {'red': 1.0, 'green': 0.9, 'blue': 0.6}
            })
            # Format header row (bold)
            worksheet.format('A3:I3', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
        else:
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


def write_evaluation_to_sheet(
    evaluation: TriageEvaluation,
    sheet_id: str,
    worksheet_name: str = "Evaluation"
) -> str:
    """
    Write evaluation results to a Google Sheet.

    Args:
        evaluation: TriageEvaluation object
        sheet_id: Google Sheet ID (from URL)
        worksheet_name: Name of the worksheet/tab (default: "Evaluation")

    Returns:
        URL of the Google Sheet
    """
    client = get_sheets_client()

    try:
        sheet = client.open_by_key(sheet_id)

        # Get or create worksheet
        try:
            worksheet = sheet.worksheet(worksheet_name)
            worksheet.clear()  # Clear existing evaluation
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=100, cols=10)

        # Header
        headers = [
            'Prompt Version',
            'Overall Score',
            'Num Items',
            'Recommendation',
            'Strengths',
            'Weaknesses'
        ]

        # Summary row
        summary_row = [
            evaluation.prompt_version,
            f"{evaluation.overall_score:.2f}",
            str(evaluation.num_items),
            evaluation.recommendation,
            evaluation.strengths,
            evaluation.weaknesses
        ]

        # Per-item headers
        item_headers = [
            'Item ID',
            'Completeness',
            'Classification',
            'Granularity',
            'Tag Quality',
            'Niche Signal',
            'Publishable',
            'Reasoning'
        ]

        # Per-item rows
        item_rows = []
        for item_eval in evaluation.item_evaluations:
            item_rows.append([
                item_eval.item_id,
                item_eval.completeness,
                item_eval.classification_accuracy,
                item_eval.granularity,
                item_eval.tag_quality,
                item_eval.niche_signal_accuracy,
                item_eval.publishability_accuracy,
                item_eval.reasoning
            ])

        # Combine all rows
        all_rows = [
            headers,
            summary_row,
            [],  # Empty row
            item_headers
        ] + item_rows

        # Write to sheet
        worksheet.update('A1', all_rows)

        # Format headers (bold)
        worksheet.format('A1:F1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        worksheet.format('A4:H4', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })

        # Highlight overall score
        score_color = {
            'red': 0.8 if evaluation.overall_score < 3 else 0.6 if evaluation.overall_score < 4 else 0.8,
            'green': 0.8 if evaluation.overall_score >= 4 else 0.6,
            'blue': 0.6
        }
        worksheet.format('B2', {'backgroundColor': score_color, 'textFormat': {'bold': True}})

        # Auto-resize columns
        worksheet.columns_auto_resize(0, len(headers) - 1)

        print(f"✓ Wrote evaluation to '{sheet.title}' → '{worksheet_name}'")
        print(f"  URL: {sheet.url}")

        return sheet.url

    except Exception as e:
        raise ValueError(f"Failed to write evaluation to Google Sheet: {e}")
