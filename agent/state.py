from typing import TypedDict, List, Optional, Any


class AgentState(TypedDict):
    task: str
    plan: List[str]
    actions: List[dict]
    current_action: int
    current_step: int
    status: str
    selected_tool: Optional[str]
    tool_input: Any
    tool_result: Any
    retry_count: int
    history: List[dict]
    requires_confirmation: bool
    confirmation_granted: bool