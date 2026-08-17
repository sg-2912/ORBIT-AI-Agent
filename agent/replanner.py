import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from agent.state import AgentState


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def replanner_node(state: AgentState):
    print("\n🧠 ORBIT Replanner started...")

    task = state["task"]
    tool_result = state["tool_result"]
    current_action = state["current_action"]
    actions = state["actions"]

    failed_action = actions[current_action]

    prompt = f"""
You are the replanning module of an AI agent called ORBIT.

Original user task:
{task}

Failed action:
{json.dumps(failed_action, indent=2)}

Tool result:
{json.dumps(tool_result, indent=2)}

Available tools:

1. list_files
2. read_file
3. create_folder
4. move_file

Create the minimum number of new actions required to recover from
the failure and continue completing the original task.

For move_file, input must contain:
- source_path
- destination_path

Only use the available tools.
Do not repeat the exact failed action unless another action first fixes
the reason it failed.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
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
                        "actions"
                    ]
                }
            )
        )

    except Exception as error:
        error_text = str(error)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            print("\n⚠️ Gemini quota exceeded during replanning.")

            return {
                "status": "llm_quota_exceeded",
                "retry_count": 0
            }

        raise

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response during replanning."
        )

    data = json.loads(response.text)

    new_actions = (
        actions[:current_action]
        + data["actions"]
    )

    print(
        f"Replanned with "
        f"{len(data['actions'])} new action(s)."
    )

    return {
        "actions": new_actions,
        "current_action": current_action,
        "retry_count": 0,
        "status": "replanned"
    }