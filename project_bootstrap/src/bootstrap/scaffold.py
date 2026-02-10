"""Create directory structure for bootstrapped projects."""

import re
from pathlib import Path
from typing import Optional, Tuple, List


def validate_project_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate project name.

    Args:
        name: Project name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if empty
    if not name or not name.strip():
        return False, "Project name cannot be empty"

    # Check length
    if len(name) > 50:
        return False, "Project name must be 50 characters or less"

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_-]*$", name):
        return False, "Project name must start with letter or underscore and contain only alphanumerics, hyphens, and underscores"

    # Check for reserved names
    reserved = {"bootstrap", "test", "src", "lib", "bin", "etc", "var"}
    if name.lower() in reserved:
        return False, f"'{name}' is a reserved name, please choose another"

    return True, None


def create(name: str, features: List[str]) -> Path:
    """
    Create the directory structure for a new AI agent project.

    Args:
        name: Project name (will be used as directory name)
        features: List of features to include (e.g., ['pydantic', 'token-tracking', 'tests'])

    Returns:
        Path to the created project directory
    """
    project_path = Path(name)

    if project_path.exists():
        raise FileExistsError(f"Directory {name} already exists")

    # Core directories for AI agent
    directories = [
        project_path,
        project_path / "src" / _to_package_name(name),
        project_path / "prompts",
        project_path / "scripts",
        project_path / "logs",
    ]

    # Add tests directory if tests feature is enabled
    if "tests" in features:
        directories.extend([
            project_path / "tests" / "inputs",
            project_path / "tests" / "outputs",
        ])

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")

    return project_path


def _to_package_name(name: str) -> str:
    """Convert project name to valid Python package name."""
    return name.replace("-", "_").replace(" ", "_").lower()
