"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient

class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        system_prompt = f"You are an expert technical writer. Write a response for the audience: {state.request.audience}. Synthesize the analysis notes into a clear, comprehensive final answer with citations."
        user_prompt = f"Query: {state.request.query}\nAnalysis Notes:\n{state.analysis_notes}"
        
        try:
            response = self.llm.complete(system_prompt, user_prompt)
            state.final_answer = response.content
        except Exception as e:
            state.final_answer = f"Writing failed: {e}"
            
        return state
