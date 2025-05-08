# To Do

1. Optimize prompt engineering for Crew agent + task yaml files
2. Improve search workflow
   1. Create an initial set of search terms from the starting article outline using frontier model (Gemini 2.5 Pro).
   2. Search queries with Google Scholar and get results.
   3. [OPTIONAL] Potentially add suggested related search terms to set and continue exploration.
   4. Scrape webpages, get markdown, parse and distill with LLM (Gemini Flash).
   5. [OPTIONAL] Download PDFs, save with informative names, parse with Marker. 
   6. Synthesize results, extract only most useful information for the topic at hand
   7. Ensure proper citation. Build pydantic class for paper metadata, PDF URL, authors, etc. 
   8. 