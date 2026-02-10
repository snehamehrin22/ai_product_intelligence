"""Initialize git repository and .gitignore."""

import subprocess
from pathlib import Path
from typing import Union


def init(project_path: Union[Path, str], language: str) -> None:
    """
    Initialize git repository (gitignore handled by configs.py now).

    Args:
        project_path: Path to the project directory
        language: Programming language (always python for AI agents)
    """
    project_path = Path(project_path)

    # Initialize git
    subprocess.run(
        ["git", "init"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    print(f"  ✓ git init")


def auto_commit(project_path: Union[Path, str]) -> None:
    """
    Create initial commit with scaffolded files.

    Args:
        project_path: Path to the project directory
    """
    project_path = Path(project_path)

    try:
        # Stage all files
        subprocess.run(
            ["git", "add", "."],
            cwd=project_path,
            check=True,
            capture_output=True,
        )

        # Create initial commit
        subprocess.run(
            ["git", "commit", "-m", "chore: initial scaffold with project-bootstrap"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        print(f"  ✓ initial commit")
    except subprocess.CalledProcessError:
        # Silently skip if commit fails (e.g., git not configured)
        pass
