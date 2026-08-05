import traceback
from app.agents import planner, ui_agent
from app.services import file_manager, workspace
from app.utils.supabase_client import supabase

async def run(user_prompt: str, project_name: str, on_log=None) -> dict:

    async def log(message: str):
        if on_log:
            await on_log(message)
        print(message)

    try:
        # Step 1 — create project
        await log(f"Creating project: {project_name}")
        project = await workspace.create_project(project_name)
        await workspace.update_project_status(project_name, "generating")

        # Step 2 — plan tasks
        await log("Planning tasks...")
        tasks = await planner.run(user_prompt)
        await log(f"Got {len(tasks)} tasks from planner")

        # Step 3 — find the main UI task
        ui_task = None
        for task in tasks:
            if task["type"] == "create_file":
                ui_task = task
                break

        # fallback if planner returns nothing useful
        if not ui_task:
            ui_task = {
                "task": f"create {project_name} app",
                "type": "create_file",
                "description": user_prompt
            }

        # Step 4 — generate the app
        await log(f"Generating: {ui_task['task']}")
        result = await ui_agent.run(ui_task, project_name)

        file_manager.create_file(
            project_name,
            result["file_path"],
            result["content"]
        )
        await log(f"Created: {result['file_path']}")

        # Step 5 — log to supabase
        supabase.table("generated_files").insert({
            "project_id": project["id"],
            "file_path": result["file_path"],
            "content": result["content"]
        }).execute()

        supabase.table("chat_history").insert({
            "project_id": project["id"],
            "role": "user",
            "content": user_prompt
        }).execute()

        supabase.table("chat_history").insert({
            "project_id": project["id"],
            "role": "agent",
            "content": f"Built {project_name} successfully"
        }).execute()

        # Step 6 — update status
        await workspace.update_project_status(project_name, "ready")
        await log(f"Done! {project_name} is ready.")

        return {
            "success": True,
            "project": project,
            "file_path": str(file_manager.get_project_path(project_name) / "index.html"),
            "preview_url": f"/preview/{project_name}"
        }

    except Exception as e:
        await log(f"Error: {type(e).__name__}: {e}")
        traceback.print_exc()
        await workspace.update_project_status(project_name, "error")
        return {
            "success": False,
            "error": str(e)
        }