# Docs.Crawl4Ai.Com

[Crawl4AI Documentation (v0.6.x)](https://docs.crawl4ai.com/)
  * [ Home ](https://docs.crawl4ai.com/)
  * [ Ask AI ](https://docs.crawl4ai.com/core/ask-ai/)
  * [ Quick Start ](https://docs.crawl4ai.com/core/quickstart/)
  * [ Code Examples ](https://docs.crawl4ai.com/core/examples/)
  * [ Search ](https://docs.crawl4ai.com/)


×
  * Home
  * [Ask AI](https://docs.crawl4ai.com/core/ask-ai/)
  * [Quick Start](https://docs.crawl4ai.com/core/quickstart/)
  * [Code Examples](https://docs.crawl4ai.com/core/examples/)
  * Setup & Installation
    * [Installation](https://docs.crawl4ai.com/core/installation/)
    * [Docker Deployment](https://docs.crawl4ai.com/core/docker-deployment/)
  * Blog & Changelog
    * [Blog Home](https://docs.crawl4ai.com/blog/)
    * [Changelog](https://github.com/unclecode/crawl4ai/blob/main/CHANGELOG.md)
  * Core
    * [Command Line Interface](https://docs.crawl4ai.com/core/cli/)
    * [Simple Crawling](https://docs.crawl4ai.com/core/simple-crawling/)
    * [Deep Crawling](https://docs.crawl4ai.com/core/deep-crawling/)
    * [Crawler Result](https://docs.crawl4ai.com/core/crawler-result/)
    * [Browser, Crawler & LLM Config](https://docs.crawl4ai.com/core/browser-crawler-config/)
    * [Markdown Generation](https://docs.crawl4ai.com/core/markdown-generation/)
    * [Fit Markdown](https://docs.crawl4ai.com/core/fit-markdown/)
    * [Page Interaction](https://docs.crawl4ai.com/core/page-interaction/)
    * [Content Selection](https://docs.crawl4ai.com/core/content-selection/)
    * [Cache Modes](https://docs.crawl4ai.com/core/cache-modes/)
    * [Local Files & Raw HTML](https://docs.crawl4ai.com/core/local-files/)
    * [Link & Media](https://docs.crawl4ai.com/core/link-media/)
  * Advanced
    * [Overview](https://docs.crawl4ai.com/advanced/advanced-features/)
    * [File Downloading](https://docs.crawl4ai.com/advanced/file-downloading/)
    * [Lazy Loading](https://docs.crawl4ai.com/advanced/lazy-loading/)
    * [Hooks & Auth](https://docs.crawl4ai.com/advanced/hooks-auth/)
    * [Proxy & Security](https://docs.crawl4ai.com/advanced/proxy-security/)
    * [Session Management](https://docs.crawl4ai.com/advanced/session-management/)
    * [Multi-URL Crawling](https://docs.crawl4ai.com/advanced/multi-url-crawling/)
    * [Crawl Dispatcher](https://docs.crawl4ai.com/advanced/crawl-dispatcher/)
    * [Identity Based Crawling](https://docs.crawl4ai.com/advanced/identity-based-crawling/)
    * [SSL Certificate](https://docs.crawl4ai.com/advanced/ssl-certificate/)
    * [Network & Console Capture](https://docs.crawl4ai.com/advanced/network-console-capture/)
  * Extraction
    * [LLM-Free Strategies](https://docs.crawl4ai.com/extraction/no-llm-strategies/)
    * [LLM Strategies](https://docs.crawl4ai.com/extraction/llm-strategies/)
    * [Clustering Strategies](https://docs.crawl4ai.com/extraction/clustring-strategies/)
    * [Chunking](https://docs.crawl4ai.com/extraction/chunking/)
  * API Reference
    * [AsyncWebCrawler](https://docs.crawl4ai.com/api/async-webcrawler/)
    * [arun()](https://docs.crawl4ai.com/api/arun/)
    * [arun_many()](https://docs.crawl4ai.com/api/arun_many/)
    * [Browser, Crawler & LLM Config](https://docs.crawl4ai.com/api/parameters/)
    * [CrawlResult](https://docs.crawl4ai.com/api/crawl-result/)
    * [Strategies](https://docs.crawl4ai.com/api/strategies/)


  * [🚀🤖 Crawl4AI: Open-Source LLM-Friendly Web Crawler & Scraper](https://docs.crawl4ai.com/#crawl4ai-open-source-llm-friendly-web-crawler-scraper)
  * [Quick Start](https://docs.crawl4ai.com/#quick-start)
  * [Video Tutorial](https://docs.crawl4ai.com/#video-tutorial)
  * [What Does Crawl4AI Do?](https://docs.crawl4ai.com/#what-does-crawl4ai-do)
  * [Documentation Structure](https://docs.crawl4ai.com/#documentation-structure)
  * [How You Can Support](https://docs.crawl4ai.com/#how-you-can-support)
  * [Quick Links](https://docs.crawl4ai.com/#quick-links)


# 🚀🤖 Crawl4AI: Open-Source LLM-Friendly Web Crawler & Scraper
[ ![unclecode%2Fcrawl4ai | Trendshift](https://trendshift.io/api/badge/repositories/11716) ](https://trendshift.io/repositories/11716)
[ ![GitHub Stars](https://img.shields.io/github/stars/unclecode/crawl4ai?style=social) ](https://github.com/unclecode/crawl4ai/stargazers) [ ![GitHub Forks](https://img.shields.io/github/forks/unclecode/crawl4ai?style=social) ](https://github.com/unclecode/crawl4ai/network/members) [ ![PyPI version](https://badge.fury.io/py/crawl4ai.svg) ](https://badge.fury.io/py/crawl4ai)
[ ![Python Version](https://img.shields.io/pypi/pyversions/crawl4ai) ](https://pypi.org/project/crawl4ai/) [ ![Downloads](https://static.pepy.tech/badge/crawl4ai/month) ](https://pepy.tech/project/crawl4ai) [ ![License](https://img.shields.io/github/license/unclecode/crawl4ai) ](https://github.com/unclecode/crawl4ai/blob/main/LICENSE)
Crawl4AI is the #1 trending GitHub repository, actively maintained by a vibrant community. It delivers blazing-fast, AI-ready web crawling tailored for large language models, AI agents, and data pipelines. Fully open source, flexible, and built for real-time performance, **Crawl4AI** empowers developers with unmatched speed, precision, and deployment ease.
> **Note** : If you're looking for the old documentation, you can access it [here](https://old.docs.crawl4ai.com).
## Quick Start
Here's a quick example to show you how easy it is to use Crawl4AI with its asynchronous capabilities:
```
import asyncio
from crawl4ai import AsyncWebCrawler
async def main():
  # Create an instance of AsyncWebCrawler
  async with AsyncWebCrawler() as crawler:
    # Run the crawler on a URL
    result = await crawler.arun(url="https://crawl4ai.com")
    # Print the extracted content
    print(result.markdown)
# Run the async main function
asyncio.run(main())
Copy
```

## Video Tutorial
## What Does Crawl4AI Do?
Crawl4AI is a feature-rich crawler and scraper that aims to:
1. **Generate Clean Markdown** : Perfect for RAG pipelines or direct ingestion into LLMs. 2. **Structured Extraction** : Parse repeated patterns with CSS, XPath, or LLM-based extraction. 3. **Advanced Browser Control** : Hooks, proxies, stealth modes, session re-use—fine-grained control. 4. **High Performance** : Parallel crawling, chunk-based extraction, real-time use cases. 5. **Open Source** : No forced API keys, no paywalls—everyone can access their data. 
**Core Philosophies** : - **Democratize Data** : Free to use, transparent, and highly configurable. - **LLM Friendly** : Minimally processed, well-structured text, images, and metadata, so AI models can easily consume it.
## Documentation Structure
To help you get started, we’ve organized our docs into clear sections:
  * **Setup & Installation** Basic instructions to install Crawl4AI via pip or Docker. 
  * **Quick Start** A hands-on introduction showing how to do your first crawl, generate Markdown, and do a simple extraction. 
  * **Core** Deeper guides on single-page crawling, advanced browser/crawler parameters, content filtering, and caching. 
  * **Advanced** Explore link & media handling, lazy loading, hooking & authentication, proxies, session management, and more. 
  * **Extraction** Detailed references for no-LLM (CSS, XPath) vs. LLM-based strategies, chunking, and clustering approaches. 
  * **API Reference** Find the technical specifics of each class and method, including `AsyncWebCrawler`, `arun()`, and `CrawlResult`.


Throughout these sections, you’ll find code samples you can **copy-paste** into your environment. If something is missing or unclear, raise an issue or PR.
## How You Can Support
  * **Star & Fork**: If you find Crawl4AI helpful, star the repo on GitHub or fork it to add your own features. 
  * **File Issues** : Encounter a bug or missing feature? Let us know by filing an issue, so we can improve. 
  * **Pull Requests** : Whether it’s a small fix, a big feature, or better docs—contributions are always welcome. 
  * **Join Discord** : Come chat about web scraping, crawling tips, or AI workflows with the community. 
  * **Spread the Word** : Mention Crawl4AI in your blog posts, talks, or on social media. 


**Our mission** : to empower everyone—students, researchers, entrepreneurs, data scientists—to access, parse, and shape the world’s data with speed, cost-efficiency, and creative freedom.
## Quick Links
  * **[GitHub Repo](https://github.com/unclecode/crawl4ai)**
  * **[Installation Guide](https://docs.crawl4ai.com/core/installation/)**
  * **[Quick Start](https://docs.crawl4ai.com/core/quickstart/)**
  * **[API Reference](https://docs.crawl4ai.com/api/async-webcrawler/)**
  * **[Changelog](https://github.com/unclecode/crawl4ai/blob/main/CHANGELOG.md)**


Thank you for joining me on this journey. Let’s keep building an **open, democratic** approach to data extraction and AI together.
Happy Crawling! — _Unclecode, Founder & Maintainer of Crawl4AI_
Site built with [MkDocs](http://www.mkdocs.org) and [Terminal for MkDocs](https://github.com/ntno/mkdocs-terminal). 
#### On this page
  * [Quick Start](https://docs.crawl4ai.com/#quick-start)
  * [Video Tutorial](https://docs.crawl4ai.com/#video-tutorial)
  * [What Does Crawl4AI Do?](https://docs.crawl4ai.com/#what-does-crawl4ai-do)
  * [Documentation Structure](https://docs.crawl4ai.com/#documentation-structure)
  * [How You Can Support](https://docs.crawl4ai.com/#how-you-can-support)
  * [Quick Links](https://docs.crawl4ai.com/#quick-links)


##### Search
xClose
Type to start searching
[ Ask AI ](https://docs.crawl4ai.com/core/ask-ai/ "Ask Crawl4AI Assistant")
