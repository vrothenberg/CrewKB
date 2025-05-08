# CrewKB Tools

This document provides a detailed technical explanation of the tools used in the CrewKB system. Each tool is designed to perform a specific function in the knowledge base article creation process, from research to content creation to validation.

## Table of Contents

- [CrewKB Tools](#crewkb-tools)
  - [Table of Contents](#table-of-contents)
  - [Tool System Overview](#tool-system-overview)
  - [Content Tools](#content-tools)
    - [OutlineGeneratorTool](#outlinegeneratortool)
    - [ContentStructureTool](#contentstructuretool)
    - [CitationFormatterTool](#citationformattertool)
  - [Search Tools](#search-tools)
    - [SerperDevTool](#serperdevtool)
    - [GoogleScholarTool](#googlescholartool)
    - [PubMedSearchTool](#pubmedsearchtool)
    - [WebpageScraperTool](#webpagescrapertool)
  - [Tool Factory](#tool-factory)
    - [create\_tool(tool\_name, \*\*kwargs)](#create_tooltool_name-kwargs)
    - [create\_tools\_for\_agent(agent\_name)](#create_tools_for_agentagent_name)
  - [Tool Integration](#tool-integration)

## Tool System Overview

The CrewKB tool system is built on top of the CrewAI `BaseTool` class, which provides a standardized interface for all tools. Each tool follows a consistent pattern:

1. **Input Schema**: Defined using Pydantic models to validate input parameters
2. **Tool Metadata**: Name and description for agent discovery and usage
3. **Core Logic**: Implemented in the `_run` method

Tools are integrated with agents through the `ToolFactory`, which centralizes tool creation and assignment to specific agents based on their roles.


## Content Tools

### OutlineGeneratorTool

**Purpose**: Generates structured outlines for medical knowledge base articles based on article type and research data.

**Technical Implementation**:
- **Input Schema**: `OutlineGeneratorToolInput`
  - `article_type` (str): Type of article (disease, biomarker, or lab test)
  - `topic` (str): The topic of the article
  - `research_data` (str): Research data to use for generating the outline

- **Template System**:
  - Maintains predefined templates for different article types:
    - Disease template: 16 sections including Overview, Symptoms, Causes, Treatment, etc.
    - Biomarker template: 14 sections including Biological Role, Clinical Significance, etc.
    - Lab test template: 14 sections including Test Purpose, Preparation, Procedure, etc.
  - Each template defines sections and subsections in a hierarchical structure

- **Outline Generation**:
  - Selects appropriate template based on article type
  - Generates Markdown-formatted outline with sections and subsections
  - Adds notes about customization and research data integration

- **Limitations**:
  - Templates are static and predefined
  - Does not dynamically adapt sections based on research data content
  - Serves as a starting point that requires manual refinement

### ContentStructureTool

**Purpose**: Validates article structure against predefined models and ensures section completeness.

**Technical Implementation**:
- **Input Schema**: `ContentStructureToolInput`
  - `article_type` (str): Type of article (disease, biomarker, or lab test)
  - `content` (str): The article content to validate

- **Validation Process**:
  - Determines required sections based on article type
  - Extracts sections from Markdown content using heading patterns
  - Compares extracted sections against required sections
  - Identifies missing, empty, and extra sections
  - Analyzes section lengths (word count)

- **Output Format**:
  - Provides validation results with clear pass/fail indicators
  - Lists missing required sections
  - Lists empty sections that need content
  - Lists additional sections not in the required set
  - Provides word count analysis for each section

- **Limitations**:
  - Section extraction relies on consistent Markdown heading formatting
  - Does not validate section content quality or relevance
  - Required sections are hardcoded rather than dynamically determined

### CitationFormatterTool

**Purpose**: Formats citations in standard medical citation styles and validates citation completeness.

**Technical Implementation**:
- **Input Schema**: `CitationFormatterToolInput`
  - `citations` (List[Citation]): List of citations to format
  - `style` (str): Citation style (ama, apa, or vancouver)

- **Citation Model**:
  - Uses Pydantic model `Citation` with fields:
    - Required: authors, title, year
    - Optional: journal, volume, issue, pages, doi, url, publisher, accessed_date

- **Validation Logic**:
  - Checks for required fields (authors, title, year)
  - Validates context-specific requirements:
    - Journal articles should have volume or pages
    - Online resources with URLs should have accessed date
  - Provides detailed validation results for each citation

- **Formatting Logic**:
  - Implements formatters for three citation styles:
    - AMA (American Medical Association)
    - APA (American Psychological Association)
    - Vancouver
  - Each formatter follows style-specific rules for ordering elements, punctuation, and formatting

- **Limitations**:
  - Limited to three citation styles
  - Does not validate author name format consistency
  - Does not verify DOI or URL validity

## Search Tools

### SerperDevTool

**Purpose**: Performs web searches using the SerperDev API to retrieve information from Google search results.

**Technical Implementation**:
- **Input Schema**: `SerperDevToolInput`
  - `query` (str): The search query to perform
  - `num_results` (int, default=10): Number of results to return
  - `search_type` (str, default="search"): Type of search to perform

- **API Integration**:
  - Requires `SERPER_API_KEY` environment variable
  - Makes POST requests to `https://google.serper.dev/search`
  - Sends JSON payload with query and result count parameters
  - Handles API errors and returns formatted error messages

- **Result Processing**:
  - Parses JSON response from SerperDev API
  - Extracts organic search results, knowledge graph data, and related searches
  - Formats results into a readable string with numbered entries

- **Limitations**:
  - Depends on external API availability
  - Rate limited based on SerperDev API plan
  - Results may vary based on Google's search algorithm changes

### GoogleScholarTool

**Purpose**: Searches academic literature using Serper's Google Scholar API endpoint.

**Technical Implementation**:
- **Input Schema**: `GoogleScholarToolInput`
  - `query` (str): The search query to perform
  - `num_results` (int, default=5): Number of results to return

- **API Integration**:
  - Requires `SERPER_API_KEY` environment variable
  - Makes POST requests to `https://google.serper.dev/scholar`
  - Sends JSON payload with query and result count parameters
  - Handles API errors and returns formatted error messages

- **Result Processing**:
  - Parses JSON response from Serper's Google Scholar API
  - Extracts academic paper details: title, authors, publication, year, citation count
  - Formats results into a readable string with numbered entries

- **Limitations**:
  - Depends on external API availability
  - Rate limited based on SerperDev API plan
  - May not provide full text access to papers

### PubMedSearchTool

**Purpose**: Searches medical literature on PubMed using the Entrez API from the Biopython package.

**Technical Implementation**:
- **Input Schema**: `PubMedSearchToolInput`
  - `query` (str): The search query to perform
  - `max_results` (int, default=10): Maximum number of results to return
  - `sort` (str, default="relevance"): How to sort results (relevance, date)

- **API Integration**:
  - Requires `ENTREZ_EMAIL` environment variable (mandatory for Entrez API)
  - Optionally uses `ENTREZ_API_KEY` for higher rate limits
  - Uses Biopython's Entrez module for API interaction
  - Performs two-step process: search for article IDs, then fetch article details

- **Result Processing**:
  - Parses XML response from PubMed
  - Extracts article metadata: title, authors, journal, publication date, abstract, PMID
  - Formats results into a readable string with numbered entries

- **Limitations**:
  - Requires Biopython package installation
  - Depends on NCBI Entrez API availability
  - Limited to 3 requests per second without API key (10 with key)
  - Abstract text is truncated to 200 characters in output

### WebpageScraperTool

**Purpose**: Scrapes web pages and extracts their content using Serper's scrape API.

**Technical Implementation**:
- **Input Schema**: `WebpageScraperToolInput`
  - `url` (str): The URL of the webpage to scrape
  - `include_markdown` (bool, default=True): Whether to include markdown in the response

- **API Integration**:
  - Requires `SERPER_API_KEY` environment variable
  - Makes POST requests to `https://scrape.serper.dev`
  - Sends JSON payload with URL and markdown preference
  - Handles API errors and returns formatted error messages

- **Result Processing**:
  - Parses JSON response from Serper's scrape API
  - Extracts page title, content (markdown or text), and metadata
  - Formats results into a readable string

- **Limitations**:
  - Depends on external API availability
  - Some websites may block scraping
  - Content extraction quality varies by website
  - Rate limited based on SerperDev API plan

## Tool Factory

The `ToolFactory` centralizes tool creation and management, providing two main methods:

### create_tool(tool_name, **kwargs)

Creates a tool instance based on the tool name:

- **Search Tools**:
  - `"serper_dev"` → `SerperDevTool`
  - `"pubmed_search"` → `PubMedSearchTool`
  - `"google_scholar"` → `GoogleScholarTool`
  - `"webpage_scraper"` → `WebpageScraperTool`

- **Content Tools**:
  - `"outline_generator"` → `OutlineGeneratorTool`
  - `"content_structure"` → `ContentStructureTool`
  - `"citation_formatter"` → `CitationFormatterTool`

### create_tools_for_agent(agent_name)

Creates a list of tools appropriate for a specific agent:

- **Research Agents**:
  - `"medical_literature_researcher"` → `[GoogleScholarTool, PubMedSearchTool, WebpageScraperTool]`
  - `"clinical_guidelines_analyst"` → `[SerperDevTool, GoogleScholarTool, WebpageScraperTool]`
  - `"medical_data_synthesizer"` → `[WebpageScraperTool]`

- **Content Agents**:
  - `"medical_content_architect"` → `[OutlineGeneratorTool]`
  - `"medical_content_writer"` → `[ContentStructureTool]`
  - `"medical_citation_specialist"` → `[CitationFormatterTool, GoogleScholarTool]`

- **Review Agents**:
  - `"medical_accuracy_reviewer"` → `[GoogleScholarTool, PubMedSearchTool, WebpageScraperTool]`
  - `"medical_content_editor"` → `[]` (LLM handles readability analysis)
  - `"patient_perspective_reviewer"` → `[]`
  - `"review_manager"` → `[]`

## Tool Integration

Tools are integrated into the CrewKB workflow through the following process:

1. **Agent Configuration**: Each agent is configured with specific tools based on its role
2. **Tool Instantiation**: The `ToolFactory` creates tool instances when agents are initialized
3. **Tool Invocation**: Agents invoke tools during task execution using the CrewAI framework
4. **Result Processing**: Tool results are incorporated into agent reasoning and outputs

The tool assignment follows a specialized pattern where each agent receives only the tools relevant to its specific role in the knowledge base article creation process. This ensures that agents have access to the capabilities they need without being overwhelmed by irrelevant tools.
