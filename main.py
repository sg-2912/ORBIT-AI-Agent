from agent.graph import create_agent_graph
from memory.memory_manager import save_task_to_memory

def main():
    print("=" * 50)
    print("🤖 ORBIT AI AGENT")
    print("=" * 50)

    agent = create_agent_graph()

    task = input("\nWhat would you like ORBIT to do?\n> ")

    initial_state = {
        "task": task,
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
        "confirmation_granted": False,
    }

    result = agent.invoke(initial_state)
    
    save_task_to_memory(
    task=task,
    status=result["status"],
    history=result["history"]
)

    print("\n📋 ORBIT PLAN")
    print("-" * 40)

    for number, step in enumerate(result["plan"], start=1):
        print(f"{number}. {step}")

    print("\n🔧 Selected Tool:")
    print(result["selected_tool"])

    print("\n📥 Tool Input:")
    print(result["tool_input"])

    print("\n⚙️ Tool Result:")
    print(result["tool_result"])

    print("\nStatus:")
    print(result["status"])

    print("\n🧾 EXECUTION HISTORY")
    print("-" * 40)

    for item in result["history"]:
        print(
            f"Action {item['action_number']} | "
            f"Tool: {item['tool']}"
        )

        print("Input:", item["input"])
        print("Result:", item["result"])
        print("-" * 40)


if __name__ == "__main__":
    main()