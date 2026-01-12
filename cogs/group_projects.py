from datetime import datetime, timedelta
from discord.ext import commands, tasks
from utils.json_io import load_json, save_json
from utils.functions import (
    get_next_project_id,
    check_phase_completion,
    check_labor_completion,
    find_wildcard_match
)

ACTIVE_PROJECTS_FILE = "data/active_projects.json"
PROJECTS_FILE = "data/projects.json"
INVENTORY_DIR = "data/inventories/"
MAX_HOURS_PER_WORK = 10  # Adjustable limit per !work_on_project


class GroupProjects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_labor_completion.start()

    @commands.command(name="start_project")
    async def start_project(self, ctx, project_type: str):
        """Start a new project."""
        project_type = project_type.lower()
        projects = load_json(ACTIVE_PROJECTS_FILE)
        project_definitions = load_json(PROJECTS_FILE).get("project_types", {})

        if project_type not in project_definitions:
            await ctx.send(f"❌ Project type '{project_type}' does not exist.", delete_after=5)
            return

        project_def = project_definitions[project_type]
        project_id = get_next_project_id(projects)

        project = {
            "id": project_id,
            "type": project_type,
            "name": project_def["name"],
            "phases": [
                {"phase": phase["phase"], "required": phase["required"],
                 "contributed": {k: 0 for k in phase["required"]}}
                for phase in project_def["phases"]
            ],
            "current_phase_index": 0,
            "status": "active",
            "created_by": str(ctx.author.id),
            "reward": project_def.get("reward", "None"),
            "contributors": {}
        }

        projects[str(project_id)] = project
        save_json(ACTIVE_PROJECTS_FILE, projects)
        await ctx.send(f"✅ Project **{project['name']}** (ID: {project_id}) has been started!", delete_after=5)

    @commands.command(name="list_projects")
    async def list_projects(self, ctx):
        """List all active projects."""
        projects = load_json(ACTIVE_PROJECTS_FILE)
        active_projects = [p for p in projects.values() if p["status"] == "active"]

        if not active_projects:
            await ctx.send("📜 There are currently **no active projects**.", delete_after=5)
            return

        response = "**🛠️ Active Projects:**\n"
        for project in active_projects:
            response += f"- **{project['name']}** (ID: `{project['id']}`), Phase: **{project['phases'][project['current_phase_index']]['phase']}**\n"

        await ctx.send(response, delete_after=15)

    @commands.command(name="contribute")
    async def contribute(self, ctx, character_name: str, project_id: int, resource: str, amount: int):
        """Contribute resources to a project."""
        projects = load_json(ACTIVE_PROJECTS_FILE)
        project = projects.get(str(project_id))

        if not project or project["status"] != "active":
            await ctx.send(f"❌ Project with ID {project_id} is not active or does not exist.", delete_after=15)
            return

        inventory = load_json(f"{INVENTORY_DIR}/{character_name.lower()}.json")
        current_phase = project["phases"][project["current_phase_index"]]
        resource = resource.title()

        if resource not in current_phase["required"]:
            await ctx.send(f"❌ {resource} is not required for the current phase of project {project['name']}.",
                           delete_after=15)
            return

        actual_item = find_wildcard_match(inventory, resource)

        if not actual_item or inventory["items"].get(actual_item, 0) < amount:
            await ctx.send(f"❌ {character_name} does not have enough {resource} to contribute.", delete_after=15)
            return

        inventory["items"][actual_item] -= amount
        if inventory["items"][actual_item] <= 0:
            del inventory["items"][actual_item]

        current_phase["contributed"][resource] += amount
        project["contributors"].setdefault(character_name, []).append({"item": actual_item, "amount": amount})

        save_json(f"{INVENTORY_DIR}/{character_name.lower()}.json", inventory)
        save_json(ACTIVE_PROJECTS_FILE, projects)

        await ctx.send(
            f"✅ {character_name} contributed {amount} {actual_item} to project {project['name']} (ID: {project_id}).",
            delete_after=15)
        check_phase_completion(project_id, self.bot)

    @commands.command(name="work_on_project")
    async def work_on_project(self, ctx, character_name: str, project_id: int, hours: int):
        """Assign labor to a project (max 10 hours per command)."""
        if hours > MAX_HOURS_PER_WORK:
            await ctx.send(f"❌ You cannot work more than {MAX_HOURS_PER_WORK} hours at a time.", delete_after=10)
            return

        inventory = load_json(f"{INVENTORY_DIR}/{character_name.lower()}.json")

        if any(inventory.get(task) for task in
               ["active_crafting", "active_scavenge", "active_disassembling", "active_labor"]):
            await ctx.send(f"❌ {character_name} is already busy with another task.", delete_after=15)
            return

        projects = load_json(ACTIVE_PROJECTS_FILE)
        project = projects.get(str(project_id))

        if not project or project["status"] != "active":
            await ctx.send(f"❌ Project with ID {project_id} is not active or does not exist.", delete_after=15)
            return

        end_time = datetime.utcnow() + timedelta(hours=hours)

        inventory["active_labor"] = {
            "project_id": project_id,
            "labor_amount": hours,
            "completion_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
        }

        save_json(f"{INVENTORY_DIR}/{character_name.lower()}.json", inventory)
        await ctx.send(f"🛠️ {character_name} is now laboring on project {project_id} for {hours} hours.",
                       delete_after=15)

    @commands.command(name="check_project")
    async def check_project(self, ctx, project_id: int):
        """Check project progress and update it if the requirements are met."""
        projects = load_json(ACTIVE_PROJECTS_FILE)
        project = projects.get(str(project_id))
        if not project:
            await ctx.send(f"❌ Project with ID {project_id} does not exist.", delete_after=15)
            return

        # If the project is already completed, just report it.
        if project.get("status") == "completed":
            status_message = (
                f"**Project: {project['name']} (ID: {project['id']})**\n"
                f"Status: {project['status']}\n"
                "This project has already been completed."
            )
            await ctx.send(status_message, delete_after=15)
            return

        current_phase_index = project.get("current_phase_index", 0)
        if current_phase_index >= len(project["phases"]):
            await ctx.send(f"❌ Invalid phase index for project {project_id}.", delete_after=15)
            return

        current_phase = project["phases"][current_phase_index]
        required = current_phase.get("required", {})
        contributed = current_phase.get("contributed", {})

        # Determine the update information by checking if all requirements are met.
        if all(contributed.get(resource, 0) >= amount for resource, amount in required.items()):
            if current_phase_index + 1 < len(project["phases"]):
                project["current_phase_index"] += 1
                new_phase = project["phases"][project["current_phase_index"]]
                update_info = f"✅ Requirements met! Advancing to phase: **{new_phase['phase']}**."
            else:
                project["status"] = "completed"
                update_info = "✅ Requirements met! Project **completed**!"
            save_json(ACTIVE_PROJECTS_FILE, projects)
        else:
            update_info = "❌ Requirements are not yet met for the current phase."

        # Build the final status message.
        if project.get("status") == "completed":
            status_message = (
                f"**Project: {project['name']} (ID: {project['id']})**\n"
                f"Status: {project['status']}\n"
                "The project is complete.\n"
                f"{update_info}"
            )
        else:
            current_phase = project["phases"][project["current_phase_index"]]
            req_list = "\n".join(
                f"- {resource}: {current_phase['contributed'].get(resource, 0)}/{amount}"
                for resource, amount in current_phase.get("required", {}).items()
            )
            status_message = (
                f"**Project: {project['name']} (ID: {project['id']})**\n"
                f"Status: {project['status']}\n"
                f"Current Phase: {current_phase['phase']}\n"
                f"Requirements:\n{req_list}\n"
                f"{update_info}"
            )

        await ctx.send(status_message, delete_after=15)

    @tasks.loop(minutes=1)
    async def check_labor_completion(self):
        """Process completed labor every minute."""
        check_labor_completion(self.bot)

    @check_labor_completion.before_loop
    async def before_check_labor_completion(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(GroupProjects(bot))
