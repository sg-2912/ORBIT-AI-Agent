import os


def list_files(folder_path: str):
    try:
        files = os.listdir(folder_path)

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