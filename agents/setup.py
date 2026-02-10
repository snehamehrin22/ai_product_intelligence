"""Setup script for agent_utils library."""

from setuptools import setup, find_packages

setup(
    name="agent_utils",
    version="0.1.0",
    description="Shared utilities for building AI agents",
    author="AI Product Intelligence Team",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
