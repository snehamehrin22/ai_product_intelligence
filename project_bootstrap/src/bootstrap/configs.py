"""Generate configuration files from templates."""

from pathlib import Path
from typing import Literal

from jinja2 import Environment, FileSystemLoader

from .scaffold import ProjectType, Language


def generate(
    project_path: Path | str,
    project_name: str,
    project_type: ProjectType,
    language: Language,
) -> None:
    """
    Generate all configuration files from templates.

    Args:
        project_path: Path to the project directory
        project_name: Name of the project
        project_type: Type of project (agent, api, cli, webapp)
        language: Programming language (python, node)
    """
    project_path = Path(project_path)
    package_name = _to_package_name(project_name)

    context = {
        "project_name": project_name,
        "package_name": package_name,
        "project_type": project_type,
        "language": language,
        "api_name": project_name.replace("-", "_"),
    }

    # Setup Jinja2
    template_dir = Path(__file__).parent / "templates"
    jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Generate .env
    _generate_env(project_path, context)

    # Generate CLAUDE.md
    _generate_claude_md(project_path, context, template_dir)

    # Generate language-specific files
    if language == "python":
        _generate_python_files(project_path, context, jinja_env)


def _generate_env(project_path: Path, context: dict) -> None:
    """Generate .env file."""
    template_path = Path(__file__).parent / "templates" / "env" / "default.env"
    content = template_path.read_text()

    # Simple substitution for .env (not using Jinja2 to avoid issues)
    content = content.replace("{{ project_name }}", context["project_name"])

    env_path = project_path / ".env"
    env_path.write_text(content)

    # Create .env.example
    example_content = content.replace(context["project_name"], "my-project")
    example_path = project_path / ".env.example"
    example_path.write_text(example_content)

    print(f"  ✓ .env + .env.example")


def _generate_claude_md(
    project_path: Path,
    context: dict,
    template_dir: Path,
) -> None:
    """Generate CLAUDE.md from templates."""
    base_path = template_dir / "claude_md" / "base.md"
    base_content = base_path.read_text()

    # Substitute base template
    base_content = base_content.replace("{{ project_name }}", context["project_name"])
    base_content = base_content.replace("{{ package_name }}", context["package_name"])

    # Add type-specific additions
    type_addon_path = template_dir / "claude_md" / f"{context['project_type']}.md"
    if type_addon_path.exists():
        addon_content = type_addon_path.read_text()
        addon_content = addon_content.replace("{{ project_name }}", context["project_name"])
        addon_content = addon_content.replace("{{ package_name }}", context["package_name"])
        addon_content = addon_content.replace("{{ api_name }}", context["api_name"])
        base_content += "\n\n" + addon_content

    claude_md_path = project_path / "CLAUDE.md"
    claude_md_path.write_text(base_content)
    print(f"  ✓ CLAUDE.md")


def _generate_python_files(project_path: Path, context: dict, jinja_env) -> None:
    """Generate Python source files."""
    package_path = project_path / "src" / context["package_name"]
    test_path = project_path / "tests"

    # Generate __init__.py
    init_template = jinja_env.get_template("python/__init__.py.j2")
    init_content = init_template.render(**context)
    (package_path / "__init__.py").write_text(init_content)

    # Generate config.py
    config_template = jinja_env.get_template("python/config.py.j2")
    config_content = config_template.render(**context)
    (package_path / "config.py").write_text(config_content)

    # Generate main.py
    main_template = jinja_env.get_template("python/main.py.j2")
    main_content = main_template.render(**context)
    (package_path / "main.py").write_text(main_content)

    # Generate test_main.py
    test_template = jinja_env.get_template("python/test_main.py.j2")
    test_content = test_template.render(**context)
    (test_path / "test_main.py").write_text(test_content)

    # Generate tests/__init__.py
    (test_path / "__init__.py").write_text("")

    print(f"  ✓ src/{context['package_name']}/__init__.py")
    print(f"  ✓ src/{context['package_name']}/config.py")
    print(f"  ✓ src/{context['package_name']}/main.py")
    print(f"  ✓ tests/test_main.py")


def _to_package_name(name: str) -> str:
    """Convert project name to valid Python package name."""
    return name.replace("-", "_").replace(" ", "_").lower()
