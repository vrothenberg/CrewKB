# CrewKB Technical Context

## Technologies Used

CrewKB is built using a stack of modern Python technologies, with a focus on AI agent orchestration, natural language processing, and structured data management.

### Core Technologies

1. **Python 3.10+**: The primary programming language for the project, chosen for its extensive ecosystem of AI and data science libraries.

2. **Crew.AI Framework**: The foundation of the agent system, providing tools for creating, managing, and orchestrating AI agents.

3. **Pydantic**: Used for data validation and settings management, particularly for defining the structure of knowledge base articles.

4. **uv**: A modern Python package manager and installer, used for dependency management and virtual environment creation.

5. **Typer**: A library for building CLI applications, used to create the command-line interface for CrewKB.

### AI and NLP Technologies

1. **Large Language Models (LLMs)**: The underlying AI models that power the agents, accessed through various providers.

2. **OpenAI API**: Used for accessing GPT models for content generation and analysis.

3. **Embeddings**: Vector representations of text used for semantic search and similarity comparisons.

### Search and Research Technologies

1. **SerperDev API**: Used for Google search capabilities.

2. **PubMed API**: Used for searching medical and scientific literature.

3. **arXiv API**: Used for accessing scientific papers and preprints.

4. **Semantic Scholar API**: Used for searching academic papers with semantic understanding.

### Data Storage and Formatting

1. **JSON**: Used for structured storage of knowledge base articles.

2. **Markdown**: Used for human-readable presentation of articles.

3. **File System Storage**: Articles are stored as files in the local file system.

## Development Setup

### Environment Setup

CrewKB uses uv for dependency management and virtual environment creation:

```bash
# Install uv if not already installed
curl -sSf https://install.python-poetry.org | python3 -

# Create a new project
mkdir -p CrewKB
cd CrewKB

# Initialize a new Python project
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

### Dependencies

The project has the following key dependencies:

```bash
# Core dependencies
uv add crewai
uv add "crewai[tools]"
uv add pydantic
uv add typer
uv add requests
uv add python-dotenv

# Optional dependencies for specific features
uv add markdown
uv add pytest  # For testing
```

### Project Structure

The project follows a modular structure:

```
CrewKB/
├── memory-bank/           # Memory bank files
├── .env                   # Environment variables
├── pyproject.toml         # Project configuration
├── README.md              # Project documentation
├── crewkb/
│   ├── __init__.py
│   ├── cli.py             # CLI interface
│   ├── config.py          # Configuration
│   ├── models/            # Pydantic models
│   ├── agents/            # Agent definitions
│   ├── crews/             # Crew definitions
│   ├── tools/             # Tool implementations
│   ├── storage/           # Storage implementations
│   └── utils/             # Utility functions
└── tests/                 # Test directory
```

### Configuration

The project uses environment variables for configuration, stored in a `.env` file:

```
# API Keys
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...

# Configuration
LOG_LEVEL=INFO
OUTPUT_DIR=./output
```

## Technical Constraints

### API Limitations

1. **Rate Limits**: External APIs (OpenAI, SerperDev, PubMed, etc.) have rate limits that must be respected.

2. **Token Limits**: LLMs have context window limitations that constrain the amount of text that can be processed at once.

3. **Cost Considerations**: API usage incurs costs, particularly for LLM calls and search APIs.

### Performance Considerations

1. **Latency**: API calls and LLM processing introduce latency that affects the overall speed of article creation.

2. **Parallelization**: Some tasks can be parallelized, but dependencies between tasks limit the degree of parallelization.

3. **Memory Usage**: Processing large articles and research data can require significant memory resources.

### Security and Privacy

1. **API Key Management**: Secure handling of API keys is essential to prevent unauthorized access.

2. **Data Privacy**: Medical information is sensitive and must be handled with appropriate privacy considerations.

3. **Output Validation**: Generated content must be validated to ensure accuracy and prevent harmful information.

## Dependencies

### External Dependencies

1. **OpenAI API**: Required for accessing GPT models.

2. **SerperDev API**: Required for Google search capabilities.

3. **PubMed API**: Required for searching medical literature.

4. **arXiv API**: Required for accessing scientific papers.

5. **Semantic Scholar API**: Required for searching academic papers.

### Internal Dependencies

1. **Pydantic Models**: The article structure depends on properly defined Pydantic models.

2. **Agent Definitions**: The system relies on well-defined agent roles and responsibilities.

3. **Tool Implementations**: Agents depend on properly implemented tools for their capabilities.

4. **Workflow Definitions**: The overall process depends on well-designed workflows.

## Development Practices

### Code Style

The project follows the PEP 8 style guide with some modifications:

- Line length limit of 100 characters
- Use of type hints throughout the codebase
- Docstrings for all public functions, classes, and methods

### Testing

The project uses pytest for testing:

- Unit tests for individual components
- Integration tests for agent interactions
- End-to-end tests for complete workflows

### Documentation

Documentation is maintained in several forms:

- Docstrings for code-level documentation
- README.md for project overview
- Memory bank files for system design and context
- CLI help text for user guidance

### Version Control

The project uses Git for version control:

- Feature branches for new features
- Pull requests for code review
- Semantic versioning for releases

## Deployment and Distribution

### Local Deployment

The primary deployment model is local installation:

```bash
# Install from source
git clone https://github.com/username/CrewKB.git
cd CrewKB
uv venv
source .venv/bin/activate
uv install -e .

# Run the CLI
crewkb --help
```

### Packaging

The project can be packaged for distribution:

```bash
# Build the package
uv build

# Install from the built package
uv install dist/crewkb-0.1.0-py3-none-any.whl
```

### Docker Deployment

A Dockerfile is provided for containerized deployment:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install uv && \
    uv venv && \
    uv install -e .

ENTRYPOINT ["crewkb"]
```

## Future Technical Considerations

### Scalability

1. **Database Integration**: Future versions may integrate with databases for more efficient storage and retrieval.

2. **Distributed Processing**: For handling larger volumes of articles, distributed processing may be implemented.

3. **API Service**: A REST API may be added to allow programmatic access to the system.

### Integration

1. **Web Interface**: A web interface may be developed for easier interaction with the system.

2. **Content Management Systems**: Integration with CMSs may be added for direct publication of articles.

3. **Knowledge Graph**: A knowledge graph may be implemented to represent relationships between biomedical concepts.

### Advanced Features

1. **Continuous Learning**: Mechanisms for agents to learn from feedback and improve over time.

2. **Multi-language Support**: Expansion to support multiple languages for global reach.

3. **Interactive Editing**: Tools for human editors to collaborate with AI agents in article creation.
