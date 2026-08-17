from langgraph.graph import StateGraph, START, END

from agent.state import AgentState
from agent.planner import planner_node
from agent.tool_selector import tool_selector_node
from agent.executor import executor_node
from agent.verifier import verifier_node
from agent.replanner import replanner_node
from agent.recovery import recovery_node
from agent.safety import safety_node


def decide_after_planner(state: AgentState):

    if state["status"] in {
        "llm_quota_exceeded",
        "llm_service_unavailable",
        "llm_error",
        "planner_error"
    }:
        return "end"

    if not state["actions"]:
        return "end"

    return "continue"


def decide_next_step(state: AgentState):

    terminal_statuses = {
        "completed",
        "resource_not_found",
        "destination_exists",
        "permission_denied",
        "invalid_path",
        "invalid_tool_input",
        "unsupported_tool"
    }

    if state["status"] in terminal_statuses:
        return "end"

    if state["status"] == "max_retries_reached":
        return "recovery"

    if state["status"] == "next_action":
        return "next_action"

    return "retry"


def decide_after_recovery(state: AgentState):
    if state["status"] == "local_recovery_success":
        return "retry"

    return "replan"


def decide_after_replanner(state: AgentState):
    if state["status"] == "llm_quota_exceeded":
        return "end"

    return "continue"


def decide_after_safety(state: AgentState):
    if state["status"] == "confirmation_required":
        return "end"

    return "execute"


def create_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("tool_selector", tool_selector_node)
    workflow.add_node("safety", safety_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("recovery", recovery_node)
    workflow.add_node("replanner", replanner_node)

    workflow.add_edge(
        START,
        "planner"
    )

    workflow.add_conditional_edges(
        "planner",
        decide_after_planner,
        {
            "continue": "tool_selector",
            "end": END
        }
    )

    workflow.add_edge(
        "tool_selector",
        "safety"
    )

    workflow.add_conditional_edges(
        "safety",
        decide_after_safety,
        {
            "execute": "executor",
            "end": END
        }
    )

    workflow.add_edge(
        "executor",
        "verifier"
    )

    workflow.add_conditional_edges(
        "verifier",
        decide_next_step,
        {
            "end": END,
            "next_action": "tool_selector",
            "retry": "executor",
            "recovery": "recovery"
        }
    )

    workflow.add_conditional_edges(
        "recovery",
        decide_after_recovery,
        {
            "retry": "executor",
            "replan": "replanner"
        }
    )

    workflow.add_conditional_edges(
        "replanner",
        decide_after_replanner,
        {
            "continue": "tool_selector",
            "end": END
        }
    )

    return workflow.compile()


def create_confirmation_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("safety", safety_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("verifier", verifier_node)

    workflow.add_edge(
        START,
        "safety"
    )

    workflow.add_conditional_edges(
        "safety",
        decide_after_safety,
        {
            "execute": "executor",
            "end": END
        }
    )

    workflow.add_edge(
        "executor",
        "verifier"
    )

    workflow.add_conditional_edges(
        "verifier",
        decide_next_step,
        {
            "end": END,
            "next_action": END,
            "retry": "executor",
            "recovery": END
        }
    )

    return workflow.compile()