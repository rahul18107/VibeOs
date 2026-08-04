from app.services.file_manager import create_project_folder, list_files, delete_project
from app.utils.supabase_client import supabase
from datetime import datetime

async def create_project(project_name: str) -> dict:
    
    folder_path = create_project_folder(project_name)

    result = supabase.table("projects").insert({
        "name": project_name,
        "status": "created",
        "path": str(folder_path),
    }).execute()

    project = result.data[0]

    return {
        "id": project["id"],
        "name": project["name"],
        "status": project["status"],
        "path": project["path"],
        "created_at": project["created_at"]
    }


async def get_project(project_name: str) -> dict | None:
    
    result = supabase.table("projects").select("*").eq(
        "name", project_name
    ).execute()

    if not result.data:
        return None

    return result.data[0]


async def get_all_projects() -> list:
    
    result = supabase.table("projects").select("*").order(
        "created_at", desc=True
    ).execute()

    return result.data


async def update_project_status(project_name: str, status: str):
    
    supabase.table("projects").update({
        "status": status
    }).eq("name", project_name).execute()


async def remove_project(project_name: str):
    
    delete_project(project_name)

    supabase.table("projects").delete().eq(
        "name", project_name
    ).execute()


async def get_project_files(project_name: str) -> list:
    return list_files(project_name)