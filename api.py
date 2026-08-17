from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, List

from memory.memory_manager import (
    load_memory,
    get_memory_summary
)

from agent.graph import (
    create_agent_graph,
    create_confirmation_graph
)


app = FastAPI(
    title="ORBIT AI Agent API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://orbit-ai-agent.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


agent = create_agent_graph()
confirmation_agent = create_confirmation_graph()


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class AgentRequest(BaseModel):
    task: str


class AgentResponse(BaseModel):
    task: str
    status: str
    message: str
    plan: List[str]
    history: List[dict]
    tool_result: Any
    requires_confirmation: bool
    selected_tool: str | None
    tool_input: Any


class ConfirmRequest(BaseModel):
    task: str
    selected_tool: str
    tool_input: Any


# ============================================================
# USER-FRIENDLY RESPONSE BUILDER
# ============================================================

def build_user_message(
    status: str,
    history: list,
    tool_result: Any = None
):
    if status == "completed":

        action_count = len(history)

        if action_count == 0:
            return "Task completed successfully."

        if action_count == 1:
            tool = history[0].get(
                "tool",
                "action"
            )

            return (
                f"Task completed successfully. "
                f"ORBIT executed {tool}."
            )

        return (
            f"Task completed successfully. "
            f"ORBIT executed {action_count} actions."
        )

    if status == "confirmation_required":
        return (
            "This action requires your confirmation "
            "before ORBIT can continue."
        )

    if status == "cancelled":
        return (
            "The action was cancelled. "
            "No destructive operation was performed."
        )

    if status == "resource_not_found":

        path = None

        if isinstance(
            tool_result,
            dict
        ):
            path = (
                tool_result.get("file")
                or tool_result.get("folder")
                or tool_result.get("source")
            )

        if path:
            return (
                f"ORBIT could not find the requested "
                f"file or folder: {path}"
            )

        return (
            "ORBIT could not find the requested "
            "file or folder."
        )

    if status == "destination_exists":
        return (
            "ORBIT could not complete the action "
            "because the destination already exists."
        )

    if status == "permission_denied":
        return (
            "ORBIT does not have permission to "
            "perform this action."
        )

    if status == "invalid_path":
        return (
            "The provided path is not valid for "
            "this operation."
        )

    if status == "invalid_tool_input":
        return (
            "ORBIT received incomplete information "
            "for the selected tool."
        )

    if status == "unsupported_tool":
        return (
            "ORBIT selected a tool that is not "
            "currently supported."
        )

    if status == "llm_quota_exceeded":
        return (
            "The AI planning service has reached "
            "its current quota. Simple local tasks "
            "may still work."
        )

    if status == "llm_service_unavailable":
        return (
            "The AI planning service is temporarily "
            "unavailable. Please try again shortly."
        )

    if status == "planner_error":
        return (
            "ORBIT could not create a valid plan "
            "for this task."
        )

    if status == "llm_error":
        return (
            "The AI planning service returned an error."
        )

    if status == "max_retries_reached":
        return (
            "ORBIT could not complete the action "
            "after several attempts."
        )

    return (
        f"ORBIT finished with status: {status}"
    )


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "ORBIT AI Agent API is running"
    }


# ============================================================
# RUN AGENT
# ============================================================

@app.post(
    "/agent/run",
    response_model=AgentResponse
)
def run_agent(request: AgentRequest):

    if not request.task.strip():
        raise HTTPException(
            status_code=400,
            detail="Task cannot be empty."
        )

    initial_state = {
        "task": request.task,
        "plan": [],
        "actions": [],
        "current_action": 0,
        "current_step": 0,
        "status": "started",
        "selected_tool": None,
        "tool_input": None,
        "tool_result": None,
        "retry_count": 0,
        "history": [],
        "requires_confirmation": False,
        "confirmation_granted": False
    }

    try:
        result = agent.invoke(
            initial_state
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    status = result.get(
        "status",
        "unknown"
    )

    history = result.get(
        "history",
        []
    )

    tool_result = result.get(
        "tool_result"
    )

    message = build_user_message(
        status,
        history,
        tool_result
    )

    return AgentResponse(
        task=request.task,
        status=status,
        message=message,
        plan=result.get(
            "plan",
            []
        ),
        history=history,
        tool_result=tool_result,
        requires_confirmation=result.get(
            "requires_confirmation",
            False
        ),
        selected_tool=result.get(
            "selected_tool"
        ),
        tool_input=result.get(
            "tool_input"
        )
    )


# ============================================================
# CONFIRM DESTRUCTIVE ACTION
# ============================================================

@app.post("/agent/confirm")
def confirm_action(
    request: ConfirmRequest
):

    allowed_destructive_tools = {
        "delete_file",
        "delete_folder"
    }

    if (
        request.selected_tool
        not in allowed_destructive_tools
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Only destructive actions "
                "requiring confirmation are supported."
            )
        )

    initial_state = {
        "task": request.task,
        "plan": [],
        "actions": [
            {
                "tool":
                    request.selected_tool,
                "input":
                    request.tool_input
            }
        ],
        "current_action": 0,
        "current_step": 0,
        "status": "started",
        "selected_tool":
            request.selected_tool,
        "tool_input":
            request.tool_input,
        "tool_result": None,
        "retry_count": 0,
        "history": [],
        "requires_confirmation": False,
        "confirmation_granted": True
    }

    try:
        result = (
            confirmation_agent.invoke(
                initial_state
            )
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    status = result.get(
        "status",
        "unknown"
    )

    history = result.get(
        "history",
        []
    )

    tool_result = result.get(
        "tool_result"
    )

    message = build_user_message(
        status,
        history,
        tool_result
    )

    return {
        "task": request.task,
        "status": status,
        "message": message,
        "history": history,
        "tool_result": tool_result,
        "requires_confirmation":
            result.get(
                "requires_confirmation",
                False
            )
    }


# ============================================================
# HISTORY
# ============================================================

@app.get("/agent/history")
def get_history():

    memory = load_memory()

    return {
        "tasks": memory.get(
            "tasks",
            []
        )
    }


# ============================================================
# MEMORY
# ============================================================

@app.get("/agent/memory")
def get_memory():

    return {
        "memory":
            get_memory_summary(
                limit=20
            )
    }


# ============================================================
# TOOLS
# ============================================================

@app.get("/agent/tools")
def get_tools():

    return {
        "tools": [
            {
                "name": "list_files",
                "description":
                    "Lists files and folders "
                    "inside a directory.",
                "input":
                    "folder path"
            },
            {
                "name": "read_file",
                "description":
                    "Reads the contents of "
                    "a text-based file.",
                "input":
                    "complete file path"
            },
            {
                "name": "create_folder",
                "description":
                    "Creates a new folder.",
                "input":
                    "complete folder path"
            },
            {
                "name": "move_file",
                "description":
                    "Moves a file from one "
                    "location to another.",
                "input":
                    (
                        "source_path + "
                        "destination_path"
                    )
            },
            {
                "name": "write_file",
                "description":
                    "Creates or writes "
                    "content to a text file.",
                "input":
                    "file_path + content"
            },
            {
                "name": "copy_file",
                "description":
                    "Copies a file from one "
                    "location to another.",
                "input":
                    (
                        "source_path + "
                        "destination_path"
                    )
            },
            {
                "name": "search_files",
                "description":
                    "Searches recursively for "
                    "files whose names match "
                    "a search term.",
                "input":
                    (
                        "folder_path + "
                        "search_term"
                    )
            },
            {
                "name": "delete_file",
                "description":
                    "Deletes a file only after "
                    "explicit user confirmation.",
                "input":
                    "file_path"
            },
            {
                "name": "rename_file",
                "description":
                    "Renames an existing file "
                    "while keeping it in the "
                    "same folder.",
                "input":
                    "source_path + new_name"
            },
            {
                "name": "rename_folder",
                "description":
                    "Renames an existing folder "
                    "while keeping it in the same "
                    "parent directory.",
                "input":
                    "source_path + new_name"
            },
            {
                "name": "delete_folder",
                "description":
                    "Deletes a folder and its contents "
                    "only after explicit user confirmation.",
                "input":
                    "folder_path"
            },
            {
                "name": "organize_by_type",
                "description":
                    "Organizes files inside a folder "
                    "into categories based on file extension.",
                "input":
                    "folder_path"
            }
        ]
    }