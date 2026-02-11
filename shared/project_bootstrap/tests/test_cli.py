"""Tests for CLI module."""

import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from bootstrap import cli


def test_cli_creates_python_agent(monkeypatch):
    """Test CLI creates Python agent project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Mock subprocess to skip venv creation
        with mock.patch("bootstrap.environment.subprocess.run"):
            # Mock sys.argv and call main()
            with mock.patch.object(sys, "argv", ["bootstrap", "my-agent", "--type", "agent", "--lang", "python", "--no-venv"]):
                exit_code = cli.main()

        assert exit_code == 0
        tmpdir_path = Path(tmpdir)
        project_path = tmpdir_path / "my-agent"

        # Check basic structure was created
        assert (project_path / "tests" / "inputs").exists()
        assert (project_path / "src" / "my_agent").exists()
        assert (project_path / ".env").exists()
        assert (project_path / "CLAUDE.md").exists()
        assert (project_path / ".gitignore").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / "pyproject.toml").exists()


def test_cli_with_no_git(monkeypatch):
    """Test CLI with --no-git flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        with mock.patch("bootstrap.environment.subprocess.run"):
            with mock.patch.object(sys, "argv", ["bootstrap", "test-project", "--no-git", "--no-venv"]):
                exit_code = cli.main()

        assert exit_code == 0
        project_path = Path(tmpdir) / "test-project"
        # .git directory should not exist
        assert not (project_path / ".git").exists()


def test_cli_existing_directory_fails(monkeypatch):
    """Test CLI fails gracefully when directory exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        project_name = "existing"

        # Create the directory first
        (tmpdir_path / project_name).mkdir()

        monkeypatch.chdir(tmpdir)

        # Should return error code
        with mock.patch.object(sys, "argv", ["bootstrap", project_name]):
            exit_code = cli.main()

        assert exit_code == 1


def test_cli_invalid_project_name(monkeypatch):
    """Test CLI rejects invalid project names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Project names starting with digits are invalid
        with mock.patch.object(sys, "argv", ["bootstrap", "2fast2furious"]):
            exit_code = cli.main()

        assert exit_code == 1


def test_cli_all_project_types(monkeypatch):
    """Test CLI creates all project types successfully."""
    project_types = ["agent", "api", "cli", "webapp"]

    for ptype in project_types:
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.chdir(tmpdir)

            with mock.patch("bootstrap.environment.subprocess.run"):
                with mock.patch.object(sys, "argv", ["bootstrap", f"test-{ptype}", "--type", ptype, "--no-venv"]):
                    exit_code = cli.main()

            assert exit_code == 0, f"Failed to create {ptype} project"
            project_path = Path(tmpdir) / f"test-{ptype}"
            assert project_path.exists()
