from agent.state import AgentState

from tools.file_tools import (
    list_files,
    read_file,
    create_folder,
    move_file,
    write_file,
    copy_file,
    search_files,
    delete_file,
    rename_file,
    rename_folder,
    delete_folder,
    organize_by_type,
)


def executor_node(state: AgentState):
    print("\n⚙️ ORBIT Executor started...")

    tool = state["selected_tool"]
    tool_input = state["tool_input"]

    try:
        # =========================================
        # LIST FILES
        # =========================================
        if tool == "list_files":

            if isinstance(tool_input, dict):
                folder_path = tool_input.get(
                    "folder_path"
                )
            else:
                folder_path = tool_input

            result = list_files(
                folder_path
            )

        # =========================================
        # READ FILE
        # =========================================
        elif tool == "read_file":

            if isinstance(tool_input, dict):
                file_path = tool_input.get(
                    "file_path"
                )
            else:
                file_path = tool_input

            result = read_file(
                file_path
            )

        # =========================================
        # CREATE FOLDER
        # =========================================
        elif tool == "create_folder":

            if isinstance(tool_input, dict):
                folder_path = tool_input.get(
                    "folder_path"
                )
            else:
                folder_path = tool_input

            result = create_folder(
                folder_path
            )

        # =========================================
        # MOVE FILE
        # =========================================
        elif tool == "move_file":

            result = move_file(
                tool_input["source_path"],
                tool_input["destination_path"]
            )

        # =========================================
        # WRITE FILE
        # =========================================
        elif tool == "write_file":

            result = write_file(
                tool_input["file_path"],
                tool_input["content"]
            )

        # =========================================
        # COPY FILE
        # =========================================
        elif tool == "copy_file":

            result = copy_file(
                tool_input["source_path"],
                tool_input["destination_path"]
            )

        # =========================================
        # SEARCH FILES
        # =========================================
        elif tool == "search_files":

            result = search_files(
                tool_input["folder_path"],
                tool_input["search_term"]
            )

        # =========================================
        # DELETE FILE
        # =========================================
        elif tool == "delete_file":

            result = delete_file(
                tool_input["file_path"]
            )

        # =========================================
        # RENAME FILE
        # =========================================
        elif tool == "rename_file":

            result = rename_file(
                tool_input["source_path"],
                tool_input["new_name"]
            )

        # =========================================
        # RENAME FOLDER
        # =========================================
        elif tool == "rename_folder":

            result = rename_folder(
                tool_input["source_path"],
                tool_input["new_name"]
            )

        # =========================================
        # DELETE FOLDER
        # =========================================
        elif tool == "delete_folder":

            result = delete_folder(
                tool_input["folder_path"]
            )

        # =========================================
        # ORGANIZE BY TYPE
        # =========================================
        elif tool == "organize_by_type":

            if isinstance(tool_input, dict):
                folder_path = tool_input.get(
                    "folder_path"
                )
            else:
                folder_path = tool_input

            result = organize_by_type(
                folder_path
            )

        # =========================================
        # UNKNOWN TOOL
        # =========================================
        else:
            result = {
                "success": False,
                "error": (
                    f"Unsupported tool: {tool}"
                )
            }

    except KeyError as error:
        result = {
            "success": False,
            "error": (
                f"Missing required tool input: "
                f"{error}"
            )
        }

    except Exception as error:
        result = {
            "success": False,
            "error": str(error)
        }

    # =========================================
    # SAVE EXECUTION HISTORY
    # =========================================
    history = state.get(
        "history",
        []
    )

    history.append({
        "action_number":
            state["current_action"] + 1,
        "tool":
            tool,
        "input":
            tool_input,
        "result":
            result
    })

    return {
        "tool_result":
            result,
        "history":
            history,
        "status":
            "executed"
    }