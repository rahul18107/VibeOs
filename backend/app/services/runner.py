import asyncio
import os
import socket
import subprocess
import threading
from app.services.file_manager import get_project_path


# The scaffolded vite.config.js is generated from this value.
DEV_SERVER_PORT = 3001

ALLOWED_COMMANDS = {
    "npm install",
    "npm run dev",
    "npm run build",
    "npm run preview",
}


def _supports_subprocess() -> bool:
    return isinstance(
        asyncio.get_running_loop(),
        getattr(asyncio, "ProactorEventLoop", type(None)),
    ) or os.name != "nt"


async def _run_threaded(command, project_path, env, on_output) -> dict:
    loop = asyncio.get_running_loop()
    stdout_lines = []
    stderr_lines = []

    def pump(stream, lines_list, prefix):
        for raw in stream:
            decoded = raw.rstrip("\r\n")
            lines_list.append(decoded)
            if on_output:
                asyncio.run_coroutine_threadsafe(
                    on_output(f"{prefix}{decoded}"), loop
                ).result()

    def work():
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(project_path),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        threads = [
            threading.Thread(target=pump, args=(process.stdout, stdout_lines, "")),
            threading.Thread(target=pump, args=(process.stderr, stderr_lines, "ERROR: ")),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return process.wait()

    returncode = await asyncio.to_thread(work)

    return {
        "returncode": returncode,
        "stdout": stdout_lines,
        "stderr": stderr_lines,
        "success": returncode == 0,
    }


async def run_command(
    command: str,
    project_name: str,
    on_output=None
) -> dict:

    project_path = get_project_path(project_name)

    if command not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {command!r}")

    env = os.environ.copy()
    env["PATH"] = "C:\\Program Files\\nodejs" + ";" + env.get("PATH", "")

    if not _supports_subprocess():
        return await _run_threaded(command, project_path, env, on_output)

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(project_path),
        env=env
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


# Dev servers never exit, so they are tracked instead of awaited.
_dev_servers: dict[str, subprocess.Popen] = {}


async def start_dev_server(project_name: str, on_output=None, timeout: float = 60.0) -> dict:
    stop_dev_server(project_name)

    project_path = get_project_path(project_name)
    env = os.environ.copy()
    env["PATH"] = "C:\\Program Files\\nodejs" + ";" + env.get("PATH", "")

    process = subprocess.Popen(
        "npm run dev",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(project_path),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    _dev_servers[project_name] = process

    loop = asyncio.get_running_loop()
    lines = []

    def pump():
        for raw in process.stdout:
            line = raw.rstrip("\r\n")
            lines.append(line)
            if on_output:
                asyncio.run_coroutine_threadsafe(on_output(line), loop)

    threading.Thread(target=pump, daemon=True).start()

    started = False
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if process.poll() is not None:
            break
        try:
            # vite binds IPv6 ::1 by default, so resolve via localhost
            with socket.create_connection(("localhost", DEV_SERVER_PORT), timeout=1):
                started = True
                break
        except OSError:
            await asyncio.sleep(0.3)

    return {
        "success": started,
        "pid": process.pid,
        "url": f"http://localhost:{DEV_SERVER_PORT}/" if started else None,
        "output": lines,
    }


def stop_dev_server(project_name: str) -> bool:
    process = _dev_servers.pop(project_name, None)
    if process is None or process.poll() is not None:
        return False
    subprocess.run(
        ["taskkill", "/F", "/T", "/PID", str(process.pid)],
        capture_output=True,
    )
    return True