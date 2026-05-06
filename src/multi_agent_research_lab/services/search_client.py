"""Search client abstraction for ResearcherAgent."""

import json
import requests
from multi_agent_research_lab.core.schemas import SourceDocument
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.config import get_settings

class SearchClient:
    """Provider-agnostic search client skeleton."""

    def __init__(self):
        self.llm = LLMClient()
        self.tavily_api_key = get_settings().tavily_api_key

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        if self.tavily_api_key:
            return self._tavily_search(query, max_results)
        return self._mock_search(query, max_results)

    def _tavily_search(self, query: str, max_results: int) -> list[SourceDocument]:
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": False,
                    "max_results": max_results,
                },
                timeout=15,
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            docs = []
            for item in results:
                docs.append(SourceDocument(
                    title=item.get("title", "No Title"),
                    url=item.get("url", "https://example.com"),
                    snippet=item.get("content", "No snippet")
                ))
            return docs
        except Exception as e:
            # Fallback on failure
            return self._mock_search(query, max_results)

    def _mock_search(self, query: str, max_results: int) -> list[SourceDocument]:
        system_prompt = f"You are a mock search engine. Generate {max_results} JSON search results for the query. Output ONLY a JSON array of objects with keys 'title', 'url' and 'snippet'."
        user_prompt = f"Query: {query}"
        
        try:
            response = self.llm.complete(system_prompt, user_prompt)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            data = json.loads(content)
            
            docs = []
            for item in data:
                docs.append(SourceDocument(
                    title=item.get("title", "No Title"),
                    url=item.get("url", "https://example.com"),
                    snippet=item.get("snippet", "No snippet")
                ))
            return docs
        except Exception:
            return [SourceDocument(title="Mock result", url="https://example.com", snippet=f"Mocked search result for '{query}'")]

