import os
import re


# ============================================================
# HELPERS
# ============================================================

def clean_text(text: str):
    return text.strip().strip(",")


def get_file_name(file_path: str):
    return os.path.basename(
        file_path.replace("\\", "/")
    )


def join_windows_path(folder_path: str, file_name: str):
    return (
        folder_path.rstrip("\\/")
        + "\\"
        + file_name
    )


def build_result(plan, actions):
    return {
        "plan": plan,
        "actions": actions
    }


# ============================================================
# ORGANIZE BY TYPE
# ============================================================

def parse_organize_by_type(command: str):
    match = re.match(
        r"^\s*organize\s+(?:all\s+)?files\s+"
        r"(?:inside|in)\s+(.+?)\s+"
        r"by\s+file\s+type\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    folder_path = clean_text(
        match.group(1)
    )

    return {
        "plan":
            f"Organize files inside {folder_path} by file type.",
        "action": {
            "tool": "organize_by_type",
            "input": {
                "folder_path": folder_path
            }
        },
        "context": {
            "last_folder": folder_path
        }
    }


# ============================================================
# CREATE FOLDER
# ============================================================

def parse_create_folder(command: str):
    match = re.match(
        r"^\s*create\s+(?:a\s+)?folder\s+([^,]+?)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    folder_path = clean_text(
        match.group(1)
    )

    return {
        "plan":
            f"Create the folder {folder_path}.",
        "action": {
            "tool": "create_folder",
            "input": folder_path
        },
        "context": {
            "last_folder": folder_path
        }
    }


# ============================================================
# WRITE FILE
# ============================================================

def parse_write_file(command: str):
    match = re.match(
        r"^\s*create\s+"
        r"(.+?\.[A-Za-z0-9]+)\s+"
        r"and\s+write\s+"
        r"(.+?)\s+"
        r"inside\s+it\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    file_path = clean_text(
        match.group(1)
    )

    content = clean_text(
        match.group(2)
    )

    return {
        "plan":
            f"Create {file_path} and write the requested content.",
        "action": {
            "tool": "write_file",
            "input": {
                "file_path": file_path,
                "content": content
            }
        },
        "context": {
            "last_file": file_path
        }
    }


# ============================================================
# READ FILE
# ============================================================

def parse_read_file(command: str):
    match = re.match(
        r"^\s*read\s+(.+?)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    file_path = clean_text(
        match.group(1)
    )

    return {
        "plan":
            f"Read the file {file_path}.",
        "action": {
            "tool": "read_file",
            "input": file_path
        },
        "context": {
            "last_file": file_path
        }
    }


# ============================================================
# LIST FILES
# ============================================================

def parse_list_files(command: str, context=None):
    context = context or {}

    relative_match = re.match(
        r"^\s*list\s+"
        r"(?:all\s+)?"
        r"(?:the\s+)?"
        r"files\s+"
        r"(?:inside|in)\s+it\s*$",
        command,
        re.IGNORECASE
    )

    if relative_match:
        folder_path = context.get(
            "last_folder"
        )

        if not folder_path:
            return None

        return {
            "plan":
                f"List the files inside {folder_path}.",
            "action": {
                "tool": "list_files",
                "input": folder_path
            },
            "context": {}
        }

    match = re.match(
        r"^\s*list\s+"
        r"(?:all\s+)?"
        r"(?:the\s+)?"
        r"files\s+"
        r"(?:inside|in)\s+(.+?)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    folder_path = clean_text(
        match.group(1)
    )

    return {
        "plan":
            f"List files inside {folder_path}.",
        "action": {
            "tool": "list_files",
            "input": folder_path
        },
        "context": {
            "last_folder": folder_path
        }
    }


# ============================================================
# COPY FILE
# ============================================================

def parse_copy_file(command: str, context=None):
    context = context or {}

    into_it_match = re.match(
        r"^\s*copy\s+(.+?)\s+into\s+it\s*$",
        command,
        re.IGNORECASE
    )

    if into_it_match:
        source_path = clean_text(
            into_it_match.group(1)
        )

        folder_path = context.get(
            "last_folder"
        )

        if not folder_path:
            return None

        file_name = get_file_name(
            source_path
        )

        destination_path = join_windows_path(
            folder_path,
            file_name
        )

        return {
            "plan":
                f"Copy {source_path} into {folder_path}.",
            "action": {
                "tool": "copy_file",
                "input": {
                    "source_path": source_path,
                    "destination_path":
                        destination_path
                }
            },
            "context": {
                "last_file": destination_path
            }
        }

    match = re.match(
        r"^\s*copy\s+(.+?)\s+to\s+(.+?)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    source_path = clean_text(
        match.group(1)
    )

    destination_path = clean_text(
        match.group(2)
    )

    return {
        "plan":
            f"Copy {source_path} to {destination_path}.",
        "action": {
            "tool": "copy_file",
            "input": {
                "source_path": source_path,
                "destination_path":
                    destination_path
            }
        },
        "context": {
            "last_file": destination_path
        }
    }


# ============================================================
# MOVE FILE
# ============================================================

def parse_move_file(command: str, context=None):
    context = context or {}

    into_it_match = re.match(
        r"^\s*move\s+(.+?)\s+into\s+it\s*$",
        command,
        re.IGNORECASE
    )

    if into_it_match:
        source_path = clean_text(
            into_it_match.group(1)
        )

        folder_path = context.get(
            "last_folder"
        )

        if not folder_path:
            return None

        file_name = get_file_name(
            source_path
        )

        destination_path = join_windows_path(
            folder_path,
            file_name
        )

        return {
            "plan":
                f"Move {source_path} into {folder_path}.",
            "action": {
                "tool": "move_file",
                "input": {
                    "source_path": source_path,
                    "destination_path":
                        destination_path
                }
            },
            "context": {
                "last_file": destination_path
            }
        }

    match = re.match(
        r"^\s*move\s+(.+?)\s+to\s+(.+?)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    source_path = clean_text(
        match.group(1)
    )

    destination_path = clean_text(
        match.group(2)
    )

    return {
        "plan":
            f"Move {source_path} to {destination_path}.",
        "action": {
            "tool": "move_file",
            "input": {
                "source_path": source_path,
                "destination_path":
                    destination_path
            }
        },
        "context": {
            "last_file": destination_path
        }
    }


# ============================================================
# RENAME FOLDER
# ============================================================

def parse_rename_folder(command: str):
    match = re.match(
        r"^\s*rename\s+"
        r"(?:the\s+)?folder\s+"
        r"(.+?)\s+to\s+"
        r"([^\s\\/]+)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    source_path = clean_text(
        match.group(1)
    )

    new_name = clean_text(
        match.group(2)
    )

    parent = os.path.dirname(
        source_path
    )

    new_path = join_windows_path(
        parent,
        new_name
    )

    return {
        "plan":
            f"Rename the folder {source_path} to {new_name}.",
        "action": {
            "tool": "rename_folder",
            "input": {
                "source_path": source_path,
                "new_name": new_name
            }
        },
        "context": {
            "last_folder": new_path
        }
    }


# ============================================================
# RENAME FILE
# ============================================================

def parse_rename_file(command: str):
    match = re.match(
        r"^\s*rename\s+"
        r"(?!folder\s)"
        r"(.+?)\s+to\s+"
        r"([^\s\\/]+)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    source_path = clean_text(
        match.group(1)
    )

    new_name = clean_text(
        match.group(2)
    )

    folder_path = os.path.dirname(
        source_path
    )

    new_path = join_windows_path(
        folder_path,
        new_name
    )

    return {
        "plan":
            f"Rename {source_path} to {new_name}.",
        "action": {
            "tool": "rename_file",
            "input": {
                "source_path": source_path,
                "new_name": new_name
            }
        },
        "context": {
            "last_file": new_path
        }
    }


# ============================================================
# DELETE FOLDER
# ============================================================

def parse_delete_folder(command: str):
    match = re.match(
        r"^\s*delete\s+"
        r"(?:the\s+)?folder\s+"
        r"(.+?)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    folder_path = clean_text(
        match.group(1)
    )

    return {
        "plan":
            f"Delete the folder {folder_path}.",
        "action": {
            "tool": "delete_folder",
            "input": {
                "folder_path": folder_path
            }
        },
        "context": {}
    }


# ============================================================
# DELETE FILE
# ============================================================

def parse_delete_file(command: str):
    match = re.match(
        r"^\s*delete\s+"
        r"(?!folder\s)"
        r"(.+?)\s*$",
        command,
        re.IGNORECASE
    )

    if not match:
        return None

    file_path = clean_text(
        match.group(1)
    )

    return {
        "plan":
            f"Delete the file {file_path}.",
        "action": {
            "tool": "delete_file",
            "input": {
                "file_path": file_path
            }
        },
        "context": {}
    }


# ============================================================
# PARSE ONE COMMAND
# ============================================================

def parse_single_command(command: str, context=None):
    context = context or {}

    parsers = [
        lambda value:
            parse_organize_by_type(value),

        lambda value:
            parse_create_folder(value),

        lambda value:
            parse_write_file(value),

        lambda value:
            parse_copy_file(
                value,
                context
            ),

        lambda value:
            parse_move_file(
                value,
                context
            ),

        lambda value:
            parse_list_files(
                value,
                context
            ),

        lambda value:
            parse_read_file(value),

        lambda value:
            parse_rename_folder(value),

        lambda value:
            parse_rename_file(value),

        lambda value:
            parse_delete_folder(value),

        lambda value:
            parse_delete_file(value),
    ]

    for parser in parsers:
        parsed = parser(
            command
        )

        if parsed:
            return parsed

    return None


# ============================================================
# SPLIT MULTI-COMMAND TASK
# ============================================================

def split_commands(task: str):
    normalized = task.strip()

    parts = re.split(
        r"\s*,\s*",
        normalized
    )

    commands = []

    for part in parts:
        part = part.strip()

        part = re.sub(
            r"^(?:and|then)\s+",
            "",
            part,
            flags=re.IGNORECASE
        )

        if part:
            commands.append(
                part
            )

    return commands


# ============================================================
# MAIN LOCAL PLANNER
# ============================================================

def local_plan(task: str):
    """
    Local deterministic planner for common
    filesystem tasks.
    """

    if not isinstance(
        task,
        str
    ):
        return None

    task = task.strip()

    if not task:
        return None

    # ========================================================
    # MULTI-COMMAND FIRST
    # ========================================================

    commands = split_commands(
        task
    )

    if len(commands) > 1:
        plan = []
        actions = []

        context = {
            "last_folder": None,
            "last_file": None
        }

        for command in commands:
            parsed = parse_single_command(
                command,
                context
            )

            if not parsed:
                return None

            plan.append(
                parsed["plan"]
            )

            actions.append(
                parsed["action"]
            )

            new_context = parsed.get(
                "context",
                {}
            )

            for key, value in new_context.items():
                if value is not None:
                    context[key] = value

        return build_result(
            plan,
            actions
        )

    # ========================================================
    # SINGLE COMMAND
    # ========================================================

    single_result = parse_single_command(
        task,
        {}
    )

    if single_result:
        return build_result(
            [
                single_result["plan"]
            ],
            [
                single_result["action"]
            ]
        )

    return None