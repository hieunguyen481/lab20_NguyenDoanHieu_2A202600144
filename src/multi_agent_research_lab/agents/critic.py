"""Critic Agent responsible for evaluating the writer's output."""

import json

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

class CriticAgent(BaseAgent):
    name = "critic"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        if not state.final_answer:
            return state

        system_prompt = """You are a strict Critic. Your job is to evaluate the final answer written by the Writer.
        Check if the final answer:
        1. Directly answers the query.
        2. Is well-written and flows logically.
        3. Cites its sources appropriately.

        Output ONLY a JSON object with two keys:
        - 'pass': boolean (true if it meets all criteria, false otherwise).
        - 'feedback': string (if pass is false, provide specific actionable feedback for the writer. If true, leave empty).
        """

        user_prompt = f"""
        Query: {state.request.query}
        Analysis Notes (Ground Truth): {state.analysis_notes}
        Final Answer to Evaluate: {state.final_answer}
        """

        try:
            response = self.llm.complete(system_prompt, user_prompt)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            data = json.loads(content)
            
            passed = data.get("pass", True)
            feedback = data.get("feedback", "")
            
            if not passed:
                # Append feedback to analysis notes so writer sees it
                state.analysis_notes += f"\n\n[CRITIC FEEDBACK]: {feedback}\nPlease rewrite the final answer addressing this feedback."
                # Clear final answer to force writer to run again
                state.final_answer = None

            # If passed, we leave final_answer intact
        except Exception as e:
            state.errors.append(f"Critic evaluation failed: {e}")

        return state
