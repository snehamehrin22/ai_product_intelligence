"""Tests for scaffold module."""

import tempfile
from pathlib import Path

import pytest

from bootstrap import scaffold


def test_create_python_agent():
    """Test creating a Python agent project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        project_path = scaffold.create("test-agent", "agent", "python")

        # Check that project was created in current directory
        assert project_path.exists()
        assert (project_path / "tests" / "inputs").exists()
        assert (project_path / "src" / "test_agent").exists()
        assert (project_path / "logs").exists()
        assert (project_path / "prompts").exists()


def test_create_node_api():
    """Test creating a Node.js API project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        project_path = scaffold.create("test-api", "api", "node")

        assert project_path.exists()
        assert (project_path / "tests" / "inputs").exists()
        assert (project_path / "src").exists()


def test_create_existing_directory_fails():
    """Test that creating a project in existing directory fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        # Create first project
        project_path = scaffold.create("existing", "agent", "python")

        # Try to create again - should fail
        with pytest.raises(FileExistsError):
            scaffold.create("existing", "agent", "python")


def test_package_name_conversion():
    """Test project name to package name conversion."""
    assert scaffold._to_package_name("my-project") == "my_project"
    assert scaffold._to_package_name("my project") == "my_project"
    assert scaffold._to_package_name("MyProject") == "myproject"
