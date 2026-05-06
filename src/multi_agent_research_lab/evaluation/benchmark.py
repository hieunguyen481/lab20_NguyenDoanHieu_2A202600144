"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics, ResearchQuery
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]

def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a metric object."""
    started = perf_counter()
    try:
        state = runner(query)
        latency = perf_counter() - started
        
        # Simple heuristics for benchmark
        cost = 0.0001 * state.iteration # Mock cost
        quality_score = 8.5 if len(state.sources) > 0 and state.final_answer else 2.0
        
        metrics = BenchmarkMetrics(
            run_name=run_name, 
            latency_seconds=latency,
            estimated_cost_usd=cost,
            quality_score=quality_score,
            notes=f"Iterations: {state.iteration}. Sources: {len(state.sources)}. Errors: {len(state.errors)}"
        )
    except Exception as e:
        latency = perf_counter() - started
        state = ResearchState(request=ResearchQuery(query=query))
        metrics = BenchmarkMetrics(
            run_name=run_name,
            latency_seconds=latency,
            estimated_cost_usd=0.0,
            quality_score=0.0,
            notes=f"Failed with error: {str(e)}"
        )
        
    return state, metrics
