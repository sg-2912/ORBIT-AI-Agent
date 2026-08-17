import json
import os


MEMORY_FILE = "memory/orbit_memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "tasks": []
        }

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception:
        return {
            "tasks": []
        }


def save_task_to_memory(task, status, history):
    memory = load_memory()

    memory["tasks"].append({
        "task": task,
        "status": status,
        "history": history
    })

    os.makedirs(
        os.path.dirname(MEMORY_FILE),
        exist_ok=True
    )

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            indent=4
        )

def get_recent_tasks(limit=5):
    memory = load_memory()

    tasks = memory.get("tasks", [])

    return tasks[-limit:]

def get_memory_summary(limit=5):
    memory = load_memory()

    tasks = memory.get("tasks", [])

    recent_tasks = tasks[-limit:]

    summary = []

    for item in recent_tasks:
        summary.append({
            "task": item.get("task"),
            "status": item.get("status")
        })

    return summary