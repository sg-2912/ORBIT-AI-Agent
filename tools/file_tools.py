import os
import shutil


def normalize_path(path: str):
    """
    Converts a path into a normalized absolute path.
    Helpful for Windows paths and consistent file handling.
    """
    return os.path.abspath(
        os.path.normpath(path)
    )


def move_file(
    source_path: str,
    destination_path: str
):
    try:
        source_path = normalize_path(
            source_path
        )

        destination_path = normalize_path(
            destination_path
        )

        if not os.path.isfile(source_path):
            return {
                "success": False,
                "source": source_path,
                "error": "Source file does not exist."
            }

        shutil.move(
            source_path,
            destination_path
        )

        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
            "message": "File moved successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def list_files(folder_path: str):
    try:
        folder_path = normalize_path(
            folder_path
        )

        if not os.path.exists(folder_path):
            return {
                "success": False,
                "folder": folder_path,
                "error": "Folder does not exist."
            }

        if not os.path.isdir(folder_path):
            return {
                "success": False,
                "folder": folder_path,
                "error": "Path is not a folder."
            }

        files = os.listdir(
            folder_path
        )

        return {
            "success": True,
            "folder": folder_path,
            "files": files
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def read_file(file_path: str):
    try:
        file_path = normalize_path(
            file_path
        )

        if not os.path.isfile(file_path):
            return {
                "success": False,
                "file": file_path,
                "error": "File does not exist."
            }

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            content = file.read()

        return {
            "success": True,
            "file": file_path,
            "content": content
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def create_folder(folder_path: str):
    try:
        folder_path = normalize_path(
            folder_path
        )

        os.makedirs(
            folder_path,
            exist_ok=True
        )

        return {
            "success": True,
            "folder": folder_path,
            "message": "Folder created successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def write_file(
    file_path: str,
    content: str
):
    try:
        file_path = normalize_path(
            file_path
        )

        parent_folder = os.path.dirname(
            file_path
        )

        if parent_folder:
            os.makedirs(
                parent_folder,
                exist_ok=True
            )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(content)

        return {
            "success": True,
            "file": file_path,
            "message": "File written successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def copy_file(
    source_path: str,
    destination_path: str
):
    try:
        source_path = normalize_path(
            source_path
        )

        destination_path = normalize_path(
            destination_path
        )

        if not os.path.isfile(source_path):
            return {
                "success": False,
                "source": source_path,
                "error": "Source file does not exist."
            }

        shutil.copy2(
            source_path,
            destination_path
        )

        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
            "message": "File copied successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def search_files(
    folder_path: str,
    search_term: str
):
    try:
        folder_path = normalize_path(
            folder_path
        )

        if not os.path.isdir(folder_path):
            return {
                "success": False,
                "folder": folder_path,
                "error": "Search folder does not exist."
            }

        matches = []

        for root, directories, files in os.walk(
            folder_path
        ):
            for file_name in files:

                if (
                    search_term.lower()
                    in file_name.lower()
                ):
                    matches.append(
                        os.path.join(
                            root,
                            file_name
                        )
                    )

        return {
            "success": True,
            "folder": folder_path,
            "search_term": search_term,
            "matches": matches,
            "count": len(matches)
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def delete_file(file_path: str):
    try:
        file_path = normalize_path(
            file_path
        )

        print(
            f"🗑 Delete requested for: {file_path}"
        )

        if not os.path.exists(file_path):
            return {
                "success": False,
                "file": file_path,
                "error": "File does not exist."
            }

        if not os.path.isfile(file_path):
            return {
                "success": False,
                "file": file_path,
                "error": "Path exists but is not a file."
            }

        os.remove(
            file_path
        )

        return {
            "success": True,
            "file": file_path,
            "message": "File deleted successfully."
        }

    except PermissionError:
        return {
            "success": False,
            "file": file_path,
            "error": (
                "Permission denied. "
                "The file may be open or protected."
            )
        }

    except Exception as error:
        return {
            "success": False,
            "file": file_path,
            "error": str(error)
        }

def rename_file(
    source_path: str,
    new_name: str
):
    try:
        source_path = normalize_path(
            source_path
        )

        if not os.path.isfile(source_path):
            return {
                "success": False,
                "source": source_path,
                "error": "Source file does not exist."
            }

        folder_path = os.path.dirname(
            source_path
        )

        destination_path = os.path.join(
            folder_path,
            new_name
        )

        destination_path = normalize_path(
            destination_path
        )

        if os.path.exists(destination_path):
            return {
                "success": False,
                "source": source_path,
                "destination": destination_path,
                "error": "A file with the new name already exists."
            }

        os.rename(
            source_path,
            destination_path
        )

        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
            "message": "File renamed successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }

def rename_folder(
    source_path: str,
    new_name: str
):
    try:
        source_path = normalize_path(
            source_path
        )

        if not os.path.isdir(source_path):
            return {
                "success": False,
                "source": source_path,
                "error": "Source folder does not exist."
            }

        parent_folder = os.path.dirname(
            source_path
        )

        destination_path = os.path.join(
            parent_folder,
            new_name
        )

        destination_path = normalize_path(
            destination_path
        )

        if os.path.exists(destination_path):
            return {
                "success": False,
                "source": source_path,
                "destination": destination_path,
                "error": "A folder with the new name already exists."
            }

        os.rename(
            source_path,
            destination_path
        )

        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
            "message": "Folder renamed successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }

def delete_folder(folder_path: str):
    original_path = folder_path

    try:
        # Validate input first
        if not isinstance(folder_path, str):
            return {
                "success": False,
                "folder": str(folder_path),
                "error": "folder_path must be a string."
            }

        if not folder_path.strip():
            return {
                "success": False,
                "folder": folder_path,
                "error": "Folder path cannot be empty."
            }

        # Normalize path
        normalized_path = normalize_path(
            folder_path
        )

        print(
            f"🗑 Delete folder requested for: "
            f"{normalized_path}"
        )

        # Check existence
        if not os.path.exists(normalized_path):
            return {
                "success": False,
                "folder": normalized_path,
                "error": "Folder does not exist."
            }

        # Make sure it really is a folder
        if not os.path.isdir(normalized_path):
            return {
                "success": False,
                "folder": normalized_path,
                "error": "Path exists but is not a folder."
            }

        # Delete folder and everything inside it
        shutil.rmtree(
            normalized_path
        )

        return {
            "success": True,
            "folder": normalized_path,
            "message": "Folder deleted successfully."
        }

    except PermissionError:
        return {
            "success": False,
            "folder": str(original_path),
            "error": (
                "Permission denied. "
                "The folder or one of its files "
                "may currently be open or protected."
            )
        }

    except Exception as error:
        return {
            "success": False,
            "folder": str(original_path),
            "error": str(error)
        }

def organize_by_type(folder_path: str):
    try:
        folder_path = normalize_path(folder_path)

        if not os.path.isdir(folder_path):
            return {
                "success": False,
                "folder": folder_path,
                "error": "Folder does not exist."
            }

        category_map = {
            "Images": {
                ".jpg", ".jpeg", ".png", ".gif",
                ".webp", ".bmp", ".svg"
            },
            "Documents": {
                ".txt", ".doc", ".docx", ".rtf"
            },
            "PDFs": {
                ".pdf"
            },
            "Spreadsheets": {
                ".csv", ".xls", ".xlsx"
            },
            "Presentations": {
                ".ppt", ".pptx"
            },
            "Code": {
                ".py", ".js", ".jsx", ".ts",
                ".tsx", ".html", ".css",
                ".java", ".cpp", ".c"
            },
            "Archives": {
                ".zip", ".rar", ".7z", ".tar", ".gz"
            }
        }

        moved_files = []
        skipped_files = []

        for item_name in os.listdir(folder_path):
            source_path = os.path.join(
                folder_path,
                item_name
            )

            if not os.path.isfile(source_path):
                continue

            extension = os.path.splitext(
                item_name
            )[1].lower()

            category = "Other"

            for category_name, extensions in category_map.items():
                if extension in extensions:
                    category = category_name
                    break

            target_folder = os.path.join(
                folder_path,
                category
            )

            os.makedirs(
                target_folder,
                exist_ok=True
            )

            destination_path = os.path.join(
                target_folder,
                item_name
            )

            if os.path.exists(destination_path):
                skipped_files.append(
                    source_path
                )
                continue

            shutil.move(
                source_path,
                destination_path
            )

            moved_files.append({
                "source": source_path,
                "destination": destination_path,
                "category": category
            })

        return {
            "success": True,
            "folder": folder_path,
            "moved_count": len(moved_files),
            "skipped_count": len(skipped_files),
            "moved_files": moved_files,
            "skipped_files": skipped_files,
            "message": "Files organized successfully."
        }

    except Exception as error:
        return {
            "success": False,
            "folder": str(folder_path),
            "error": str(error)
        }