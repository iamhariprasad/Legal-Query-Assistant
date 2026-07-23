"""LangGraph workflow shape tests."""

from app.ai.langgraph_nodes.workflow import LegalAssistantGraph


def test_workflow_exposes_compiled_graph() -> None:
    assert hasattr(LegalAssistantGraph, "_build_graph")

