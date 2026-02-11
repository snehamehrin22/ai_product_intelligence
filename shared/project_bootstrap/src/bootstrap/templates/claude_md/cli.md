## CLI-Specific Patterns

### Framework

This project uses Click for command-line interfaces.

```bash
pip install click
```

### Project Structure

```
src/{{ package_name }}/
├── __init__.py
├── config.py           # Load .env, validate config
├── main.py             # Click app setup
└── commands/
    ├── __init__.py
    └── cmd_name.py     # Individual commands
```

### Command Pattern

```python
import click

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file')
def process(input_file: str, output: str | None):
    """Process INPUT_FILE and write to OUTPUT."""
    # Your implementation
    click.echo(f"Processing {input_file}...")

if __name__ == "__main__":
    process()
```

### Group Commands

```python
@click.group()
def cli():
    """Main CLI group."""
    pass

@cli.command()
def subcommand():
    """A subcommand."""
    pass

# Usage: mycli subcommand
```

### Testing

Use Click's CliRunner:

```python
from click.testing import CliRunner
from src.{{ package_name }}.main import cli

def test_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['arg1', '--option', 'value'])
    assert result.exit_code == 0
    assert 'expected output' in result.output
```
