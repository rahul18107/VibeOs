from fastapi import APIRouter
from app.services.workspace import get_all_projects, get_project

router = APIRouter()

@router.get("/projects")
async def list_projects():
    projects = await get_all_projects()
    return {"projects": projects}

@router.get("/projects/{project_name}")
async def get_one_project(project_name: str):
    project = await get_project(project_name)
    if not project:
        return {"error": "Project not found"}, 404
    return {"project": project}