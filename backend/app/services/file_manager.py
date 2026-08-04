import os
import shutil
from pathlib import Path

BASE_WORKSPACE = Path(__file__).parent.parent.parent / "workspace"

def get_project_path(project_name: str) -> Path:
    return BASE_WORKSPACE / project_name

def create_project_folder(project_name: str) -> Path:
    project_path = get_project_path(project_name)
    project_path.mkdir(parents=True, exist_ok=True)
    return project_path 

def create_file(project_name: str, file_path: str, content: str) -> str:
    full_path = get_project_path(project_name) / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

def read_file(project_name: str, file_path: str) -> str:
    full_path = get_project_path(project_name) / file_path
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return full_path.read_text(encoding="utf-8")

def write_file(project_name: str, file_path: str, content: str) -> str:
    full_path = get_project_path(project_name) / file_path
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

def delete_file(project_name: str, file_path: str):
    full_path = get_project_path(project_name) / file_path
    if full_path.exists():
        full_path.unlink()

def list_files(project_name: str) -> list:
    project_path = get_project_path(project_name)
    if not project_path.exists():
        return []
    files = []
    for file in project_path.rglob("*"):
        if file.is_file():
            files.append(str(file.relative_to(project_path)))
    return files

def delete_project(project_name: str):
    project_path = get_project_path(project_name)
    if project_path.exists():
        shutil.rmtree(project_path)