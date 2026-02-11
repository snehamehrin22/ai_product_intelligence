"""
View feedback analysis report.

Usage:
    python scripts/view_feedback_report.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.carousel_pipeline.feedback_analyzer import (
    generate_feedback_report,
    display_feedback_report
)


def main():
    """Generate and display feedback report."""
    print("\n" + "="*70)
    print("📊 GENERATING FEEDBACK REPORT")
    print("="*70)

    try:
        report = generate_feedback_report()
        display_feedback_report(report)

        # Optionally save report
        save = input("\n💾 Save report to JSON? (y/n): ").lower()
        if save == 'y':
            report_path = "data/feedback/feedback_report.json"
            Path(report_path).parent.mkdir(parents=True, exist_ok=True)
            Path(report_path).write_text(json.dumps(report, indent=2))
            print(f"   ✓ Saved to: {report_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
