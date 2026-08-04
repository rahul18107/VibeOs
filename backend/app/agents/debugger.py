from app.providers.cloudflare import generate_json
from app.services.file_manager import read_file, write_file

DEBUGGER_SYSTEM_PROMPT = """
You are a React debugging expert for VibeOS.

You will be given a file's code and an error message.

Your job is to fix the code and return the corrected version.

You must respond with ONLY a JSON object. No explanation, no markdown, no extra text.

The JSON object must have:
- "file_path": the same file path that was given to you
- "content": the fully corrected file content
- "fix_description": one sentence explaining what you fixed

Rules:
- Return the COMPLETE file content, not just the changed lines
- Do not add any new external library imports
- Do not change the structure of the component, only fix the error
- If you cannot fix the error, return the original code unchanged
"""

async def run(
    project_name: str,
    file_path: str,
    error_message: str
) -> dict:

    original_code = read_file(project_name, file_path)

    prompt = f"""
Project: {project_name}
File: {file_path}
Error: {error_message}

Code:
{original_code}

Fix the error in this code.
"""

    result = await generate_json(
        prompt=prompt,
        system=DEBUGGER_SYSTEM_PROMPT
    )

    write_file(project_name, file_path, result["content"])

    return {
        "file_path": result["file_path"],
        "fix_description": result["fix_description"],
        "success": True
    }