"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


import json
from multi_agent_research_lab.core.schemas import SourceDocument
from multi_agent_research_lab.services.llm_client import LLMClient

class SearchClient:
    """Provider-agnostic search client skeleton."""

    def __init__(self):
        self.llm = LLMClient()

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
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

