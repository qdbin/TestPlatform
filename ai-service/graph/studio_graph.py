from typing import TypedDict, List, Dict, Any
import os

import requests

from langgraph.graph import StateGraph, START, END


class StudioState(TypedDict, total=False):
    project_id: str
    query: str
    top_k: int
    status: str
    results: List[Dict[str, Any]]


def run_rag_search(state: StudioState) -> StudioState:
    project_id = str(state.get("project_id") or "")
    query = str(state.get("query") or "")
    top_k = int(state.get("top_k") or 5)
    token = os.getenv("STUDIO_TOKEN", "")
    headers = {"token": token} if token else {}
    base_url = os.getenv("STUDIO_AI_BASE_URL", "http://127.0.0.1:8001")
    response = requests.post(
        f"{base_url}/ai/rag/query",
        json={"project_id": project_id, "query": query, "top_k": top_k},
        headers=headers,
        timeout=90,
    )
    result = response.json() if response.ok else {"status": "error", "data": []}
    return {
        "status": str(result.get("status") or "error"),
        "results": result.get("data") or [],
    }


builder = StateGraph(StudioState)
builder.add_node("run_rag_search", run_rag_search)
builder.add_edge(START, "run_rag_search")
builder.add_edge("run_rag_search", END)
graph = builder.compile()
