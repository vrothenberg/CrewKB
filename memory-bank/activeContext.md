# CrewKB Active Context

## Current Work Focus

The current focus of the CrewKB project is on enhancing the search and knowledge synthesis workflow for knowledge base article creation. This includes:

1. **Enhanced Search Workflow**: Implementing a comprehensive search workflow that leverages Google Scholar and Semantic Scholar to gather high-quality research papers, with a focus on:
   - Generating search terms from article outlines using Gemini 2.5 Pro
   - Searching with DirectGoogleScholarTool and SemanticScholarTool
   - Analyzing related search terms to expand research coverage
   - Downloading and parsing PDFs using the Marker package
   - Distilling content with Gemini 2.0 Flash

2. **Knowledge Organization**: Creating a structured knowledge directory system to organize research materials by topic, including:
   - Implementing Pydantic models for paper metadata
   - Creating a hierarchical storage structure for research materials
   - Developing utilities for managing the knowledge directory

3. **Agent-Based Synthesis**: Developing specialized agents for different stages of the knowledge synthesis process:
   - Outline generation with Gemini 2.5 Pro
   - Search term generation and analysis
   - Content distillation and synthesis
   - Quality review and improvement

4. **Testing and Refinement**: Testing the enhanced search workflow to ensure it produces high-quality, well-cited knowledge base articles.

5. **Documentation**: Updating code documentation, creating user guides, and documenting the new workflow.

## Recent Changes

We have made significant progress in migrating to Google's Gemini models, implementing the end-to-end workflow, metrics collection system, MLflow integration, streamlining the CLI interface, developing a comprehensive testing framework, and designing an enhanced search and knowledge synthesis workflow:

1. **Migration to Google Gemini Models**:
   - Refactored the codebase to use Google's Gemini 2.0 Flash models instead of OpenAI models
   - Created a LLM factory utility to centralize model configuration
   - Updated configuration files to support Gemini API keys and model settings
   - Modified all agent creation code to use the new LLM factory

2. **End-to-End Workflow Implementation**:
   - Implemented a flow that orchestrates the entire knowledge base article creation process
   - Created a state model for tracking the article creation process
   - Implemented transitions between research, content creation, review, and quality assessment phases
   - Added error handling and recovery mechanisms

3. **CLI Enhancement and Streamlining**:
   - Added a generate command that uses the end-to-end workflow to create a complete knowledge base article
   - Added a metrics command that generates dashboards for visualizing article quality metrics
   - Added a visualize_flow command that generates a visualization of the knowledge base article creation flow
   - Streamlined the CLI interface to use Python's entry point mechanism
   - Removed the wrapper script in favor of a direct CLI command
   - Enhanced environment variable handling in the CLI
   - Updated the installation process to create a proper CLI entry point

4. **Metrics Collection System**:
   - Implemented a metrics collector for tracking and analyzing the quality of generated articles
   - Added quality metrics calculation for accuracy, readability, and patient relevance
   - Implemented risk assessment for identifying potential issues in generated articles
   - Created a dashboard generation system for visualizing article quality metrics

5. **Quality Assessment System**:
   - Implemented a quality assessment system that evaluates the accuracy, readability, and patient relevance of generated articles
   - Added a confidence scoring mechanism based on quality metrics and risk assessment
   - Implemented a risk area identification system for highlighting potential issues in generated articles

6. **Flow Visualization**:
   - Added the ability to generate a visualization of the knowledge base article creation flow
   - Created a plot function that shows the relationships between different steps in the flow
   - Implemented a command for generating the flow visualization

7. **Tool Factory Implementation**:
   - Created a ToolFactory utility to centralize tool creation and management
   - Implemented methods for creating tools by name and for specific agents
   - Updated crew implementations to use the ToolFactory for tool assignment
   - Ensured proper tool assignment to review agents for validation tools

8. **Testing Framework Development**:
   - Established a comprehensive testing structure for all components
   - Created unit tests for validation tools (FactCheckerTool, ReadabilityAnalyzerTool)
   - Implemented tests for the ToolFactory utility
   - Created documentation for the testing framework and guidelines
   - Fixed compatibility issues with Pydantic models in validation tools
   - Updated tests to handle changes in tool description formatting
   - Ensured all tests pass successfully with the run_tests.sh script

9. **Additional Search Tools Implementation**:
   - Implemented SemanticScholarTool for searching academic papers with citation count and quality filtering
   - Added unit tests for the SemanticScholarTool
   - Updated ToolFactory to create and assign the SemanticScholarTool to appropriate agents
   - Integrated the SemanticScholarTool with the research and citation workflows

10. **MLflow Integration**:
    - Integrated MLflow for tracking experiments, logging metrics, and visualizing agent performance
    - Created a MLflow utility module to centralize MLflow integration
    - Updated configuration files to support MLflow tracking URI and experiment name
    - Modified the knowledge base flow to log metrics to MLflow
    - Enhanced the metrics collector to integrate with MLflow
    - Created a test script for verifying MLflow integration
    - Updated memory bank files to document MLflow integration

11. **DirectGoogleScholarTool and Test Suite Fixes**:
    - Resolved `TypeError` in `DirectGoogleScholarTool` related to invalid arguments (`stealth`, `magic`, `simulate_user`) for `BrowserConfig` from `crawl4ai`.
    - Corrected `TypeError` for `CrawlerRunConfig` by changing `timeout` to `page_timeout`.
    - Fixed `RuntimeWarning: coroutine '_async_run' was never awaited` in `test_direct_google_scholar_tool.py` by ensuring the coroutine object passed to the mocked `asyncio.run` is closed.
    - Implemented basic stealth enhancements in `DirectGoogleScholarTool`:
        - Set `user_agent_mode="random"` in `BrowserConfig`.
        - Passed `magic=True` to the `crawler.arun()` call.
    - Updated `.clinerules` to reflect user preference of not auto-fixing Flake8 errors.

12. **Enhanced Search Workflow Design**:
    - Designed a comprehensive search workflow that leverages Google Scholar and Semantic Scholar
    - Created a detailed design document for the enhanced search and knowledge synthesis workflow
    - Defined Pydantic models for paper metadata, search terms, and knowledge topics
    - Designed a hierarchical storage structure for organizing research materials
    - Defined agent roles and prompt templates for each stage of the workflow
    - Decided to not rely on the PubMedTool due to implementation issues
    - Planned for using the Marker package for PDF parsing

## Next Steps

The immediate next steps for the project are:

### Phase 1: Core Infrastructure (1-2 weeks)

1. **Knowledge Models Implementation**: Completed ✅
   - Implemented PaperSource, SearchTerm, and KnowledgeTopic models
   - Created storage utilities for these models
   - Implemented directory structure creation and management
   - Created comprehensive tests for all models
   - Created example script demonstrating the knowledge models and directory utilities

2. **Search Coordinator Implementation**: Completed ✅
   - Implemented AsyncSearchCoordinator with caching and error handling
   - Implemented SearchCache with disk-based and in-memory caching
   - Implemented RetryStrategy with exponential backoff
   - Integrated DirectGoogleScholarTool and SemanticScholarTool
   - Added comprehensive tests for all components
   - Created example script demonstrating usage

3. **PDF Management Implementation**: Completed ✅
   - Implemented PDFDownloadManager class for async PDF downloads with caching
   - Created MarkerWrapper class to interface with the Marker package
   - Implemented PDFProcessor class to orchestrate the download and parsing process
   - Added error handling and retry logic
   - Implemented tracking of failed PDFs for potential fallback processing
   - Added Gemini integration for improved PDF parsing
   - Created PDFProcessorTool for agent use
   - Added comprehensive tests for all components
   - Created example script demonstrating usage
   - Integrated with the research crew workflow

### Phase 2: Agent Implementation (2-3 weeks)

1. **Outline and Search Term Generation**:
   - Implement outline generator agent
   - Implement search term generator agent
   - Create prompts and test with various topics

2. **Content Processing Agents**:
   - Implement related term analyzer agent
   - Implement content distiller agent
   - Create prompts and test with sample content

3. **Synthesis and Review Agents**:
   - Implement knowledge synthesizer agent
   - Implement quality reviewer agent
   - Create prompts and test with sample content

### Phase 3: Workflow Integration (2-3 weeks)

1. **Workflow Orchestration**:
   - Implement workflow manager
   - Create state management for the workflow
   - Implement error recovery and resumption

2. **CLI Integration**:
   - Update CLI to support the new workflow
   - Add commands for each phase of the workflow
   - Implement progress tracking and reporting

3. **Testing and Refinement**:
   - Create comprehensive tests for each component
   - Test end-to-end workflow with various topics
   - Refine based on test results

## Active Decisions and Considerations

### Architecture Decisions

1. **Flow-Based Architecture**: We've implemented a flow-based architecture for the end-to-end workflow, which provides a structured, event-driven approach to AI workflows. This allows for better state management, error handling, and visualization.

2. **Metrics Collection Approach**: We're using a metrics collection system that tracks and analyzes the quality of generated articles. This provides valuable insights into the performance of the system and helps identify areas for improvement.

3. **Quality Assessment System**: We've implemented a quality assessment system that evaluates the accuracy, readability, and patient relevance of generated articles. This ensures that the articles meet high standards of quality.

4. **Risk Assessment System**: We've implemented a risk assessment system that identifies potential issues in generated articles and determines a confidence level. This helps users understand the reliability of the generated content.

### Technical Considerations

1. **API Selection**: We're using the SerperDev API for web search and the Semantic Scholar API for academic paper search. We've decided not to rely on the PubMed tool due to implementation issues. The DirectGoogleScholarTool provides direct access to Google Scholar without requiring an API key.

2. **LLM Provider**: We're using Google's Gemini 2.0 Flash model for the agents, as it provides a good balance of performance, quality, and cost with its 1M token context window.

3. **Error Handling**: We've implemented error handling in the tools, crews, and flows to manage API failures and other potential issues.

4. **Citation Validation**: We've implemented robust citation validation to ensure that all factual statements are properly attributed to reliable sources.

5. **Performance Optimization**: We're working on optimizing the article creation process to reduce latency and resource usage. This includes implementing caching strategies and optimizing API usage.

### Open Questions

1. **Metrics Refinement**: How can we refine the quality metrics to better reflect the actual quality of the articles?

2. **Performance Optimization**: What additional strategies can we implement to further optimize the article creation process?

3. **API Key Management**: What is the best approach for managing API keys (Gemini, SerperDev, PubMed, Semantic Scholar) securely while allowing for easy configuration?

4. **Gemini Model Selection**: Should we experiment with other Gemini models like gemini-1.5-pro (2M tokens) for tasks that might benefit from larger context windows or more advanced reasoning?

5. **Prompt Engineering**: Do we need to adjust our prompts to better align with Gemini models' capabilities and response patterns?

4. **Quality Assurance**: How can we further enhance the quality assurance system to ensure the accuracy and reliability of the generated content?

5. **User Experience**: How can we improve the user experience of the CLI to make it more intuitive and user-friendly?

### Current Priorities

1. **Search Coordinator Implementation**: Completed ✅
   - Implemented AsyncSearchCoordinator with caching and error handling
   - Implemented SearchCache with disk-based and in-memory caching
   - Implemented RetryStrategy with exponential backoff
   - Integrated DirectGoogleScholarTool and SemanticScholarTool
   - Added comprehensive tests for all components
   - Created example script demonstrating usage

2. **PDF Management Implementation**: Completed ✅
   - Implemented PDFDownloadManager class for async PDF downloads with caching
   - Created MarkerWrapper class to interface with the Marker package
   - Implemented PDFProcessor class to orchestrate the download and parsing process
   - Added error handling and retry logic
   - Implemented tracking of failed PDFs for potential fallback processing
   - Added Gemini integration for improved PDF parsing
   - Created PDFProcessorTool for agent use
   - Added comprehensive tests for all components
   - Created example script demonstrating usage
   - Integrated with the research crew workflow

3. **Agent Implementation**: Developing specialized agents for outline generation, search term generation, related term analysis, content distillation, knowledge synthesis, and quality review.

4. **Workflow Integration**: Implementing the knowledge synthesis workflow manager with state management and error recovery.

5. **Testing and Documentation**: Creating comprehensive tests and documentation for all components.

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Project Setup | Completed | Basic directory structure created |
| Memory Bank | Completed | Core memory bank files created |
| Implementation Plan | Completed | Comprehensive plan developed |
| Agent System | Completed | Research, content creation, and review agents implemented |
| Tool System | Completed | Search, content, and validation tools implemented |
| Workflow System | Completed | Research, content creation, review, and end-to-end workflows implemented |
| CLI Integration | Completed | Research, create, review, generate, metrics, and visualize_flow commands implemented |
| Metrics Collection | Completed | Quality metrics tracking and dashboard generation implemented |
| Knowledge Models | Completed | PaperSource, SearchTerm, and KnowledgeTopic models implemented |
| Knowledge Directory | Completed | Directory structure for organizing research materials implemented |
| Search Coordinator | Completed | AsyncSearchCoordinator with caching, retry logic, and tests implemented |
| PDF Management | Completed | PDFDownloadManager, MarkerWrapper, PDFProcessor, and PDFProcessorTool implemented with tests |
| Testing and Refinement | In Progress | Unit testing framework established, validation tools tested, DirectGoogleScholarTool tests fixed |
| Documentation | In Progress | Code documentation in progress, test documentation added |

## Recent Insights

From our implementation of the end-to-end workflow, metrics collection system, and design of the enhanced search workflow, we've gained several insights:

1. **Flow-Based Architecture**: The value of a flow-based architecture for AI workflows is evident in the end-to-end workflow implementation. It provides a structured, event-driven approach to AI workflows that allows for better state management, error handling, and visualization.

2. **Quality Metrics**: The importance of quality metrics for evaluating the performance of the system is reinforced by our implementation. They provide valuable insights into the quality of the generated articles and help identify areas for improvement.

3. **Risk Assessment**: The value of risk assessment for identifying potential issues in generated articles is evident in the quality assessment system. It helps users understand the reliability of the generated content.

4. **Visualization**: The importance of visualization for understanding complex workflows is reinforced by our implementation of the flow visualization. It helps users understand the relationships between different steps in the workflow.

5. **State Management**: The value of proper state management for tracking the article creation process is evident in the flow implementation. It ensures that the system can recover from errors and resume from where it left off.

6. **Event-Driven Architecture**: The benefits of an event-driven architecture for AI workflows are reinforced by our implementation. It allows for better separation of concerns and more flexible workflow design.

7. **Quality Assessment**: The importance of a comprehensive quality assessment system for ensuring the accuracy, readability, and patient relevance of generated articles is evident in our implementation.

8. **Dashboard Generation**: The value of dashboard generation for visualizing article quality metrics is reinforced by our implementation. It provides a clear and intuitive way to understand the performance of the system.

9. **Confidence Scoring**: The importance of confidence scoring for indicating the reliability of generated content is evident in the quality assessment system. It helps users understand the level of trust they can place in the generated articles.

10. **Risk Area Identification**: The value of risk area identification for highlighting potential issues in generated articles is reinforced by our implementation. It helps users understand the specific areas where the article may be less reliable.

11. **Pydantic Compatibility**: The importance of properly annotating class variables in Pydantic models is evident from our testing framework development. Using ClassVar annotations for class-level variables that are not meant to be model fields is essential for compatibility with newer versions of Pydantic.

12. **Quality Filtering**: The value of quality filtering in search tools is evident from our implementation of the SemanticScholarTool. Filtering papers by citation count and other quality metrics helps ensure that the agents have access to high-quality, reliable sources for their research and fact-checking.

13. **Structured Knowledge Organization**: The importance of a structured approach to organizing research materials is clear from our design of the knowledge directory system. A hierarchical structure with clear metadata makes it easier to manage and synthesize information from multiple sources.

14. **PDF Processing**: The need for robust PDF processing capabilities is evident from our plan to use the Marker package. Converting PDFs to markdown format makes it easier for LLMs to process and extract relevant information.

15. **Search Term Expansion**: The value of expanding search terms based on related terms from Google Scholar is clear from our design of the related term analyzer. This helps ensure comprehensive coverage of the topic and reduces the risk of missing important information.

16. **Agent Specialization**: The benefits of specialized agents for different stages of the knowledge synthesis process are reinforced by our design. Each agent can focus on a specific task and leverage the appropriate LLM model for that task.

17. **Asynchronous Search Coordination**: The implementation of the AsyncSearchCoordinator has demonstrated the value of asynchronous programming for search operations. By running searches in parallel across multiple sources, we can significantly reduce the overall search time while still providing comprehensive coverage.

18. **Multi-Level Caching**: The implementation of both in-memory and disk-based caching in the SearchCache has shown the importance of multi-level caching for search operations. In-memory caching provides fast access to frequently used results, while disk-based caching ensures persistence across sessions.

19. **Retry Logic with Exponential Backoff**: The implementation of the RetryStrategy with exponential backoff has demonstrated the importance of robust error handling for API calls. This approach helps manage rate limits and transient errors, improving the reliability of the search process.
