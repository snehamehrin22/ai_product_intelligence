"""Create directory structure for bootstrapped projects."""

import os
from pathlib import Path
from typing import Literal


ProjectType = Literal["agent", "api", "cli", "webapp"]
Language = Literal["python", "node"]


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
