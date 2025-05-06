# CrewKB Project Brief

## Project Overview

CrewKB is a knowledge base creation system for biomedical topics using the Crew.AI framework. The system leverages specialized AI agents that collaborate to research, create, and review comprehensive, accurate, and structured knowledge base articles on health conditions, biomarkers, laboratory tests, medicines, and supplements.

## Core Requirements

1. **Agent-Based Architecture**: Implement specialized agents with focused roles for research, content creation, and review.

2. **Multiple Workflows**: Create different workflows for different types of biomedical topics (diseases, biomarkers, lab tests).

3. **Structured Content**: Ensure all articles follow a consistent structure defined by Pydantic models.

4. **Dual Storage Format**: Store articles in both JSON (for programmatic access) and Markdown (for human readability).

5. **Quality Assurance**: Implement mechanisms for ensuring accuracy and detecting hallucinations.

6. **CLI Interface**: Provide a simple command-line interface for creating and managing articles.

## Project Goals

### Primary Goals

1. **Automation**: Automate the process of creating comprehensive knowledge base articles on biomedical topics.

2. **Consistency**: Ensure all articles follow a consistent structure and quality standard.

3. **Accuracy**: Ensure all information is accurate, up-to-date, and properly cited.

4. **Scalability**: Enable the creation of large volumes of content without compromising on quality.

### Secondary Goals

1. **Extensibility**: Make it easy to add new article types and workflows.

2. **Customizability**: Allow users to customize the article structure and content requirements.

3. **Integration**: Facilitate integration with content management systems and other tools.

4. **Collaboration**: Enable collaboration between AI agents and human experts.

## Target Users

1. **Knowledge Base Administrators**: Professionals responsible for creating and maintaining biomedical knowledge bases.

2. **Medical Content Creators**: Writers and editors who create content on biomedical topics.

3. **Healthcare Professionals**: Doctors, nurses, and other healthcare providers who need access to comprehensive information.

4. **Researchers**: Scientists and researchers who need to compile information on specific biomedical topics.

## Success Criteria

1. **Article Quality**: Articles are comprehensive, accurate, and properly structured.

2. **Production Efficiency**: The system significantly reduces the time required to create knowledge base articles.

3. **User Satisfaction**: Users find the system easy to use and the articles valuable.

4. **Scalability**: The system can handle a wide range of biomedical topics with consistent quality.

## Implementation Phases

### Phase 1: Foundation (1-2 weeks)

- Set up the project structure
- Define the article models
- Implement the storage system
- Create the CLI interface

### Phase 2: Agent Development (2-3 weeks)

- Implement research agents
- Implement content creation agents
- Implement review agents

### Phase 3: Tool Development (2-3 weeks)

- Implement search tools
- Implement content tools
- Implement validation tools

### Phase 4: Workflow Integration (2-3 weeks)

- Implement disease knowledge base workflow
- Implement biomarker knowledge base workflow
- Implement lab test knowledge base workflow

### Phase 5: Testing and Refinement (2-3 weeks)

- Conduct unit and integration testing
- Perform end-to-end testing
- Refine the system based on feedback

## Technical Constraints

1. **Python 3.10+**: The project will be implemented in Python 3.10 or higher.

2. **Crew.AI Framework**: The project will use the Crew.AI framework for agent orchestration.

3. **Pydantic**: The project will use Pydantic for data validation and settings management.

4. **uv**: The project will use uv for dependency management and virtual environment creation.

5. **API Limitations**: The project will need to respect rate limits and other constraints of external APIs.

## Resources

1. **Crew.AI Documentation**: https://docs.crewai.com/

2. **Pydantic Documentation**: https://docs.pydantic.dev/

3. **uv Documentation**: https://github.com/astral-sh/uv

4. **External APIs**:
   - OpenAI API
   - SerperDev API
   - PubMed API
   - arXiv API
   - Semantic Scholar API

## Risks and Mitigation

1. **API Rate Limits**: Implement rate limiting and caching to avoid hitting API limits.

2. **LLM Limitations**: Design the system to handle context window limitations and other constraints of LLMs.

3. **Content Accuracy**: Implement robust validation mechanisms to ensure accuracy.

4. **Performance**: Optimize the system to minimize latency and resource usage.

5. **API Key Management**: Implement secure handling of API keys.

## Stakeholders

1. **Project Owner**: The user who initiated the project.

2. **Development Team**: The team responsible for implementing the system.

3. **End Users**: The professionals who will use the system to create knowledge base articles.

4. **Content Consumers**: The individuals who will read and use the knowledge base articles.

## Communication Plan

1. **Regular Updates**: Provide regular updates on project progress.

2. **Documentation**: Maintain comprehensive documentation of the system.

3. **Feedback Loop**: Establish a feedback loop to gather input from stakeholders.

4. **Issue Tracking**: Use a system to track and address issues and feature requests.

## Conclusion

CrewKB aims to revolutionize the creation of biomedical knowledge base content by leveraging the power of AI agents to automate the research, creation, and review process. By implementing a modular, agent-based architecture with specialized roles and workflows, the system will enable the efficient production of high-quality, consistent, and accurate knowledge base articles on a wide range of biomedical topics.
