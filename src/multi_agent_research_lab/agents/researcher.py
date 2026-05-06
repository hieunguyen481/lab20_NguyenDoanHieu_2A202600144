"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.search_client import SearchClient

class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self):
        self.search_client = SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        sources = self.search_client.search(state.request.query, max_results=state.request.max_sources)
        state.sources.extend(sources)
        
        notes = "Research Notes:\n"
        for i, src in enumerate(sources):
            notes += f"[{i+1}] {src.title} ({src.url})\nSnippet: {src.snippet}\n\n"
            
        state.research_notes = notes
        return state
