"""Create directory structure for bootstrapped projects."""

import re
from pathlib import Path
from typing import Literal


ProjectType = Literal["agent", "api", "cli", "webapp"]
Language = Literal["python", "node"]


def validate_project_name(name: str) -> tuple[bool, str | None]:
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


def create(name: str, project_type: ProjectType, language: Language) -> Path:
    """
    Create the directory structure for a new project.

    Args:
        name: Project name (will be used as directory name)
        project_type: Type of project (agent, api, cli, webapp)
        language: Programming language (python, node)

    Returns:
        Path to the created project directory
    """
    project_path = Path(name)

    if project_path.exists():
        raise FileExistsError(f"Directory {name} already exists")

    # Core directories
    directories = [
        project_path,
        project_path / "tests" / "inputs",
        project_path / "logs",
        project_path / "data",
    ]

    if language == "python":
        directories.extend([
            project_path / "src" / _to_package_name(name),
            project_path / "prompts",
        ])
    elif language == "node":
        directories.extend([
            project_path / "src",
            project_path / "prompts",
        ])

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")

    return project_path


def _to_package_name(name: str) -> str:
    """Convert project name to valid Python package name."""
    return name.replace("-", "_").replace(" ", "_").lower()
