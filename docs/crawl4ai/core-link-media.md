# Link Media

[Crawl4AI Documentation (v0.6.x)](https://docs.crawl4ai.com/)
  * [ Home ](https://docs.crawl4ai.com/)
  * [ Ask AI ](https://docs.crawl4ai.com/core/ask-ai/)
  * [ Quick Start ](https://docs.crawl4ai.com/core/quickstart/)
  * [ Code Examples ](https://docs.crawl4ai.com/core/examples/)
  * [ Search ](https://docs.crawl4ai.com/core/link-media/)


×
  * [Home](https://docs.crawl4ai.com/)
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
    * Link & Media
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


  * [Link & Media](https://docs.crawl4ai.com/core/link-media/#link-media)
  * [Excluding External Images](https://docs.crawl4ai.com/core/link-media/#excluding-external-images)
  * [Excluding All Images](https://docs.crawl4ai.com/core/link-media/#excluding-all-images)
  * [1. Link Extraction](https://docs.crawl4ai.com/core/link-media/#1-link-extraction)
  * [2. Domain Filtering](https://docs.crawl4ai.com/core/link-media/#2-domain-filtering)
  * [3. Media Extraction](https://docs.crawl4ai.com/core/link-media/#3-media-extraction)
  * [4. Putting It All Together: Link & Media Filtering](https://docs.crawl4ai.com/core/link-media/#4-putting-it-all-together-link-media-filtering)
  * [5. Common Pitfalls & Tips](https://docs.crawl4ai.com/core/link-media/#5-common-pitfalls-tips)


# Link & Media
In this tutorial, you’ll learn how to:
  1. Extract links (internal, external) from crawled pages 
  2. Filter or exclude specific domains (e.g., social media or custom domains) 
  3. Access and ma### 3.2 Excluding Images


#### Excluding External Images
If you're dealing with heavy pages or want to skip third-party images (advertisements, for example), you can turn on:
```
crawler_cfg = CrawlerRunConfig(
  exclude_external_images=True
)
Copy
```

This setting attempts to discard images from outside the primary domain, keeping only those from the site you're crawling.
#### Excluding All Images
If you want to completely remove all images from the page to maximize performance and reduce memory usage, use:
```
crawler_cfg = CrawlerRunConfig(
  exclude_all_images=True
)
Copy
```

This setting removes all images very early in the processing pipeline, which significantly improves memory efficiency and processing speed. This is particularly useful when: - You don't need image data in your results - You're crawling image-heavy pages that cause memory issues - You want to focus only on text content - You need to maximize crawling speeddata (especially images) in the crawl result 4. Configure your crawler to exclude or prioritize certain images
> **Prerequisites** - You have completed or are familiar with the [AsyncWebCrawler Basics](https://docs.crawl4ai.com/core/simple-crawling/) tutorial. - You can run Crawl4AI in your environment (Playwright, Python, etc.).
Below is a revised version of the **Link Extraction** and **Media Extraction** sections that includes example data structures showing how links and media items are stored in `CrawlResult`. Feel free to adjust any field names or descriptions to match your actual output.
## 1. Link Extraction
### 1.1 `result.links`
When you call `arun()` or `arun_many()` on a URL, Crawl4AI automatically extracts links and stores them in the `links` field of `CrawlResult`. By default, the crawler tries to distinguish **internal** links (same domain) from **external** links (different domains).
**Basic Example** :
```
from crawl4ai import AsyncWebCrawler
async with AsyncWebCrawler() as crawler:
  result = await crawler.arun("https://www.example.com")
  if result.success:
    internal_links = result.links.get("internal", [])
    external_links = result.links.get("external", [])
    print(f"Found {len(internal_links)} internal links.")
    print(f"Found {len(internal_links)} external links.")
    print(f"Found {len(result.media)} media items.")
    # Each link is typically a dictionary with fields like:
    # { "href": "...", "text": "...", "title": "...", "base_domain": "..." }
    if internal_links:
      print("Sample Internal Link:", internal_links[0])
  else:
    print("Crawl failed:", result.error_message)
Copy
```

**Structure Example** :
```
result.links = {
 "internal": [
  {
   "href": "https://kidocode.com/",
   "text": "",
   "title": "",
   "base_domain": "kidocode.com"
  },
  {
   "href": "https://kidocode.com/degrees/technology",
   "text": "Technology Degree",
   "title": "KidoCode Tech Program",
   "base_domain": "kidocode.com"
  },
  # ...
 ],
 "external": [
  # possibly other links leading to third-party sites
 ]
}
Copy
```

  * **`href`**: The raw hyperlink URL.
  * **`text`**: The link text (if any) within the`<a>` tag. 
  * **`title`**: The`title` attribute of the link (if present). 
  * **`base_domain`**: The domain extracted from`href`. Helpful for filtering or grouping by domain.


## 2. Domain Filtering
Some websites contain hundreds of third-party or affiliate links. You can filter out certain domains at **crawl time** by configuring the crawler. The most relevant parameters in `CrawlerRunConfig` are:
  * **`exclude_external_links`**: If`True` , discard any link pointing outside the root domain. 
  * **`exclude_social_media_domains`**: Provide a list of social media platforms (e.g.,`["facebook.com", "twitter.com"]`) to exclude from your crawl. 
  * **`exclude_social_media_links`**: If`True` , automatically skip known social platforms. 
  * **`exclude_domains`**: Provide a list of custom domains you want to exclude (e.g.,`["spammyads.com", "tracker.net"]`).


### 2.1 Example: Excluding External & Social Media Links
```
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
async def main():
  crawler_cfg = CrawlerRunConfig(
    exclude_external_links=True,     # No links outside primary domain
    exclude_social_media_links=True    # Skip recognized social media domains
  )
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
      "https://www.example.com",
      config=crawler_cfg
    )
    if result.success:
      print("[OK] Crawled:", result.url)
      print("Internal links count:", len(result.links.get("internal", [])))
      print("External links count:", len(result.links.get("external", []))) 
      # Likely zero external links in this scenario
    else:
      print("[ERROR]", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())
Copy
```

### 2.2 Example: Excluding Specific Domains
If you want to let external links in, but specifically exclude a domain (e.g., `suspiciousads.com`), do this:
```
crawler_cfg = CrawlerRunConfig(
  exclude_domains=["suspiciousads.com"]
)
Copy
```

This approach is handy when you still want external links but need to block certain sites you consider spammy.
## 3. Media Extraction
### 3.1 Accessing `result.media`
By default, Crawl4AI collects images, audio, video URLs, and data tables it finds on the page. These are stored in `result.media`, a dictionary keyed by media type (e.g., `images`, `videos`, `audio`, `tables`).
**Basic Example** :
```
if result.success:
  # Get images
  images_info = result.media.get("images", [])
  print(f"Found {len(images_info)} images in total.")
  for i, img in enumerate(images_info[:3]): # Inspect just the first 3
    print(f"[Image {i}] URL: {img['src']}")
    print(f"      Alt text: {img.get('alt', '')}")
    print(f"      Score: {img.get('score')}")
    print(f"      Description: {img.get('desc', '')}\n")
  # Get tables
  tables = result.media.get("tables", [])
  print(f"Found {len(tables)} data tables in total.")
  for i, table in enumerate(tables):
    print(f"[Table {i}] Caption: {table.get('caption', 'No caption')}")
    print(f"      Columns: {len(table.get('headers', []))}")
    print(f"      Rows: {len(table.get('rows', []))}")
Copy
```

**Structure Example** :
```
result.media = {
 "images": [
  {
   "src": "https://cdn.prod.website-files.com/.../Group%2089.svg",
   "alt": "coding school for kids",
   "desc": "Trial Class Degrees degrees All Degrees AI Degree Technology ...",
   "score": 3,
   "type": "image",
   "group_id": 0,
   "format": None,
   "width": None,
   "height": None
  },
  # ...
 ],
 "videos": [
  # Similar structure but with video-specific fields
 ],
 "audio": [
  # Similar structure but with audio-specific fields
 ],
 "tables": [
  {
   "headers": ["Name", "Age", "Location"],
   "rows": [
    ["John Doe", "34", "New York"],
    ["Jane Smith", "28", "San Francisco"],
    ["Alex Johnson", "42", "Chicago"]
   ],
   "caption": "Employee Directory",
   "summary": "Directory of company employees"
  },
  # More tables if present
 ]
}
Copy
```

Depending on your Crawl4AI version or scraping strategy, these dictionaries can include fields like:
  * **`src`**: The media URL (e.g., image source)
  * **`alt`**: The alt text for images (if present)
  * **`desc`**: A snippet of nearby text or a short description (optional)
  * **`score`**: A heuristic relevance score if you’re using content-scoring features
  * **`width`**,**`height`**: If the crawler detects dimensions for the image/video
  * **`type`**: Usually`"image"` , `"video"`, or `"audio"`
  * **`group_id`**: If you’re grouping related media items, the crawler might assign an ID


With these details, you can easily filter out or focus on certain images (for instance, ignoring images with very low scores or a different domain), or gather metadata for analytics.
### 3.2 Excluding External Images
If you’re dealing with heavy pages or want to skip third-party images (advertisements, for example), you can turn on:
```
crawler_cfg = CrawlerRunConfig(
  exclude_external_images=True
)
Copy
```

This setting attempts to discard images from outside the primary domain, keeping only those from the site you’re crawling.
### 3.3 Working with Tables
Crawl4AI can detect and extract structured data from HTML tables. Tables are analyzed based on various criteria to determine if they are actual data tables (as opposed to layout tables), including:
  * Presence of thead and tbody sections
  * Use of th elements for headers
  * Column consistency
  * Text density
  * And other factors


Tables that score above the threshold (default: 7) are extracted and stored in `result.media.tables`.
**Accessing Table Data** :
```
if result.success:
  tables = result.media.get("tables", [])
  print(f"Found {len(tables)} data tables on the page")
  if tables:
    # Access the first table
    first_table = tables[0]
    print(f"Table caption: {first_table.get('caption', 'No caption')}")
    print(f"Headers: {first_table.get('headers', [])}")
    # Print the first 3 rows
    for i, row in enumerate(first_table.get('rows', [])[:3]):
      print(f"Row {i+1}: {row}")
Copy
```

**Configuring Table Extraction** :
You can adjust the sensitivity of the table detection algorithm with:
```
crawler_cfg = CrawlerRunConfig(
  table_score_threshold=5 # Lower value = more tables detected (default: 7)
)
Copy
```

Each extracted table contains: - `headers`: Column header names - `rows`: List of rows, each containing cell values - `caption`: Table caption text (if available) - `summary`: Table summary attribute (if specified)
### 3.4 Additional Media Config
  * **`screenshot`**: Set to`True` if you want a full-page screenshot stored as `base64` in `result.screenshot`. 
  * **`pdf`**: Set to`True` if you want a PDF version of the page in `result.pdf`. 
  * **`capture_mhtml`**: Set to`True` if you want an MHTML snapshot of the page in `result.mhtml`. This format preserves the entire web page with all its resources (CSS, images, scripts) in a single file, making it perfect for archiving or offline viewing.
  * **`wait_for_images`**: If`True` , attempts to wait until images are fully loaded before final extraction.


#### Example: Capturing Page as MHTML
```
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
async def main():
  crawler_cfg = CrawlerRunConfig(
    capture_mhtml=True # Enable MHTML capture
  )
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://example.com", config=crawler_cfg)
    if result.success and result.mhtml:
      # Save the MHTML snapshot to a file
      with open("example.mhtml", "w", encoding="utf-8") as f:
        f.write(result.mhtml)
      print("MHTML snapshot saved to example.mhtml")
    else:
      print("Failed to capture MHTML:", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())
Copy
```

The MHTML format is particularly useful because: - It captures the complete page state including all resources - It can be opened in most modern browsers for offline viewing - It preserves the page exactly as it appeared during crawling - It's a single file, making it easy to store and transfer
## 4. Putting It All Together: Link & Media Filtering
Here’s a combined example demonstrating how to filter out external links, skip certain domains, and exclude external images:
```
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
async def main():
  # Suppose we want to keep only internal links, remove certain domains, 
  # and discard external images from the final crawl data.
  crawler_cfg = CrawlerRunConfig(
    exclude_external_links=True,
    exclude_domains=["spammyads.com"],
    exclude_social_media_links=True,  # skip Twitter, Facebook, etc.
    exclude_external_images=True,   # keep only images from main domain
    wait_for_images=True,       # ensure images are loaded
    verbose=True
  )
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://www.example.com", config=crawler_cfg)
    if result.success:
      print("[OK] Crawled:", result.url)
      # 1. Links
      in_links = result.links.get("internal", [])
      ext_links = result.links.get("external", [])
      print("Internal link count:", len(in_links))
      print("External link count:", len(ext_links)) # should be zero with exclude_external_links=True
      # 2. Images
      images = result.media.get("images", [])
      print("Images found:", len(images))
      # Let's see a snippet of these images
      for i, img in enumerate(images[:3]):
        print(f" - {img['src']} (alt={img.get('alt','')}, score={img.get('score','N/A')})")
    else:
      print("[ERROR] Failed to crawl. Reason:", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())
Copy
```

## 5. Common Pitfalls & Tips
1. **Conflicting Flags** : - `exclude_external_links=True` but then also specifying `exclude_social_media_links=True` is typically fine, but understand that the first setting already discards _all_ external links. The second becomes somewhat redundant. - `exclude_external_images=True` but want to keep some external images? Currently no partial domain-based setting for images, so you might need a custom approach or hook logic.
2. **Relevancy Scores** : - If your version of Crawl4AI or your scraping strategy includes an `img["score"]`, it’s typically a heuristic based on size, position, or content analysis. Evaluate carefully if you rely on it.
3. **Performance** : - Excluding certain domains or external images can speed up your crawl, especially for large, media-heavy pages. - If you want a “full” link map, do _not_ exclude them. Instead, you can post-filter in your own code.
4. **Social Media Lists** : - `exclude_social_media_links=True` typically references an internal list of known social domains like Facebook, Twitter, LinkedIn, etc. If you need to add or remove from that list, look for library settings or a local config file (depending on your version).
**That’s it for Link & Media Analysis!** You’re now equipped to filter out unwanted sites and zero in on the images and videos that matter for your project.
### Table Extraction Tips
  * Not all HTML tables are extracted - only those detected as "data tables" vs. layout tables.
  * Tables with inconsistent cell counts, nested tables, or those used purely for layout may be skipped.
  * If you're missing tables, try adjusting the `table_score_threshold` to a lower value (default is 7).


The table detection algorithm scores tables based on features like consistent columns, presence of headers, text density, and more. Tables scoring above the threshold are considered data tables worth extracting.
Site built with [MkDocs](http://www.mkdocs.org) and [Terminal for MkDocs](https://github.com/ntno/mkdocs-terminal). 
#### On this page
  * [Excluding External Images](https://docs.crawl4ai.com/core/link-media/#excluding-external-images)
  * [Excluding All Images](https://docs.crawl4ai.com/core/link-media/#excluding-all-images)
  * [1. Link Extraction](https://docs.crawl4ai.com/core/link-media/#1-link-extraction)
  * [1.1 result.links](https://docs.crawl4ai.com/core/link-media/#11-resultlinks)
  * [2. Domain Filtering](https://docs.crawl4ai.com/core/link-media/#2-domain-filtering)
  * [2.1 Example: Excluding External & Social Media Links](https://docs.crawl4ai.com/core/link-media/#21-example-excluding-external-social-media-links)
  * [2.2 Example: Excluding Specific Domains](https://docs.crawl4ai.com/core/link-media/#22-example-excluding-specific-domains)
  * [3. Media Extraction](https://docs.crawl4ai.com/core/link-media/#3-media-extraction)
  * [3.1 Accessing result.media](https://docs.crawl4ai.com/core/link-media/#31-accessing-resultmedia)
  * [3.2 Excluding External Images](https://docs.crawl4ai.com/core/link-media/#32-excluding-external-images)
  * [3.3 Working with Tables](https://docs.crawl4ai.com/core/link-media/#33-working-with-tables)
  * [3.4 Additional Media Config](https://docs.crawl4ai.com/core/link-media/#34-additional-media-config)
  * [Example: Capturing Page as MHTML](https://docs.crawl4ai.com/core/link-media/#example-capturing-page-as-mhtml)
  * [4. Putting It All Together: Link & Media Filtering](https://docs.crawl4ai.com/core/link-media/#4-putting-it-all-together-link-media-filtering)
  * [5. Common Pitfalls & Tips](https://docs.crawl4ai.com/core/link-media/#5-common-pitfalls-tips)
  * [Table Extraction Tips](https://docs.crawl4ai.com/core/link-media/#table-extraction-tips)


##### Search
xClose
Type to start searching
[ Ask AI ](https://docs.crawl4ai.com/core/ask-ai/ "Ask Crawl4AI Assistant")
