import json
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        
        if state.iteration >= 5:
            state.record_route("done")
            return state

        system_prompt = """You are a supervisor managing a research team.
        The team has:
        - researcher: Finds raw sources and extracts research notes.
        - analyst: Structures research notes into analysis notes.
        - writer: Synthesizes analysis notes into a final answer.
        
        Analyze the current state and choose the next worker: 'researcher', 'analyst', 'writer', or 'done'.
        If there are no research notes, call researcher.
        If there are research notes but no analysis notes, call analyst.
        If there are analysis notes but no final answer, call writer.
        If there is a final answer, return 'done'.
        
        Output ONLY a JSON object with a single key 'next_worker' whose value is the name of the worker.
        """

        user_prompt = f"""
        Query: {state.request.query}
        Iteration: {state.iteration}
        Research Notes Present: {bool(state.research_notes)}
        Analysis Notes Present: {bool(state.analysis_notes)}
        Final Answer Present: {bool(state.final_answer)}
        """

        try:
            response = self.llm.complete(system_prompt, user_prompt)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            data = json.loads(content)
            next_worker = data.get("next_worker", "done")
        except Exception as e:
            state.errors.append(f"Supervisor routing failed: {e}")
            next_worker = "done"

        state.record_route(next_worker)
        return state
