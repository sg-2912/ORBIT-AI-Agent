from agent.state import AgentState


MAX_RETRIES = 3


def verifier_node(state: AgentState):
    print("\n✅ ORBIT Verifier started...")

    result = state.get("tool_result")
    retry_count = state.get("retry_count", 0)
    current_action = state.get("current_action", 0)
    actions = state.get("actions", [])

    # =================================================
    # SUCCESS
    # =================================================

    if result and result.get("success") is True:
        print("Verification successful.")

        next_action = current_action + 1

        if next_action >= len(actions):
            return {
                "status": "completed",
                "current_action": next_action,
                "retry_count": 0
            }

        return {
            "status": "next_action",
            "current_action": next_action,
            "retry_count": 0
        }

    # =================================================
    # EXTRACT ERROR
    # =================================================

    error_message = ""

    if result:
        error_message = str(
            result.get("error", "")
        ).lower()

    print(
        f"Verification failed: {error_message}"
    )

    # =================================================
    # NON-RETRYABLE FILE SYSTEM ERRORS
    # =================================================

    if (
        "does not exist" in error_message
        or "no such file" in error_message
        or "cannot find" in error_message
        or "not found" in error_message
    ):
        print("File or folder not found.")

        return {
            "status": "resource_not_found",
            "retry_count": 0
        }

    if (
        "already exists" in error_message
        or "destination exists" in error_message
    ):
        print("Destination already exists.")

        return {
            "status": "destination_exists",
            "retry_count": 0
        }

    if (
        "permission denied" in error_message
        or "access is denied" in error_message
        or "protected" in error_message
    ):
        print("Permission error detected.")

        return {
            "status": "permission_denied",
            "retry_count": 0
        }

    if (
        "not a file" in error_message
        or "not a folder" in error_message
        or "not a directory" in error_message
        or "invalid path" in error_message
    ):
        print("Invalid path type detected.")

        return {
            "status": "invalid_path",
            "retry_count": 0
        }

    if (
        "missing required tool input" in error_message
    ):
        print("Tool input is incomplete.")

        return {
            "status": "invalid_tool_input",
            "retry_count": 0
        }

    if (
        "unsupported tool" in error_message
    ):
        print("Unsupported tool selected.")

        return {
            "status": "unsupported_tool",
            "retry_count": 0
        }

    # =================================================
    # RETRYABLE / UNKNOWN FAILURE
    # =================================================

    retry_count += 1

    print(
        f"Retryable failure detected. "
        f"Retry {retry_count}/{MAX_RETRIES}"
    )

    if retry_count >= MAX_RETRIES:
        return {
            "status": "max_retries_reached",
            "retry_count": retry_count
        }

    return {
        "status": "retry",
        "retry_count": retry_count
    }