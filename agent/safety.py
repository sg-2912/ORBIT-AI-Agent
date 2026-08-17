from agent.state import AgentState


DESTRUCTIVE_TOOLS = {
    "delete_file",
    "delete_folder"
}


def safety_node(state: AgentState):
    print("\n🛡 ORBIT Safety Check started...")

    tool = state["selected_tool"]

    if tool in DESTRUCTIVE_TOOLS:

        if state.get(
            "confirmation_granted",
            False
        ):
            print(
                "Confirmation already granted."
            )

            return {
                "requires_confirmation": False,
                "status": "safe_to_execute"
            }

        print(
            f"User confirmation required for {tool}."
        )

        return {
            "requires_confirmation": True,
            "status": "confirmation_required"
        }

    return {
        "requires_confirmation": False,
        "status": "safe_to_execute"
    }