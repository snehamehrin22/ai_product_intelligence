"""Initialize git repository and .gitignore."""

import subprocess
from pathlib import Path
from typing import Literal

from .scaffold import ProjectType, Language


def init(project_path: Path | str, language: Language) -> None:
    """
    Initialize git repository and create .gitignore.

    Args:
        project_path: Path to the project directory
        language: Programming language (python, node)
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

    # Create .gitignore
    gitignore_content = _load_gitignore(language)
    gitignore_path = project_path / ".gitignore"
    gitignore_path.write_text(gitignore_content)
    print(f"  ✓ .gitignore")


def auto_commit(project_path: Path | str) -> None:
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


def _load_gitignore(language: Language) -> str:
    """Load .gitignore template for the language."""
    template_path = Path(__file__).parent / "templates" / "gitignore" / f"{language}.txt"
    return template_path.read_text()
