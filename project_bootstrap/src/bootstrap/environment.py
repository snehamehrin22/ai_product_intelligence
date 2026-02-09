"""Set up virtual environment and install dependencies."""

import subprocess
import sys
from pathlib import Path
from typing import Literal

from .scaffold import ProjectType, Language


def setup(
    project_path: Path | str,
    language: Language,
    project_type: ProjectType,
) -> None:
    """
    Set up virtual environment and install dependencies.

    Args:
        project_path: Path to the project directory
        language: Programming language (python, node)
        project_type: Type of project (agent, api, cli, webapp)
    """
    project_path = Path(project_path)

    if language == "python":
        _setup_python(project_path, project_type)
    elif language == "node":
        _setup_node(project_path, project_type)


def _setup_python(project_path: Path, project_type: ProjectType) -> None:
    """Set up Python virtual environment."""
    # Create venv
    venv_path = project_path / ".venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        check=True,
        capture_output=True,
    )
    print(f"  ✓ python3 -m venv .venv")

    # Determine Python executable in venv
    python_exe = venv_path / "bin" / "python" if sys.platform != "win32" else venv_path / "Scripts" / "python.exe"

    # Create combined requirements.txt
    requirements_content = _load_python_requirements(project_type)
    req_path = project_path / "requirements.txt"
    req_path.write_text(requirements_content)

    # Install dependencies
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-q", "-r", "requirements.txt"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    print(f"  ✓ pip install -r requirements.txt")


def _setup_node(project_path: Path, project_type: ProjectType) -> None:
    """Set up Node.js project."""
    # npm install
    subprocess.run(
        ["npm", "install"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    print(f"  ✓ npm install")


def _load_python_requirements(project_type: ProjectType) -> str:
    """Load and merge requirements for Python project."""
    template_dir = Path(__file__).parent / "templates" / "python"

    # Load base requirements
    base_req = (template_dir / "requirements-base.txt").read_text()

    # Load type-specific requirements
    type_req = (template_dir / f"requirements-{project_type}.txt").read_text()

    # Merge them
    lines = base_req.strip().split("\n") + type_req.strip().split("\n")
    # Remove duplicates while preserving order
    seen = set()
    unique_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and line not in seen:
            unique_lines.append(line)
            seen.add(line)

    return "\n".join(unique_lines) + "\n"
