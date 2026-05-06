import os
import sys

from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.services.llm_client import LLMClient

def run_baseline(query: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=query))
    client = LLMClient()
    response = client.complete(
        "You are a helpful research assistant. Provide a detailed summary.", 
        f"Research Query: {query}"
    )
    state.final_answer = response.content
    state.iteration = 1
    return state

def run_multi_agent(query: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    result = workflow.run(state)
    return result

def main():
    query = "Tìm hiểu về kiến trúc GraphRAG và viết tóm tắt 200 chữ"
    print(f"Running benchmark for query: '{query}'\n")

    print("1. Running Single-Agent Baseline...")
    _, baseline_metrics = run_benchmark("Single-Agent Baseline", query, run_baseline)
    
    print("2. Running Multi-Agent Workflow...")
    _, multi_agent_metrics = run_benchmark("Multi-Agent Workflow", query, run_multi_agent)

    print("\nGenerating report...")
    report_md = render_markdown_report([baseline_metrics, multi_agent_metrics])
    
    report_md += """

## LangSmith Trace Screenshot

![LangSmith Trace](trace.png)

## Failure Mode & How to Fix

**Failure mode:** Hệ thống bị kẹt trong một vòng lặp vô tận (infinite loop) khi `Analyst` liên tục cho rằng `research_notes` chưa đủ chất lượng và yêu cầu `Supervisor` trả ngược lại cho `Researcher` đi tìm kiếm lại, nhưng dữ liệu tìm kiếm trả về không thay đổi. Điều này khiến cả 3 Agents cứ chuyền tay nhau liên tục làm tốn chi phí API và không bao giờ ra được kết quả cuối cùng.

**Cách fix:** Thiết lập giới hạn số vòng lặp tối đa (guardrail `max_iterations`). Khi đạt đến `state.iteration >= 5`, `Supervisor` sẽ có cơ chế bắt buộc phải chuyển hướng (route) sang trạng thái `done` hoặc `writer` để kết thúc chương trình. Đoạn code này đã được implement tại logic của `SupervisorAgent`.
"""
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)
    
    print("Report saved to reports/benchmark_report.md")

if __name__ == "__main__":
    main()
