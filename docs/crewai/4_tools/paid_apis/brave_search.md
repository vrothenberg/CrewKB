# Brave Search

> The `BraveSearchTool` is designed to search the internet using the Brave Search API.

# `BraveSearchTool`

## Description

This tool is designed to perform web searches using the Brave Search API. It allows you to search the internet with a specified query and retrieve relevant results. The tool supports customizable result counts and country-specific searches.

## Installation

To incorporate this tool into your project, follow the installation instructions below:

```shell
pip install 'crewai[tools]'
```

## Steps to Get Started

To effectively use the `BraveSearchTool`, follow these steps:

1. **Package Installation**: Confirm that the `crewai[tools]` package is installed in your Python environment.
2. **API Key Acquisition**: Acquire a Brave Search API key by registering at [Brave Search API](https://api.search.brave.com/app/keys).
3. **Environment Configuration**: Store your obtained API key in an environment variable named `BRAVE_API_KEY` to facilitate its use by the tool.

## Example

The following example demonstrates how to initialize the tool and execute a search with a given query:

```python Code
from crewai_tools import BraveSearchTool

# Initialize the tool for internet searching capabilities
tool = BraveSearchTool()

# Execute a search
results = tool.run(search_query="CrewAI agent framework")
print(results)
```

## Parameters

The `BraveSearchTool` accepts the following parameters:

* **search\_query**: Mandatory. The search query you want to use to search the internet.
* **country**: Optional. Specify the country for the search results. Default is empty string.
* **n\_results**: Optional. Number of search results to return. Default is `10`.
* **save\_file**: Optional. Whether to save the search results to a file. Default is `False`.

## Example with Parameters

Here is an example demonstrating how to use the tool with additional parameters:

```python Code
from crewai_tools import BraveSearchTool

# Initialize the tool with custom parameters
tool = BraveSearchTool(
    country="US",
    n_results=5,
    save_file=True
)

# Execute a search
results = tool.run(search_query="Latest AI developments")
print(results)
```

## Agent Integration Example

Here's how to integrate the `BraveSearchTool` with a CrewAI agent:

```python Code
from crewai import Agent
from crewai.project import agent
from crewai_tools import BraveSearchTool

# Initialize the tool
brave_search_tool = BraveSearchTool()

# Define an agent with the BraveSearchTool
@agent
def researcher(self) -> Agent:
    return Agent(
        config=self.agents_config["researcher"],
        allow_delegation=False,
        tools=[brave_search_tool]
    )
```

## Conclusion

By integrating the `BraveSearchTool` into Python projects, users gain the ability to conduct real-time, relevant searches across the internet directly from their applications. The tool provides a simple interface to the powerful Brave Search API, making it easy to retrieve and process search results programmatically. By adhering to the setup and usage guidelines provided, incorporating this tool into projects is streamlined and straightforward.
