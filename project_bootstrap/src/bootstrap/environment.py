"""Set up virtual environment and install dependencies."""

import subprocess
import sys
from pathlib import Path
from typing import Union, List


def setup(
    project_path: Union[Path, str],
    features: List[str],
) -> None:
    """
    Set up Python virtual environment and install dependencies.

    Args:
        project_path: Path to the project directory
        features: List of features to include (e.g., ['pydantic', 'token-tracking', 'tests'])
    """
    project_path = Path(project_path)
    _setup_python(project_path, features)


def _setup_python(project_path: Path, features: List[str]) -> None:
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
    requirements_content = _build_requirements(features)
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


def _build_requirements(features: List[str]) -> str:
    """Build requirements.txt based on features."""
    # Base requirements for all AI agents
    requirements = [
        "# Core dependencies",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
    ]

    # Add feature-specific requirements
    if "pydantic" in features:
        requirements.extend([
            "",
            "# Pydantic for validation",
            "pydantic>=2.0.0",
        ])

    if "token-tracking" in features:
        requirements.extend([
            "",
            "# Token tracking (built-in with OpenAI SDK)",
        ])

    if "tests" in features:
        requirements.extend([
            "",
            "# Testing",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ])

    # Add logging
    requirements.extend([
        "",
        "# Logging and observability",
        "loguru>=0.7.0",
    ])

    return "\n".join(requirements) + "\n"
