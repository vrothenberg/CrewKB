#!/usr/bin/env python
"""
Setup script for the CrewKB project.

This script provides the necessary package configuration for setuptools.
For development environment setup, use the install.sh script instead.
"""

from setuptools import setup, find_packages

# Package metadata
PACKAGE_NAME = "crewkb"
VERSION = "0.1.0"
# Split description to avoid line length issues
DESCRIPTION = (
    "A knowledge base creation system for biomedical topics "
    "using Crew.AI"
)
AUTHOR = "CrewKB Team"
AUTHOR_EMAIL = "example@example.com"
URL = ""
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.10"

# Dependencies
INSTALL_REQUIRES = [
    "crewai[tools]",
    "pydantic",
    "typer",
    "requests",
    "python-dotenv",
    "markdown",
    "langchain",
    "langchain-community",
    "langchain-core",
    "biopython",  # Added for PubMed search
]

EXTRAS_REQUIRE = {
    "dev": [
        "pytest",
        "flake8",
        "black",
        "isort",
    ],
}

# Entry points
ENTRY_POINTS = {
    "console_scripts": [
        "crewkb=crewkb.cli:main",
    ],
}

if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        packages=find_packages(),
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        entry_points=ENTRY_POINTS,
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering :: Medical Science Apps.",
        ],
    )
