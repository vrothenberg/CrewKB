"""
Setup utilities for the CrewKB project.

This module provides utilities for setting up the development environment
and installing dependencies using uv.
"""

import os
import subprocess
import shutil
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
    print("uv is not installed. Please install it manually:")
    print("  curl -sSf https://astral.sh/uv/install.sh | sh")
    print("  # or")
    print("  pip install uv")
    return False


def get_python_path(venv_path: Path) -> Path:
    """
    Get the path to the Python executable in the virtual environment.

    Args:
        venv_path: Path to the virtual environment.

    Returns:
        Path to the Python executable.
    """
    if os.name == "nt":  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Unix/macOS
        return venv_path / "bin" / "python"


def create_venv(
    venv_path: Optional[Path] = None, force: bool = False
) -> Optional[Path]:
    """
    Create a virtual environment using uv.

    Args:
        venv_path: Path to create the virtual environment.
                  Defaults to .venv in current directory.
        force: Whether to force recreation of the virtual environment.

    Returns:
        Path to the virtual environment if creation was successful,
        None otherwise.
    """
    if not check_uv_installed():
        print("uv is not installed. Installing...")
        if not install_uv():
            print("Failed to install uv.")
            return None

    if venv_path is None:
        venv_path = Path(".venv")

    # Check if virtual environment already exists
    if venv_path.exists() and not force:
        python_path = get_python_path(venv_path)
        
        if python_path.exists():
            print(f"Virtual environment already exists at {venv_path}")
            return venv_path
        else:
            print("Virtual environment exists but appears to be incomplete.")
            print("Recreating virtual environment...")
            try:
                # Remove the existing virtual environment
                shutil.rmtree(venv_path)
            except Exception as e:
                print(f"Failed to remove existing virtual environment: {e}")
                return None
    elif venv_path.exists() and force:
        print(f"Removing existing virtual environment at {venv_path}")
        try:
            shutil.rmtree(venv_path)
        except Exception as e:
            print(f"Failed to remove existing virtual environment: {e}")
            return None

    try:
        print("Creating virtual environment...")
        subprocess.run(
            ["uv", "venv", str(venv_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        
        # Verify that python exists in the virtual environment
        python_path = get_python_path(venv_path)
        if not python_path.exists():
            print("Failed to create a valid virtual environment")
            print("(python not found)")
            return None
            
        return venv_path
    except Exception as e:
        print(f"Failed to create virtual environment: {e}")
        # If the error is because the venv already exists, try to use it
        if "are the same file" in str(e):
            print("Trying to use existing virtual environment...")
            # Check if python exists
            python_path = get_python_path(venv_path)
            if python_path.exists():
                return venv_path
            else:
                print("Existing virtual environment is invalid")
                print("(python not found)")
                return None
        return None


def remove_dependency(dependency: str, verbose: bool = True) -> bool:
    """
    Remove a dependency using uv.

    Args:
        dependency: The dependency to remove.
        verbose: Whether to print verbose output.

    Returns:
        True if removal was successful, False otherwise.
    """
    if not check_uv_installed():
        print("uv is not installed. Please install it first.")
        return False

    try:
        print(f"Removing {dependency}...")
        # Use uv pip freeze to check if the package is installed
        result = subprocess.run(
            ["uv", "pip", "freeze"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        
        # Check if the package is in the output
        installed_packages = result.stdout.splitlines()
        package_installed = any(
            line.lower().startswith(f"{dependency.lower()}==")
            or line.lower().startswith(f"{dependency.lower()}[")
            for line in installed_packages
        )
        
        if package_installed:
            # Remove the package
            try:
                subprocess.run(
                    ["uv", "pip", "uninstall", "-y", dependency],
                    stdout=None if verbose else subprocess.PIPE,
                    stderr=None if verbose else subprocess.PIPE,
                    check=True,
                )
                print(f"Successfully removed {dependency}")
            except subprocess.SubprocessError as e:
                print(f"Warning: Failed to remove {dependency}: {e}")
                # Continue anyway, as uv add will handle conflicts
        
        return True
    except subprocess.SubprocessError as e:
        print(f"Failed to check for installed packages: {e}")
        # Continue anyway, as uv add will handle conflicts
        return True


def install_dependencies(
    dependencies: List[str], dev: bool = False, verbose: bool = True
) -> bool:
    """
    Install dependencies using uv.

    Args:
        dependencies: List of dependencies to install.
        dev: Whether to install as development dependencies.
        verbose: Whether to print verbose output.

    Returns:
        True if installation was successful, False otherwise.
    """
    if not check_uv_installed():
        print("uv is not installed. Please install it first.")
        return False

    try:
        # Install dependencies one by one to avoid issues
        for dependency in dependencies:
            # Remove the dependency first to avoid conflicts
            base_dependency = dependency.split("[")[0]
            remove_dependency(base_dependency, verbose)
            
            cmd = ["uv", "add"]
            if dev:
                cmd.append("--dev")
            cmd.append(dependency)
            
            print(f"Installing {dependency}...")
            result = subprocess.run(
                cmd,
                stdout=None if verbose else subprocess.PIPE,
                stderr=None if verbose else subprocess.PIPE,
                check=False,
            )
            
            if result.returncode != 0:
                print(f"Failed to install {dependency}:")
                if (not verbose and result and hasattr(result, 'stderr') 
                        and result.stderr):
                    print(result.stderr.decode())
                return False
        
        return True
    except subprocess.SubprocessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


def install_crewai_tools(verbose: bool = True) -> bool:
    """
    Install crewai tools dependencies.

    Args:
        verbose: Whether to print verbose output.

    Returns:
        True if installation was successful, False otherwise.
    """
    # Install langchain dependencies separately
    # since crewai[tools] doesn't work with uv
    tools_dependencies = [
        "langchain",
        "langchain-community",
        "langchain-core",
    ]
    
    print("Installing crewai tools dependencies...")
    return install_dependencies(tools_dependencies, verbose=verbose)


def setup_environment(verbose: bool = True, force: bool = True) -> bool:
    """
    Set up the development environment.

    This function creates a virtual environment and installs all required
    dependencies using uv.

    Args:
        verbose: Whether to print verbose output.
        force: Whether to force recreation of the virtual environment.

    Returns:
        True if setup was successful, False otherwise.
    """
    print("Setting up the CrewKB development environment...")
    
    # Check if uv is installed
    if not check_uv_installed():
        print("uv is not installed. Please install it first.")
        return False
    
    # Always force recreation of the virtual environment to avoid conflicts
    venv_path = create_venv(force=True)
    if not venv_path:
        return False
    
    # Install dependencies
    print("\nInstalling dependencies...")
    
    # First, install crewai with tools
    print("Installing crewai[tools]...")
    try:
        # Make sure crewai is completely removed first
        subprocess.run(
            ["uv", "pip", "uninstall", "-y", "crewai"],
            stdout=None if verbose else subprocess.PIPE,
            stderr=None if verbose else subprocess.PIPE,
            check=False,
        )
        
        # Install crewai[tools]
        result = subprocess.run(
            ["uv", "add", "crewai[tools]"],
            stdout=None if verbose else subprocess.PIPE,
            stderr=None if verbose else subprocess.PIPE,
            check=True,
        )
        print("Successfully installed crewai[tools]")
    except subprocess.SubprocessError as e:
        print(f"Failed to install crewai[tools]: {e}")
        if verbose:
            print("Trying to install dependencies separately...")
    
    # Install other dependencies one by one
    dependencies = [
        # Core dependencies
        "pydantic",
        "typer",
        "requests",
        "python-dotenv",
        "markdown",
        # LangChain dependencies
        "langchain",
        "langchain-community",
        "langchain-core",
        # Development dependencies
        "pytest",
        "flake8",
        "black",
        "isort",
    ]
    
    for dependency in dependencies:
        cmd = ["uv", "add"]
        if dependency in ["pytest", "flake8", "black", "isort"]:
            cmd.append("--dev")
        cmd.append(dependency)
        
        print(f"Installing {dependency}...")
        result = subprocess.run(
            cmd,
            stdout=None if verbose else subprocess.PIPE,
            stderr=None if verbose else subprocess.PIPE,
            check=False,
        )
        
        if result.returncode != 0:
            print(f"Warning: Failed to install {dependency}")
            if verbose and hasattr(result, 'stderr') and result.stderr:
                print(result.stderr.decode())
            # Continue with other dependencies

    print("\nEnvironment setup complete.")
    print("\nTo activate the virtual environment, run:")
    print("  source .venv/bin/activate  # On Unix/macOS")
    print("  .venv\\Scripts\\activate  # On Windows")
    print("\nTo run the CLI, use:")
    print("  python -m crewkb.cli --help")
    
    print("\nMake sure to create a .env file with your API keys:")
    print("  GEMINI_API_KEY=your_gemini_api_key")
    print("  SERPER_API_KEY=your_serper_api_key")
    print("  ENTREZ_EMAIL=your_email@example.com")
    print("  ENTREZ_API_KEY=your_entrez_api_key")
    return True


if __name__ == "__main__":
    setup_environment()
    setup_environment()
