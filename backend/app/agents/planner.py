from app.providers.cloudflare import generate_json

PLANNER_SYSTEM_PROMPT = """
You are a software architect for VibeOS, an AI workspace that builds apps.

Your job is to break down a user's app request into a clear list of tasks.

You must respond with ONLY a JSON array. No explanation, no markdown, no extra text.

Each task in the array must have:
- "task": short name of the task
- "type": one of ["create_file", "run_command"]
- "description": what needs to be done

Example response for "build me a calculator app":
[
  {"task": "create App.jsx", "type": "create_file", "description": "Main calculator component with buttons and display"},
  {"task": "create index.css", "type": "create_file", "description": "Basic styles for the calculator"},
  {"task": "run npm install", "type": "run_command", "description": "Install dependencies"},
  {"task": "run dev server", "type": "run_command", "description": "Start the development server"}
]
"""

async def run(user_prompt: str) -> list:

    return await generate_json(
        prompt=f"Break this app request into tasks: {user_prompt}",
        system=PLANNER_SYSTEM_PROMPT
    )