#!/bin/bash

# Run tests for CrewKB
# This script runs the unit tests for the CrewKB project

# Set the Python path to include the current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running CrewKB tests...${NC}"
echo

# Run all tests
echo -e "${YELLOW}Running all tests:${NC}"
python -m unittest discover -s crewkb/tests
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi

echo

# Run specific test categories
# echo -e "${YELLOW}Running validation tool tests:${NC}"
# python -m unittest discover -s crewkb/tests/tools/validation
# if [ $? -eq 0 ]; then
#     echo -e "${GREEN}Validation tool tests passed!${NC}"
# else
#     echo -e "${RED}Some validation tool tests failed.${NC}"
#     exit 1
# fi

echo

echo -e "${YELLOW}Running utility tests:${NC}"
python -m unittest discover -s crewkb/tests/utils
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Utility tests passed!${NC}"
else
    echo -e "${RED}Some utility tests failed.${NC}"
    exit 1
fi

echo

# Run with coverage if available
if command -v coverage &> /dev/null; then
    echo -e "${YELLOW}Running tests with coverage:${NC}"
    coverage run -m unittest discover -s crewkb/tests
    coverage report
    echo -e "${YELLOW}For a detailed HTML report, run:${NC} coverage html"
else
    echo -e "${YELLOW}Coverage not installed. To install:${NC} pip install coverage"
fi

echo
echo -e "${GREEN}All test runs completed!${NC}"
