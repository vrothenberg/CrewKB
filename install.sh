#!/bin/bash

# CrewKB Installation Script
# This script sets up the CrewKB development environment in one step

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_green() { echo -e "${GREEN}$1${NC}"; }
print_yellow() { echo -e "${YELLOW}$1${NC}"; }
print_red() { echo -e "${RED}$1${NC}"; }
print_blue() { echo -e "${BLUE}$1${NC}"; }

# Print header
print_blue "========================================"
print_blue "       CrewKB Installation Script       "
print_blue "========================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_yellow "No .env file found. Creating from .env.example..."
        cp .env.example .env
        print_yellow "Please edit .env file with your API keys before running the application."
    else
        print_red "Error: No .env or .env.example file found."
        exit 1
    fi
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_yellow "uv is not installed. Installing..."
    
    # Check if pip is available
    if command -v pip &> /dev/null; then
        pip install uv
    else
        print_red "Error: pip is not available. Please install pip first."
        print_yellow "You can install uv manually with:"
        echo "  curl -sSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi

# Remove existing virtual environment if it exists
if [ -d ".venv" ]; then
    print_yellow "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create virtual environment
print_green "Creating virtual environment..."
uv venv .venv

# Define paths to virtual environment binaries
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows paths
    VENV_PYTHON=".venv/Scripts/python.exe"
    VENV_PIP=".venv/Scripts/pip.exe"
    VENV_ACTIVATE=".venv/Scripts/activate"
    VENV_BIN=".venv/Scripts"
else
    # Unix paths
    VENV_PYTHON=".venv/bin/python"
    VENV_PIP=".venv/bin/pip"
    VENV_ACTIVATE=".venv/bin/activate"
    VENV_BIN=".venv/bin"
fi

# Verify virtual environment was created correctly
if [ ! -f "$VENV_PYTHON" ]; then
    print_red "Error: Virtual environment creation failed."
    print_red "Python executable not found at: $VENV_PYTHON"
    exit 1
fi

# Install the package in development mode with all dependencies
print_green "Installing CrewKB in development mode with all dependencies..."
VIRTUAL_ENV=".venv" uv pip install -e ".[dev]"

# Check if installation was successful
if [ $? -ne 0 ]; then
    print_red "Error: Installation failed."
    exit 1
fi

# Verify the crewkb command is available
if [ ! -f "$VENV_BIN/crewkb" ]; then
    print_yellow "Warning: crewkb command not found in expected location."
    print_yellow "Checking if it was installed elsewhere..."
    
    # Try to find the crewkb command
    CREWKB_PATH=$(find .venv -name "crewkb" -type f 2>/dev/null)
    
    if [ -z "$CREWKB_PATH" ]; then
        print_red "Error: crewkb command not found. Installation may have failed."
        exit 1
    else
        print_green "Found crewkb command at: $CREWKB_PATH"
        VENV_BIN=$(dirname "$CREWKB_PATH")
        print_green "Updating VENV_BIN to: $VENV_BIN"
    fi
fi

# Make sure the crewkb command is executable
chmod +x "$VENV_BIN/crewkb" 2>/dev/null || true

# Print success message
echo ""
print_blue "========================================"
print_blue "       Installation Complete!           "
print_blue "========================================"
echo ""
print_green "CrewKB has been successfully installed in the .venv virtual environment!"
echo ""
print_green "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
print_green "After activation, you can run the CLI with:"
echo "  crewkb --help"
echo ""
print_green "Available commands:"
echo "  crewkb create [TOPIC]      - Create a knowledge base article"
echo "  crewkb research [TOPIC]    - Research a biomedical topic"
echo "  crewkb review [FILE]       - Review a knowledge base article"
echo "  crewkb generate [TOPIC]    - Generate a complete article"
echo "  crewkb metrics             - Generate metrics dashboard"
echo "  crewkb version             - Show version information"
echo ""
print_yellow "IMPORTANT: The environment is NOT activated automatically to avoid"
print_yellow "modifying your current shell. You MUST activate the environment"
print_yellow "before using CrewKB."
echo ""
print_yellow "Environment variables from .env will be loaded automatically when"
print_yellow "you run the crewkb command."
echo ""
