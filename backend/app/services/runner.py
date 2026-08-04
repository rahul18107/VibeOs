import asyncio
import os
from pathlib import Path
from app.services.file_manager import get_project_path

async def run_command(
    command: str,
    project_name: str,
    on_output=None
) -> dict:
    
    project_path = get_project_path(project_name)
    
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(project_path)
    )

    stdout_lines = []
    stderr_lines = []

    async def read_stream(stream, lines_list, prefix=""):
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode("utf-8").strip()
            lines_list.append(decoded)
            if on_output:
                await on_output(f"{prefix}{decoded}")

    await asyncio.gather(
        read_stream(process.stdout, stdout_lines),
        read_stream(process.stderr, stderr_lines, prefix="ERROR: ")
    )

    await process.wait()

    return {
        "returncode": process.returncode,
        "stdout": stdout_lines,
        "stderr": stderr_lines,
        "success": process.returncode == 0
    }


async def run_npm_install(project_name: str, on_output=None) -> dict:
    return await run_command("npm install", project_name, on_output)


async def run_dev_server(project_name: str, on_output=None) -> dict:
    return await run_command("npm run dev", project_name, on_output)