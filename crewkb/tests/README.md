# CrewKB Tests

This directory contains tests for the CrewKB project.

## Test Structure

The tests are organized by component:

- `tools/`: Tests for the tools used by agents
  - `search/`: Tests for search tools
  - `content/`: Tests for content tools
  - `validation/`: Tests for validation tools
- `utils/`: Tests for utility functions and classes
- `crews/`: Tests for crew implementations
- `models/`: Tests for data models
- `storage/`: Tests for storage implementations

## Running Tests

To run all tests:

```bash
# From the project root directory
python -m unittest discover -s crewkb/tests
```

To run a specific test file:

```bash
# From the project root directory
python -m unittest crewkb/tests/utils/test_tool_factory.py
```

To run a specific test case:

```bash
# From the project root directory
python -m unittest crewkb.tests.utils.test_tool_factory.TestToolFactory
```

To run a specific test method:

```bash
# From the project root directory
python -m unittest crewkb.tests.utils.test_tool_factory.TestToolFactory.test_create_tool
```

## Test Coverage

To generate a test coverage report, you'll need to install the `coverage` package:

```bash
pip install coverage
```

Then run the tests with coverage:

```bash
# From the project root directory
coverage run -m unittest discover -s crewkb/tests
```

And generate a report:

```bash
coverage report
```

For a more detailed HTML report:

```bash
coverage html
```

This will create a directory called `htmlcov` with an HTML report that you can open in your browser.

## Writing Tests

When writing tests for CrewKB, follow these guidelines:

1. **Test Structure**: Use the `unittest` framework and organize tests by component.
2. **Test Naming**: Name test files with the `test_` prefix and test methods with the `test_` prefix.
3. **Test Coverage**: Aim for high test coverage, especially for critical components.
4. **Mocking**: Use `unittest.mock` to mock external dependencies like APIs.
5. **Assertions**: Use the appropriate assertions for the type of test.
6. **Documentation**: Document the purpose of each test class and method.

## Test Dependencies

The tests depend on the following packages:

- `unittest`: The standard Python testing framework
- `unittest.mock`: For mocking external dependencies
- `coverage` (optional): For generating test coverage reports
