# Selenium Scraper

> The `SeleniumScrapingTool` is designed to extract and read the content of a specified website using Selenium.

# `SeleniumScrapingTool`

<Note>
  This tool is currently in development. As we refine its capabilities, users may encounter unexpected behavior.
  Your feedback is invaluable to us for making improvements.
</Note>

## Description

The `SeleniumScrapingTool` is crafted for high-efficiency web scraping tasks.
It allows for precise extraction of content from web pages by using CSS selectors to target specific elements.
Its design caters to a wide range of scraping needs, offering flexibility to work with any provided website URL.

## Installation

To use this tool, you need to install the CrewAI tools package and Selenium:

```shell
pip install 'crewai[tools]'
uv add selenium webdriver-manager
```

You'll also need to have Chrome installed on your system, as the tool uses Chrome WebDriver for browser automation.

## Example

The following example demonstrates how to use the `SeleniumScrapingTool` with a CrewAI agent:

```python Code
from crewai import Agent, Task, Crew, Process
from crewai_tools import SeleniumScrapingTool

# Initialize the tool
selenium_tool = SeleniumScrapingTool()

# Define an agent that uses the tool
web_scraper_agent = Agent(
    role="Web Scraper",
    goal="Extract information from websites using Selenium",
    backstory="An expert web scraper who can extract content from dynamic websites.",
    tools=[selenium_tool],
    verbose=True,
)

# Example task to scrape content from a website
scrape_task = Task(
    description="Extract the main content from the homepage of example.com. Use the CSS selector 'main' to target the main content area.",
    expected_output="The main content from example.com's homepage.",
    agent=web_scraper_agent,
)

# Create and run the crew
crew = Crew(
    agents=[web_scraper_agent],
    tasks=[scrape_task],
    verbose=True,
    process=Process.sequential,
)
result = crew.kickoff()
```

You can also initialize the tool with predefined parameters:

```python Code
# Initialize the tool with predefined parameters
selenium_tool = SeleniumScrapingTool(
    website_url='https://example.com',
    css_element='.main-content',
    wait_time=5
)

# Define an agent that uses the tool
web_scraper_agent = Agent(
    role="Web Scraper",
    goal="Extract information from websites using Selenium",
    backstory="An expert web scraper who can extract content from dynamic websites.",
    tools=[selenium_tool],
    verbose=True,
)
```

## Parameters

The `SeleniumScrapingTool` accepts the following parameters during initialization:

* **website\_url**: Optional. The URL of the website to scrape. If provided during initialization, the agent won't need to specify it when using the tool.
* **css\_element**: Optional. The CSS selector for the elements to extract. If provided during initialization, the agent won't need to specify it when using the tool.
* **cookie**: Optional. A dictionary containing cookie information, useful for simulating a logged-in session to access restricted content.
* **wait\_time**: Optional. Specifies the delay (in seconds) before scraping, allowing the website and any dynamic content to fully load. Default is `3` seconds.
* **return\_html**: Optional. Whether to return the HTML content instead of just the text. Default is `False`.

When using the tool with an agent, the agent will need to provide the following parameters (unless they were specified during initialization):

* **website\_url**: Required. The URL of the website to scrape.
* **css\_element**: Required. The CSS selector for the elements to extract.

## Agent Integration Example

Here's a more detailed example of how to integrate the `SeleniumScrapingTool` with a CrewAI agent:

```python Code
from crewai import Agent, Task, Crew, Process
from crewai_tools import SeleniumScrapingTool

# Initialize the tool
selenium_tool = SeleniumScrapingTool()

# Define an agent that uses the tool
web_scraper_agent = Agent(
    role="Web Scraper",
    goal="Extract and analyze information from dynamic websites",
    backstory="""You are an expert web scraper who specializes in extracting 
    content from dynamic websites that require browser automation. You have 
    extensive knowledge of CSS selectors and can identify the right selectors 
    to target specific content on any website.""",
    tools=[selenium_tool],
    verbose=True,
)

# Create a task for the agent
scrape_task = Task(
    description="""
    Extract the following information from the news website at {website_url}:
    
    1. The headlines of all featured articles (CSS selector: '.headline')
    2. The publication dates of these articles (CSS selector: '.pub-date')
    3. The author names where available (CSS selector: '.author')
    
    Compile this information into a structured format with each article's details grouped together.
    """,
    expected_output="A structured list of articles with their headlines, publication dates, and authors.",
    agent=web_scraper_agent,
)

# Run the task
crew = Crew(
    agents=[web_scraper_agent],
    tasks=[scrape_task],
    verbose=True,
    process=Process.sequential,
)
result = crew.kickoff(inputs={"website_url": "https://news-example.com"})
```

## Implementation Details

The `SeleniumScrapingTool` uses Selenium WebDriver to automate browser interactions:

```python Code
class SeleniumScrapingTool(BaseTool):
    name: str = "Read a website content"
    description: str = "A tool that can be used to read a website content."
    args_schema: Type[BaseModel] = SeleniumScrapingToolSchema
    
    def _run(self, **kwargs: Any) -> Any:
        website_url = kwargs.get("website_url", self.website_url)
        css_element = kwargs.get("css_element", self.css_element)
        return_html = kwargs.get("return_html", self.return_html)
        driver = self._create_driver(website_url, self.cookie, self.wait_time)

        content = self._get_content(driver, css_element, return_html)
        driver.close()

        return "\n".join(content)
```

The tool performs the following steps:

1. Creates a headless Chrome browser instance
2. Navigates to the specified URL
3. Waits for the specified time to allow the page to load
4. Adds any cookies if provided
5. Extracts content based on the CSS selector
6. Returns the extracted content as text or HTML
7. Closes the browser instance

## Handling Dynamic Content

The `SeleniumScrapingTool` is particularly useful for scraping websites with dynamic content that is loaded via JavaScript. By using a real browser instance, it can:

1. Execute JavaScript on the page
2. Wait for dynamic content to load
3. Interact with elements if needed
4. Extract content that would not be available with simple HTTP requests

You can adjust the `wait_time` parameter to ensure that all dynamic content has loaded before extraction.

## Conclusion

The `SeleniumScrapingTool` provides a powerful way to extract content from websites using browser automation. By enabling agents to interact with websites as a real user would, it facilitates scraping of dynamic content that would be difficult or impossible to extract using simpler methods. This tool is particularly useful for research, data collection, and monitoring tasks that involve modern web applications with JavaScript-rendered content.
