"""
Entry point for the notes agent production pipeline.

Usage:
    python scripts/run_pipeline.py [--limit N]

Examples:
    python scripts/run_pipeline.py           # Process up to 10 entries
    python scripts/run_pipeline.py --limit 5 # Process up to 5 entries
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from notes_agent.main_loop import run_pipeline


def main():
    """Run the notes agent pipeline."""
    # Load environment variables
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the notes agent classification pipeline")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of entries to fetch from Notion (default: 10)"
    )

    args = parser.parse_args()

    # Run the pipeline
    run_pipeline(limit=args.limit)


if __name__ == "__main__":
    main()
