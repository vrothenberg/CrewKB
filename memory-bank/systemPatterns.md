# CrewKB System Patterns

## System Architecture

CrewKB follows a modular, agent-based architecture built on the Crew.AI framework. The system is designed to be flexible, extensible, and capable of handling different types of biomedical knowledge base articles.

```mermaid
flowchart TD
    User[User] --> CLI[CLI Interface]
    CLI --> WorkflowManager[Workflow Manager]
    
    WorkflowManager --> Workflows
    
    subgraph Workflows
        DiseaseWorkflow[Disease KB Workflow]
        BiomarkerWorkflow[Biomarker KB Workflow]
        LabTestWorkflow[Lab Test KB Workflow]
        KnowledgeSynthesisWorkflow[Knowledge Synthesis Workflow]
    end
    
    subgraph Agents
        ResearchAgents[Research Agents]
        ContentAgents[Content Creation Agents]
        ReviewAgents[Review Agents]
        SynthesisAgents[Knowledge Synthesis Agents]
    end
    
    Workflows --> Agents
    
    Agents --> Tools
    
    subgraph Tools
        SearchTools[Search Tools]
        ContentTools[Content Tools]
        ValidationTools[Validation Tools]
        PDFTools[PDF Processing Tools]
    end
    
    Agents --> KBStorage[(KB Storage)]
    
    KBStorage --> OutputFormats[JSON & Markdown]
    
    KBStorage --> KnowledgeDir[(Knowledge Directory)]
    
    KnowledgeDir --> Papers[(Research Papers)]
    KnowledgeDir --> Synthesis[(Synthesized Content)]
```

## Key Components

### 1. CLI Interface

The command-line interface serves as the primary entry point for users to interact with the CrewKB system. It allows users to:

- Initiate the creation of new knowledge base articles
- Specify topics and article types
- Monitor the progress of article creation
- Access and export completed articles

### 2. Workflow Manager

The Workflow Manager orchestrates the overall process of knowledge base article creation. It:

- Selects the appropriate workflow based on the article type
- Manages the execution of workflows
- Handles transitions between different phases
- Monitors the progress and status of article creation

### 3. Specialized Workflows

CrewKB implements different workflows for various types of biomedical topics:

- **Disease KB Workflow**: Specialized for creating articles about health conditions
- **Biomarker KB Workflow**: Tailored for biomarker-related articles
- **Lab Test KB Workflow**: Designed for articles about laboratory tests
- **Knowledge Synthesis Workflow**: Orchestrates the enhanced search and knowledge synthesis process

Each workflow defines the sequence of tasks, agent interactions, and specific requirements for its article type.

The Knowledge Synthesis Workflow follows a distinct pattern:

```mermaid
flowchart TD
    Start[Topic Selection] --> OutlineGen[Outline Generation\nGemini 2.5 Pro]
    OutlineGen --> SearchTermGen[Search Term Generation\nGemini 2.5 Pro]
    
    subgraph Search["Search Phase"]
        SearchTermGen --> GoogleScholar[Google Scholar Search\nDirectGoogleScholarTool]
        SearchTermGen --> SemanticScholar[Semantic Scholar Search\nSemanticScholarTool]
        GoogleScholar --> RelatedTerms[Related Term Analysis\nGemini 2.0 Flash]
        RelatedTerms --> |New Terms| GoogleScholar
        GoogleScholar --> PDFLinks[PDF Link Extraction]
        SemanticScholar --> PDFLinks
    end
    
    subgraph Processing["Processing Phase"]
        PDFLinks --> PDFDownload[PDF Download Manager]
        PDFDownload --> PDFParsing[PDF Parsing\nMarker]
        PDFParsing --> ContentDistillation[Content Distillation\nGemini 2.0 Flash]
    end
    
    subgraph Synthesis["Synthesis Phase"]
        ContentDistillation --> KnowledgeSynthesis[Knowledge Synthesis\nGemini 2.5 Pro]
        KnowledgeSynthesis --> ArticleGeneration[Article Generation]
    end
    
    subgraph Review["Review Phase"]
        ArticleGeneration --> QualityReview[Quality Review\nGemini 2.5 Pro]
        QualityReview --> |Needs Revision| KnowledgeSynthesis
        QualityReview --> |Approved| FinalArticle[Final Knowledge Base Article]
    end
    
    style Search fill:#f9f9ff,stroke:#0077b6,stroke-width:2px
    style Processing fill:#f9f9ff,stroke:#0077b6,stroke-width:2px
    style Synthesis fill:#f9f9ff,stroke:#0077b6,stroke-width:2px
    style Review fill:#f9f9ff,stroke:#0077b6,stroke-width:2px
```

### 4. Agent System

The agent system consists of specialized AI agents with distinct roles and responsibilities:

#### Research Agents
- **Medical Literature Researcher**: Searches and analyzes scientific literature
- **Clinical Guidelines Analyst**: Identifies and summarizes clinical guidelines
- **Medical Data Synthesizer**: Compiles and organizes research findings

#### Content Creation Agents
- **Medical Content Architect**: Designs article outlines
- **Medical Content Writer**: Transforms research into structured content
- **Medical Citation Specialist**: Manages citations and references

#### Review Agents
- **Medical Accuracy Reviewer**: Verifies scientific accuracy
- **Medical Content Editor**: Ensures quality and adherence to structure
- **Patient Perspective Reviewer**: Evaluates accessibility for non-specialists

#### Knowledge Synthesis Agents
- **Outline Generator**: Creates comprehensive outlines for knowledge base articles using Gemini 2.5 Pro
- **Search Term Generator**: Generates effective search terms based on the outline using Gemini 2.5 Pro
- **Related Term Analyzer**: Analyzes related search terms to expand research coverage using Gemini 2.0 Flash
- **Content Distiller**: Extracts relevant information from research papers using Gemini 2.0 Flash
- **Knowledge Synthesizer**: Synthesizes distilled content into a coherent article using Gemini 2.5 Pro
- **Quality Reviewer**: Reviews articles for quality, accuracy, and completeness using Gemini 2.5 Pro

### 5. Tool System

The tool system provides specialized capabilities to the agents:

#### Search Tools
- **SerperDevTool**: For Google search
- **DirectGoogleScholarTool**: For searching Google Scholar directly without an API
- **SemanticScholarTool**: For searching academic papers with citation count and quality filtering
- **WebpageScraperTool**: For scraping web pages using Serper's API
- **Crawl4AIScraperTool**: For more advanced web scraping

#### Search Coordination
- **AsyncSearchCoordinator**: Coordinates searches across multiple tools with caching and error handling
- **SearchCache**: Provides disk-based and in-memory caching for search results
- **RetryStrategy**: Implements retry logic with exponential backoff for API calls

#### Content Tools
- **OutlineGeneratorTool**: For creating article outlines
- **CitationFormatterTool**: For formatting citations
- **ContentStructureTool**: For structuring content according to templates

#### Validation Tools
- **FactCheckerTool**: For verifying factual accuracy
- **StructureValidatorTool**: For validating article structure
- **HallucinationDetectorTool**: For identifying unsupported claims

#### PDF Processing Tools
- **PDFDownloadManager**: For downloading PDFs from extracted links with caching and retry logic
- **MarkerWrapper**: For parsing PDFs to markdown using the Marker package with Gemini integration
- **PDFProcessor**: For orchestrating the download and parsing process with error tracking

### 6. Storage System

The storage system manages the persistence of knowledge base articles and research materials:

- **JSON Storage**: Stores articles in structured JSON format
- **Markdown Storage**: Converts articles to Markdown for human readability
- **Version Control**: Maintains article history and revisions
- **Knowledge Directory**: Organizes research materials by topic

#### Knowledge Directory Structure

The knowledge directory follows a hierarchical structure:

```
knowledge/
├── {topic1}/
│   ├── metadata.json            # KnowledgeTopic model
│   ├── outline.md               # Generated outline
│   ├── search_terms.json        # List of search terms
│   ├── papers/
│   │   ├── {paper_id1}/
│   │   │   ├── metadata.json    # PaperSource model
│   │   │   ├── paper.pdf        # Downloaded PDF
│   │   │   ├── paper.md         # Parsed markdown
│   │   │   └── distilled.md     # Distilled content
│   │   └── {paper_id2}/
│   │       └── ...
│   ├── synthesis.md             # Synthesized content
│   ├── draft.md                 # Draft article
│   ├── review.md                # Review feedback
│   └── final.md                 # Final article
└── {topic2}/
    └── ...
```

## Design Patterns

### 1. Agent-Based Architecture

CrewKB uses an agent-based architecture where specialized agents collaborate to accomplish complex tasks. This pattern:

- Enables division of labor based on specialized expertise
- Facilitates parallel processing of different aspects of article creation
- Allows for autonomous decision-making within defined roles
- Supports flexible workflows with dynamic task allocation
- Leverages different LLM models for different tasks (e.g., Gemini 2.5 Pro for complex reasoning, Gemini 2.0 Flash for efficiency)

### 2. Workflow Pattern

The workflow pattern organizes the article creation process into distinct phases with clear transitions:

- **Sequential Processing**: Tasks that depend on previous outputs are arranged sequentially
- **Parallel Processing**: Independent tasks can be executed concurrently
- **Conditional Branching**: Workflow can adapt based on content requirements or quality assessments
- **Iterative Refinement**: Supports cycling back to previous phases for improvements
- **Feedback Loops**: Enables continuous improvement based on review feedback

### 2.1 Knowledge Synthesis Workflow Pattern

The knowledge synthesis workflow follows a specialized pattern:

- **Outline-Driven Research**: Research is guided by a comprehensive outline
- **Search Term Expansion**: Search terms are expanded based on related terms
- **Multi-Source Integration**: Information is gathered from multiple sources
- **Hierarchical Processing**: Content is processed at multiple levels (PDF → Markdown → Distilled Content → Synthesized Article)
- **Quality-Gated Progression**: Content must pass quality checks before proceeding to the next phase

### 3. Tool Composition Pattern

The tool composition pattern allows agents to leverage specialized tools for specific tasks:

- **Tool Registry**: Central registration of available tools
- **Tool Selection**: Agents select appropriate tools based on task requirements
- **Tool Chaining**: Complex operations can be accomplished by chaining multiple tools
- **Tool Abstraction**: Common interfaces allow for tool interchangeability
- **Tool Coordination**: The Search Coordinator manages multiple search tools with caching and error handling:
  - **Parallel Execution**: Runs searches across multiple sources concurrently using asyncio
  - **Multi-Level Caching**: Implements both in-memory and disk-based caching for search results
  - **Error Resilience**: Handles API failures gracefully with retry logic and exponential backoff
  - **Result Normalization**: Converts search results from different sources into a common format
  - **Quality Filtering**: Supports filtering results by citation count and publication year

### 4. Model-View-Controller (MVC)

The system follows an MVC pattern for separation of concerns:

- **Model**: Pydantic models define the structure of knowledge base articles
- **View**: Output formatters (JSON, Markdown) present articles in different formats
- **Controller**: Workflow manager and agents control the article creation process

### 5. Factory Pattern

Factory patterns are used to create different types of agents, tools, and workflows:

- **Agent Factory**: Creates specialized agents based on role requirements
- **Tool Factory**: Instantiates appropriate tools based on capability needs
- **Workflow Factory**: Constructs workflows tailored to specific article types

## Component Relationships

### Agent-Tool Relationship

Agents use tools to perform specific tasks:

- Research agents use search tools to gather information
- Content agents use content tools to structure and format articles
- Review agents use validation tools to ensure quality and accuracy
- Knowledge synthesis agents use a combination of search tools, PDF processing tools, and LLM capabilities

### Workflow-Agent Relationship

Workflows orchestrate the collaboration between agents:

- Workflows define the sequence of agent interactions
- Workflows manage the handoff of information between agents
- Workflows determine when to involve specific agents based on task requirements
- The Knowledge Synthesis Workflow coordinates specialized agents for different stages of the process

### Storage-Output Relationship

The storage system manages the persistence and presentation of articles and research materials:

- Articles are stored internally in a structured format (JSON)
- Articles can be exported in different formats (Markdown, JSON)
- Storage system maintains version history and metadata
- The Knowledge Directory organizes research materials by topic in a hierarchical structure
- Research papers are stored with metadata, original PDFs, parsed markdown, and distilled content

## Technical Decisions

### 1. Pydantic for Data Modeling

CrewKB uses Pydantic for defining article structures and research metadata because:

- It provides strong typing and validation
- It supports JSON serialization/deserialization
- It enables clear documentation of data requirements
- It integrates well with modern Python codebases
- It allows for nested models and complex relationships

### 2. Crew.AI for Agent Orchestration

Crew.AI was chosen as the framework for agent orchestration because:

- It provides a robust system for defining and managing agents
- It supports complex workflows and agent interactions
- It integrates with various LLM providers
- It offers tools for monitoring and debugging agent behavior

### 3. Modular Design for Extensibility

The system is designed with modularity in mind to support:

- Addition of new article types without modifying existing code
- Integration of new search sources and tools
- Customization of workflows for specific requirements
- Independent testing and development of components
- Flexible knowledge organization with the Knowledge Directory structure

### 4. CLI-First Approach

The system prioritizes a command-line interface because:

- It provides a simple, direct way to interact with the system
- It facilitates automation and scripting
- It reduces frontend development complexity
- It aligns with the technical nature of the primary users

### 5. Dual Storage Format

Articles are stored in both JSON and Markdown formats because:

- JSON provides structured data for programmatic access
- Markdown offers human-readable content for review and publication
- Dual formats support different use cases without conversion overhead

### 6. Hierarchical Knowledge Organization

Research materials are organized in a hierarchical structure because:

- It provides a clear organization by topic
- It keeps related materials together
- It supports the full research lifecycle from search to synthesis
- It enables tracking of the provenance of information
- It facilitates review and refinement of the knowledge base
