from agent.state import AgentState


def tool_selector_node(state: AgentState):
    print("\n🔧 ORBIT Tool Selector started...")

    actions = state["actions"]
    current_action = state["current_action"]

    if current_action >= len(actions):
        return {
            "selected_tool": None,
            "tool_input": None,
            "status": "no_more_actions"
        }

    action = actions[current_action]

    selected_tool = action["tool"]
    tool_input = action["input"]

    print("Selected tool:", selected_tool)
    print(
        f"Action {current_action + 1} of {len(actions)}"
    )

    return {
        "selected_tool": selected_tool,
        "tool_input": tool_input,
        "status": "tool_selected"
    }