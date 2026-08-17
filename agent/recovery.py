import os

from agent.state import AgentState


def recovery_node(state: AgentState):
    print("\n🛠 ORBIT Local Recovery started...")

    tool = state["selected_tool"]
    tool_input = state["tool_input"]
    tool_result = state["tool_result"]

    error_message = ""

    if tool_result:
        error_message = str(tool_result.get("error", "")).lower()

    # Recovery case:
    # move_file failed because destination folder does not exist
    if tool == "move_file":
        destination_path = tool_input["destination_path"]

        destination_folder = os.path.dirname(destination_path)

        if destination_folder and not os.path.exists(destination_folder):
            print("Missing destination folder detected.")

            os.makedirs(
                destination_folder,
                exist_ok=True
            )

            print(
                f"Created missing folder: "
                f"{destination_folder}"
            )

            return {
                "status": "local_recovery_success",
                "retry_count": 0
            }

    print("Local recovery could not solve the problem.")

    return {
        "status": "replan_required"
    }