"""
Test setup validation for Forno SSR project.

Validates:
- Virtual environment
- Python version
- Package installation
- OpenAI API access
- Project structure
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_venv():
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print("✓ Virtual environment active")
        return True
    else:
        print("✗ Not in virtual environment")
        print("  Fix: Run 'source .venv/bin/activate'")
        return False


def test_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version too old: {version.major}.{version.minor}.{version.micro}")
        print("  Fix: Use Python 3.10+")
        return False


def test_packages():
    """Check if required packages are installed."""
    required = [
        "openai",
        "pydantic",
        "dotenv",
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "sklearn",
        "tqdm",
    ]

    missing = []
    for pkg in required:
        try:
            if pkg == "dotenv":
                __import__("dotenv")
            elif pkg == "sklearn":
                __import__("sklearn")
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if not missing:
        print("✓ All required packages installed")
        return True
    else:
        print(f"✗ Missing packages: {', '.join(missing)}")
        print("  Fix: Run 'pip install -r requirements.txt'")
        return False


def test_env_file():
    """Check if .env file exists with API key."""
    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        print("✗ .env file not found")
        print("  Fix: Create .env file in project root")
        print("  Add: OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE")
        return False

    # Try to load
    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("✗ OPENAI_API_KEY not set in .env")
        print("  Fix: Add OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE to .env")
        return False

    if not api_key.startswith("sk-"):
        print("✗ OPENAI_API_KEY appears invalid (should start with 'sk-')")
        return False

    print("✓ OpenAI API key configured")
    return True


def test_openai_connection():
    """Test OpenAI API connection."""
    try:
        from openai import OpenAI
        import os
        from dotenv import load_dotenv

        load_dotenv()
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Test with minimal completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5,
        )

        if response.choices[0].message.content:
            print("✓ OpenAI API connection successful")
            return True
        else:
            print("✗ OpenAI API response invalid")
            return False

    except Exception as e:
        print(f"✗ OpenAI API connection failed: {str(e)}")
        print("  Fix: Check your API key and internet connection")
        return False


def test_embeddings():
    """Test embedding API."""
    try:
        from openai import OpenAI
        import os
        from dotenv import load_dotenv

        load_dotenv()
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Test embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="test",
        )

        if len(response.data[0].embedding) > 0:
            print("✓ Embedding API working")
            return True
        else:
            print("✗ Embedding API returned empty vector")
            return False

    except Exception as e:
        print(f"✗ Embedding API failed: {str(e)}")
        return False


def test_project_structure():
    """Test if project structure is correct."""
    try:
        from forno_ssr.personas import get_all_personas
        from forno_ssr.concepts import get_all_concepts
        from forno_ssr.anchors import get_all_anchor_sets

        personas = get_all_personas()
        concepts = get_all_concepts()
        anchors = get_all_anchor_sets()

        print(f"✓ Personas loaded: {len(personas)} personas")
        print(f"✓ Concepts loaded: {len(concepts)} concepts")
        print(f"✓ Anchors loaded: {len(anchors)} anchor sets")

        return True

    except Exception as e:
        print(f"✗ Project structure error: {str(e)}")
        print("  Fix: Ensure all files in src/forno_ssr/ are present")
        return False


def main():
    """Run all validation tests."""
    print("=" * 50)
    print("FORNO SSR SETUP VALIDATION")
    print("=" * 50)
    print()

    tests = [
        ("Virtual Environment", test_venv),
        ("Python Version", test_python_version),
        ("Required Packages", test_packages),
        ("Environment Variables", test_env_file),
        ("OpenAI Connection", test_openai_connection),
        ("Embedding API", test_embeddings),
        ("Project Structure", test_project_structure),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {name} test crashed: {str(e)}")
            results.append(False)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("=" * 50)
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print()
        print("Setup validation complete! ✓")
        print()
        print("Next steps:")
        print("  1. Run quick test: python scripts/test_quick_survey.py")
        print("  2. Run full survey: python scripts/run_survey.py")
        print("  3. Generate analysis: python scripts/analyze_results.py")
    else:
        print(f"✗ {total - passed} test(s) failed ({passed}/{total} passed)")
        print()
        print("Fix the issues above and run this script again.")

    print("=" * 50)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
