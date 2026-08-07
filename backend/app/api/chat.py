from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.orchestrator import run

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

@router.post("/chat")
async def chat(request: ChatRequest):
    result = await run(request.prompt,"Calculator")
    return result