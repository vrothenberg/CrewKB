#!/usr/bin/env python
"""
Setup script for the CrewKB project.

This script is a wrapper around the setup utilities in crewkb.utils.setup.
"""

import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from crewkb.utils.setup import setup_environment
except ImportError:
    print("Error: Could not import setup_environment from utils.setup.")
    print("Make sure you're running this script from the project root.")
    sys.exit(1)


def main():
    """
    Main entry point for the setup script.
    """
    print("Setting up the CrewKB development environment...")
    success = setup_environment()
    
    if success:
        print("\nSetup completed successfully!")
        print("\nTo activate the virtual environment, run:")
        print("  source .venv/bin/activate  # On Unix/macOS")
        print("  .venv\\Scripts\\activate  # On Windows")
        print("\nTo run the CLI, use:")
        print("  python -m crewkb.cli --help")
    else:
        print("\nSetup failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
