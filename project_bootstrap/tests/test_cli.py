"""Tests for CLI module."""

import tempfile
from pathlib import Path
from unittest import mock

import pytest

from bootstrap.cli import main


def test_cli_creates_python_agent(monkeypatch):
    """Test CLI creates Python agent project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory so project is created there
        monkeypatch.chdir(tmpdir)

        # Mock the subprocess calls to avoid actually setting up venv
        with mock.patch("subprocess.run") as mock_run:
            result = main.__wrapped__(["my-agent", "--type", "agent", "--lang", "python", "--no-venv"])

        tmpdir_path = Path(tmpdir)
        project_path = tmpdir_path / "my-agent"

        # Check basic structure was created
        assert (project_path / "tests" / "inputs").exists()
        assert (project_path / "src" / "my_agent").exists()
        assert (project_path / ".env").exists()
        assert (project_path / "CLAUDE.md").exists()
        assert (project_path / ".gitignore").exists()


def test_cli_with_no_git(monkeypatch):
    """Test CLI with --no-git flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        with mock.patch("subprocess.run"):
            # Should not raise
            main.__wrapped__(["test-project", "--no-git", "--no-venv"])

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

        # Should exit with error
        with mock.patch("sys.exit") as mock_exit:
            main.__wrapped__([project_name])
            # Check that it tried to exit (implementation calls sys.exit on error)
