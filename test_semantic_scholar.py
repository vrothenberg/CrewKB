"""
Test script for the Semantic Scholar tool.
"""

import asyncio
import logging
from crewkb.tools.search.semantic_scholar_tool import SemanticScholarTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_semantic_scholar():
    """Test the Semantic Scholar tool with authentication fallback."""
    print("Testing Semantic Scholar Tool...")
    
    # Create a tool instance
    tool = SemanticScholarTool()
    
    # Test with a simple query
    query = "machine learning healthcare"
    max_results = 5
    min_citation_count = 100
    
    print(f"Searching for: {query}")
    print(f"Parameters: max_results={max_results}, min_citation_count={min_citation_count}")
    
    try:
        # Step 1: Search for papers
        print("\n--- Step 1: Searching for papers ---")
        search_results = await tool._search_papers(query, max_results * 2)
        print(f"Search results type: {type(search_results)}")
        if search_results:
            print(f"Found {len(search_results.get('data', []))} papers in search results")
            # Print first result as example
            if search_results.get('data'):
                print("Example paper from search results:")
                print(search_results['data'][0])
        else:
            print("No search results found")
        
        # Extract paper IDs
        paper_ids = [paper.get("paperId") for paper in search_results.get("data", [])]
        print(f"Extracted {len(paper_ids)} paper IDs")
        
        # Step 2: Get detailed paper information
        print("\n--- Step 2: Getting detailed paper information ---")
        papers = await tool._get_paper_details(paper_ids, query)
        print(f"Got details for {len(papers) if papers else 0} papers")
        if papers:
            print("Example paper details:")
            print(papers[0])
        
        # Step 3: Filter papers
        print("\n--- Step 3: Filtering papers ---")
        filtered_papers = tool._filter_papers(papers, min_citation_count, 1.0)
        print(f"After filtering: {len(filtered_papers) if filtered_papers else 0} papers")
        if filtered_papers:
            print("Example filtered paper:")
            print(filtered_papers[0])
        
        # Step 4: Sort papers
        print("\n--- Step 4: Sorting papers ---")
        sorted_papers = tool._sort_papers(filtered_papers, "relevance")
        print(f"After sorting: {len(sorted_papers) if sorted_papers else 0} papers")
        
        # Step 5: Format results
        print("\n--- Step 5: Formatting results ---")
        formatted_results = tool._format_results(sorted_papers[:max_results], query)
        
        # Print the final results
        print("\nFinal Results:")
        print(formatted_results)
        
        return formatted_results
    except Exception as e:
        import traceback
        print(f"Error during testing: {str(e)}")
        print(traceback.format_exc())
        return f"Error performing Semantic Scholar search: {str(e)}"

if __name__ == "__main__":
    asyncio.run(test_semantic_scholar())
