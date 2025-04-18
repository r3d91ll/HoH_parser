from typing import List
import os

def list_py_files(directory: str) -> List[str]:
    """Recursively list all Python files in a directory."""
    py_files: List[str] = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files
