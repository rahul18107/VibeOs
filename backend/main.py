import asyncio
import sys

# Windows subprocesses (npm install, npm run dev) require the Proactor loop;
# the Selector loop raises a bare NotImplementedError.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.agents.ui_agent import run as ui_agent_run
from app.utils.config import APP_ENV
from app.agents.orchestrator import run as orchestrator_run

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("VibeOS backend starting...")
    yield
    print("VibeOS backend shutting down...")

app = FastAPI(
    title="VibeOS",
    description="AI workspace that builds software through conversation",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "VibeOS",
        "env": APP_ENV
    }



@app.get("/test-ui-agent")
async def test_ui_agent():
    task = {
        "task": "create App.jsx",
        "type": "create_file",
        "description": "Main calculator component with buttons and display"
    }
    result = await ui_agent_run(task, "Calculator")
    return result



@app.post("/test-orchestrator")
async def test_orchestrator():
    result = await orchestrator_run(
        user_prompt="build me a simple calculator app",
        project_name="Calculator"
    )
    return result


