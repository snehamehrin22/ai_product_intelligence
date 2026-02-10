"""Command-line interface for project-bootstrap."""

import argparse
import subprocess
import sys
from pathlib import Path

from . import scaffold, git, environment, configs

__version__ = "0.3.0"


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="bootstrap",
        description="Scaffold AI agent and application projects with golden templates",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "name",
        help="Project name (will be used as directory name)",
    )

    parser.add_argument(
        "--llm",
        choices=["openai", "deepseek", "anthropic"],
        default="openai",
        help="LLM provider (default: openai)",
    )

    parser.add_argument(
        "--features",
        help="Comma-separated features to include (e.g., pydantic,token-tracking,tests)",
        default="pydantic,token-tracking,tests",
    )

    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git initialization",
    )

    parser.add_argument(
        "--no-venv",
        action="store_true",
        help="Skip virtual environment setup",
    )

    args = parser.parse_args()

    try:
        # Validate project name first
        is_valid, error_msg = scaffold.validate_project_name(args.name)
        if not is_valid:
            print(f"\n✗ Invalid project name: {error_msg}", file=sys.stderr)
            return 1

        # Parse features
        features = [f.strip() for f in args.features.split(",")]

        # Step 1: Create directory structure
        print(f"\nStep 1/5: Scaffolding directories...")
        project_path = scaffold.create(args.name, features)

        # Step 2: Initialize git
        if not args.no_git:
            print(f"\nStep 2/5: Initializing git...")
            git.init(project_path, "python")
        else:
            print(f"\nStep 2/5: Skipping git (--no-git)")

        # Step 3: Set up environment
        if not args.no_venv:
            print(f"\nStep 3/5: Setting up environment...")
            environment.setup(project_path, features)
        else:
            print(f"\nStep 3/5: Skipping environment setup (--no-venv)")

        # Step 4: Generate configs
        print(f"\nStep 4/5: Generating configuration files...")
        configs.generate(project_path, args.name, args.llm, features)

        # Step 5: Auto-commit if git enabled
        if not args.no_git:
            print(f"\nStep 5/5: Creating initial commit...")
            git.auto_commit(project_path)
        else:
            print(f"\nStep 5/5: Skipping commit (--no-git)")

        # Success message
        print(f"\n✓ {args.name} ready!\n")
        print(f"  cd {args.name}")
        print(f"  source .venv/bin/activate")
        print(f"  # Add your API keys to .env")
        print(f"  pytest  # Run tests")
        print(f"  python scripts/run_agent.py  # Run the agent")
        print(f"  code .\n")

        return 0

    except FileExistsError as e:
        print(f"\n✗ Error: Directory already exists", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error: Failed to execute command", file=sys.stderr)
        print(f"  Command: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"  Exit code: {e.returncode}", file=sys.stderr)
        if args.lang == "python":
            print(f"\n  Tip: Check your internet connection and Python installation", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
