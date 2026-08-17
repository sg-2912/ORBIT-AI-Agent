import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from agent.state import AgentState
from memory.memory_manager import get_memory_summary
from agent.local_planner import local_plan


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


PLANNER_SCHEMA = {
    "type": "object",
    "properties": {
        "plan": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tool": {
                        "type": "string"
                    },
                    "input": {}
                },
                "required": [
                    "tool",
                    "input"
                ]
            }
        }
    },
    "required": [
        "plan",
        "actions"
    ]
}


def planner_node(state: AgentState):
    print("\n🧠 ORBIT AI Planner started...")

    task = state["task"]

    # =========================================
    # LOCAL PLANNER FIRST
    # =========================================
    #
    # Simple deterministic file operations do
    # not need an LLM call.
    #
    # This also keeps ORBIT working when Gemini
    # quota is unavailable.
    # =========================================

    local_result = local_plan(task)

    if local_result:
        print(
            "🧩 ORBIT Local Planner activated."
        )

        print(
            f"Generated "
            f"{len(local_result['actions'])} "
            f"local action(s)."
        )

        return {
            "plan": local_result["plan"],
            "actions": local_result["actions"],
            "current_action": 0,
            "current_step": 0,
            "status": "planned"
        }

    # =========================================
    # GEMINI FOR COMPLEX TASKS
    # =========================================

    print(
        "✨ Local planner could not understand task."
    )

    print(
        "🤖 Sending task to Gemini..."
    )

    recent_tasks = get_memory_summary(
        limit=5
    )

    prompt = f"""
You are the planning module of an AI computer-use agent named ORBIT.

User task:
{task}

Recent ORBIT memory:

{json.dumps(recent_tasks, indent=2)}

Use this memory only when it is relevant to the current task.

Do not blindly repeat old actions.

Available tools:

1. list_files

Input:

"folder_path"


2. read_file

Input:

"file_path"


3. create_folder

Input:

"folder_path"


4. move_file

Input:

{{
    "source_path": "...",
    "destination_path": "..."
}}


5. write_file

Input:

{{
    "file_path": "...",
    "content": "..."
}}

For write_file, input must contain:

{{
    "file_path": "complete file path",
    "content": "text to write"
}}


6. copy_file

Input:

{{
    "source_path": "...",
    "destination_path": "..."
}}

For copy_file, input must contain:

{{
    "source_path": "complete source path",
    "destination_path": "complete destination path"
}}


7. search_files

Input:

{{
    "folder_path": "...",
    "search_term": "..."
}}

For search_files, input must contain:

{{
    "folder_path": "directory to search",
    "search_term": "file name or partial file name"
}}


8. delete_file

Input:

{{
    "file_path": "..."
}}

For delete_file, input must contain:

{{
    "file_path": "complete file path"
}}


9. rename_file

Input:

{{
    "source_path": "...",
    "new_name": "..."
}}

For rename_file, input must contain:

{{
    "source_path":
        "complete path of the existing file",

    "new_name":
        "new file name including extension"
}}

10. rename_folder
    Input:
    {
        "source_path": "...",
        "new_name": "..."
    }

For rename_folder, input must contain:

{
    "source_path": "complete path of the existing folder",
    "new_name": "new folder name"
}

11. organize_by_type

Input:

{{
    "folder_path": "..."
}}

For organize_by_type, input must contain:

{{
    "folder_path": "folder whose files should be organized by extension"
}}

Important:

delete_file is destructive.

Use delete_file only when the user explicitly asks
to delete a file.

Do NOT replace delete_file with another tool when
the user clearly requested deletion.


Create:

1. A human-readable step-by-step plan.

2. A machine-executable action list using only
   the available tools.


Important rules:

- Use only tools that are actually required.

- Keep actions in the exact order they must execute.

- Do not invent files or paths unless they can be
  logically derived from the user's task.

- Every action must contain a valid tool name.

- Every action must contain the correct input structure.

- If the user explicitly asks to delete a file,
  select delete_file.

- Return only the structured JSON response.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PLANNER_SCHEMA
            )
        )

    # =========================================
    # GEMINI API ERRORS
    # =========================================

    except errors.APIError as error:
        code = getattr(
            error,
            "code",
            None
        )

        message = str(error)

        # -------------------------------------
        # 429 QUOTA
        # -------------------------------------

        if (
            code == 429
            or "RESOURCE_EXHAUSTED" in message
        ):
            print(
                "\n⚠️ Gemini quota exceeded."
            )

            # Try local planner again as backup.
            fallback = local_plan(task)

            if fallback:
                print(
                    "🧩 Local fallback planner activated."
                )

                return {
                    "plan": fallback["plan"],
                    "actions": fallback["actions"],
                    "current_action": 0,
                    "current_step": 0,
                    "status": "planned"
                }

            return {
                "plan": [],
                "actions": [],
                "current_action": 0,
                "current_step": 0,
                "status": "llm_quota_exceeded"
            }

        # -------------------------------------
        # 503 SERVICE UNAVAILABLE
        # -------------------------------------

        if (
            code == 503
            or "UNAVAILABLE" in message
        ):
            print(
                "\n⚠️ Gemini is temporarily unavailable."
            )

            fallback = local_plan(task)

            if fallback:
                print(
                    "🧩 Local fallback planner activated."
                )

                return {
                    "plan": fallback["plan"],
                    "actions": fallback["actions"],
                    "current_action": 0,
                    "current_step": 0,
                    "status": "planned"
                }

            return {
                "plan": [],
                "actions": [],
                "current_action": 0,
                "current_step": 0,
                "status": "llm_service_unavailable"
            }

        # -------------------------------------
        # OTHER GEMINI ERROR
        # -------------------------------------

        print(
            f"\n❌ Gemini API error: {error}"
        )

        return {
            "plan": [],
            "actions": [],
            "current_action": 0,
            "current_step": 0,
            "status": "llm_error"
        }

    # =========================================
    # OTHER PLANNER ERRORS
    # =========================================

    except Exception as error:
        print(
            f"\n❌ Unexpected planner error: {error}"
        )

        # One last local attempt.
        fallback = local_plan(task)

        if fallback:
            print(
                "🧩 Local fallback planner activated."
            )

            return {
                "plan": fallback["plan"],
                "actions": fallback["actions"],
                "current_action": 0,
                "current_step": 0,
                "status": "planned"
            }

        return {
            "plan": [],
            "actions": [],
            "current_action": 0,
            "current_step": 0,
            "status": "planner_error"
        }

    # =========================================
    # EMPTY RESPONSE
    # =========================================

    if not response.text:
        print(
            "\n❌ Gemini returned an empty response."
        )

        fallback = local_plan(task)

        if fallback:
            print(
                "🧩 Local fallback planner activated."
            )

            return {
                "plan": fallback["plan"],
                "actions": fallback["actions"],
                "current_action": 0,
                "current_step": 0,
                "status": "planned"
            }

        return {
            "plan": [],
            "actions": [],
            "current_action": 0,
            "current_step": 0,
            "status": "planner_error"
        }

    # =========================================
    # PARSE GEMINI RESPONSE
    # =========================================

    try:
        data = json.loads(
            response.text
        )

    except json.JSONDecodeError as error:
        print(
            "\n❌ Planner JSON parsing failed:"
        )

        print(error)

        fallback = local_plan(task)

        if fallback:
            print(
                "🧩 Local fallback planner activated."
            )

            return {
                "plan": fallback["plan"],
                "actions": fallback["actions"],
                "current_action": 0,
                "current_step": 0,
                "status": "planned"
            }

        return {
            "plan": [],
            "actions": [],
            "current_action": 0,
            "current_step": 0,
            "status": "planner_error"
        }

    # =========================================
    # VALIDATE RESPONSE
    # =========================================

    plan = data.get(
        "plan",
        []
    )

    actions = data.get(
        "actions",
        []
    )

    if not isinstance(plan, list):
        plan = []

    if not isinstance(actions, list):
        actions = []

    if not actions:
        print(
            "⚠️ Gemini returned no executable actions."
        )

        fallback = local_plan(task)

        if fallback:
            print(
                "🧩 Local fallback planner activated."
            )

            return {
                "plan": fallback["plan"],
                "actions": fallback["actions"],
                "current_action": 0,
                "current_step": 0,
                "status": "planned"
            }

    print(
        f"Generated {len(actions)} action(s)."
    )

    return {
        "plan": plan,
        "actions": actions,
        "current_action": 0,
        "current_step": 0,
        "status": "planned"
    }