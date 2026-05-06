"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient

class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        system_prompt = "You are a research analyst. Extract key claims, compare viewpoints, and structure the research notes. Output clear, concise analysis notes."
        user_prompt = f"Query: {state.request.query}\nResearch Notes:\n{state.research_notes}"
        
        try:
            response = self.llm.complete(system_prompt, user_prompt)
            state.analysis_notes = response.content
        except Exception as e:
            state.analysis_notes = f"Analysis failed: {e}"
            
        return state
