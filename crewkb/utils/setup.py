"""
Setup utilities for the CrewKB project.

This module provides utilities for setting up the development environment
and installing dependencies.
"""

import subprocess
from pathlib import Path
from typing import List, Optional


def check_uv_installed() -> bool:
    """
    Check if uv is installed.

    Returns:
        True if uv is installed, False otherwise.
    """
    try:
        subprocess.run(
            ["uv", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_uv() -> bool:
    """
    Install uv.

    Returns:
        True if installation was successful, False otherwise.
    """
    try:
        # Install uv using the official installer
        subprocess.run(
            [
                "curl",
                "-sSf",
                "https://install.python-poetry.org",
                "|",
                "python3",
                "-",
            ],
            shell=True,
            check=True,
        )
        return True
    except subprocess.SubprocessError:
        return False


def create_venv(venv_path: Optional[Path] = None) -> bool:
    """
    Create a virtual environment using uv.

    Args:
        venv_path: Path to create the virtual environment. Defaults to .venv
                   in the current directory.

    Returns:
        True if creation was successful, False otherwise.
    """
    if not check_uv_installed():
        print("uv is not installed. Installing...")
        if not install_uv():
            print("Failed to install uv.")
            return False

    try:
        cmd = ["uv", "venv"]
        if venv_path:
            cmd.extend([str(venv_path)])

        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.SubprocessError as e:
        print(f"Failed to create virtual environment: {e}")
        return False


def install_dependencies(
    dependencies: List[str], dev: bool = False
) -> bool:
    """
    Install dependencies using uv.

    Args:
        dependencies: List of dependencies to install.
        dev: Whether to install as development dependencies.

    Returns:
        True if installation was successful, False otherwise.
    """
    if not check_uv_installed():
        print("uv is not installed. Installing...")
        if not install_uv():
            print("Failed to install uv.")
            return False

    try:
        cmd = ["uv", "add"]
        if dev:
            cmd.append("--dev")
        cmd.extend(dependencies)

        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.SubprocessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


def setup_environment() -> bool:
    """
    Set up the development environment.

    This function creates a virtual environment and installs all required
    dependencies.

    Returns:
        True if setup was successful, False otherwise.
    """
    # Create virtual environment
    if not create_venv():
        return False

    # Install core dependencies
    core_dependencies = [
        "crewai",
        "crewai[tools]",
        "pydantic",
        "typer",
        "requests",
        "python-dotenv",
    ]
    if not install_dependencies(core_dependencies):
        return False

    # Install optional dependencies
    optional_dependencies = [
        "markdown",
    ]
    if not install_dependencies(optional_dependencies):
        return False

    # Install development dependencies
    dev_dependencies = [
        "pytest",
        "flake8",
        "black",
        "isort",
    ]
    if not install_dependencies(dev_dependencies, dev=True):
        return False

    print("Environment setup complete.")
    return True


if __name__ == "__main__":
    setup_environment()
