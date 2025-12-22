"""
Web Search Tool Example

This is a simple example of a web search tool.
In production, you would integrate with a real search API like Serper or Google.
"""

import random
from typing import List, Dict


class WebSearchTool:
    """Simple web search tool for demonstration"""
    
    name = "web_search"
    description = "Search the web for information on any topic"
    
    def __init__(self):
        # In production, initialize with API keys
        pass
    
    def run(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform a web search
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        # This is a mock implementation
        # In production, use a real search API
        
        mock_results = [
            {
                "title": f"Understanding {query}",
                "url": f"https://example.com/{query.replace(' ', '-')}-guide",
                "snippet": f"A comprehensive guide to {query}. Learn everything you need to know about this topic..."
            },
            {
                "title": f"{query} - Wikipedia",
                "url": f"https://wikipedia.org/wiki/{query.replace(' ', '_')}",
                "snippet": f"{query} is an important concept in modern technology and science..."
            },
            {
                "title": f"Latest developments in {query}",
                "url": f"https://techblog.com/{query.replace(' ', '-')}-2025",
                "snippet": f"Recent breakthroughs and innovations in the field of {query}..."
            },
            {
                "title": f"{query} best practices",
                "url": f"https://bestpractices.io/{query.replace(' ', '-')}",
                "snippet": f"Industry standards and best practices for implementing {query}..."
            },
            {
                "title": f"The future of {query}",
                "url": f"https://futurism.com/{query.replace(' ', '-')}-predictions",
                "snippet": f"Expert predictions on how {query} will evolve in the coming years..."
            }
        ]
        
        # Return requested number of results
        return mock_results[:num_results]
    
    def __call__(self, query: str) -> str:
        """Make the tool callable for CrewAI compatibility"""
        results = self.run(query)
        
        # Format results as a string
        formatted = f"Search results for '{query}':\\n\\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\\n"
            formatted += f"   URL: {result['url']}\\n"
            formatted += f"   {result['snippet']}\\n\\n"
        
        return formatted