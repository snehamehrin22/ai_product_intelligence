"""Command-line interface for project-bootstrap."""

import argparse
import sys
from pathlib import Path

from . import scaffold, git, environment, configs


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="bootstrap",
        description="Scaffold AI agent and application projects with golden templates",
    )

    parser.add_argument(
        "name",
        help="Project name (will be used as directory name)",
    )

    parser.add_argument(
        "--type",
        choices=["agent", "api", "cli", "webapp"],
        default="agent",
        help="Project type (default: agent)",
    )

    parser.add_argument(
        "--lang",
        choices=["python", "node"],
        default="python",
        help="Programming language (default: python)",
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
        # Step 1: Create directory structure
        print(f"\nStep 1/4: Scaffolding directories...")
        project_path = scaffold.create(args.name, args.type, args.lang)

        # Step 2: Initialize git
        if not args.no_git:
            print(f"\nStep 2/4: Initializing git...")
            git.init(project_path, args.lang)
        else:
            print(f"\nStep 2/4: Skipping git (--no-git)")

        # Step 3: Set up environment
        if not args.no_venv:
            print(f"\nStep 3/4: Setting up environment...")
            environment.setup(project_path, args.lang, args.type)
        else:
            print(f"\nStep 3/4: Skipping environment setup (--no-venv)")

        # Step 4: Generate configs
        print(f"\nStep 4/4: Generating configuration files...")
        configs.generate(project_path, args.name, args.type, args.lang)

        # Success message
        print(f"\n✓ {args.name} ready!\n")
        print(f"  cd {args.name} && code .\n")

        return 0

    except FileExistsError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
