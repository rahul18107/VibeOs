from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.services.file_manager import BASE_WORKSPACE
import os

router = APIRouter()

@router.get("/preview/{project_name}")
async def preview(project_name: str):
    path = os.path.join(BASE_WORKSPACE, project_name, "index.html")
    if not os.path.exists(path):
        return {"error": "Project not found"}
    return FileResponse(path, media_type="text/html")