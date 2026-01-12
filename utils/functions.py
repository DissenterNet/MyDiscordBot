import os
from datetime import datetime
from utils.json_io import load_json, save_json

PROJECTS_FILE = "data/projects.json"
ACTIVE_PROJECTS_FILE = "data/active_projects.json"


def get_next_project_id(projects):
    """Determine the next available project ID."""
    numeric_ids = [int(pid) for pid in projects.keys() if pid.isdigit()]
    return max(numeric_ids, default=0) + 1


def check_phase_completion(project_id, bot):
    """Check if a project phase or project itself is complete."""
    projects = load_json(ACTIVE_PROJECTS_FILE)
    project = projects.get(str(project_id))

    if not project:
        print(f"[DEBUG] Project {project_id} not found.")
        return

    # If the project is already completed, nothing more to do.
    if project.get("status") == "completed":
        print(f"[DEBUG] Project {project_id} is already completed.")
        return

    current_phase_index = project.get("current_phase_index", 0)
    phases = project.get("phases", [])

    # Check that the current phase index is valid.
    if current_phase_index >= len(phases):
        print(f"[DEBUG] Invalid current_phase_index {current_phase_index} for project {project_id}.")
        return

    current_phase = phases[current_phase_index]
    required = current_phase.get("required", {})
    contributed = current_phase.get("contributed", {})

    # Debug output to show what's being checked.
    print(
        f"[DEBUG] Project {project_id} Phase {current_phase_index} - Required: {required}, Contributed: {contributed}")

    # Check if every required resource has been met.
    phase_complete = all(contributed.get(resource, 0) >= amount for resource, amount in required.items())

    if phase_complete:
        # If there is another phase, advance to it.
        if current_phase_index + 1 < len(phases):
            project["current_phase_index"] += 1
            print(f"[DEBUG] Project {project_id} advanced to phase {project['current_phase_index']}.")
        else:
            # No further phases: mark the project as completed.
            project["status"] = "completed"
            print(f"[DEBUG] Project {project_id} is now completed.")
            channel = bot.get_channel(1333893155661021266)  # COMPLETED_PROJECTS_CHANNEL
            if channel:
                bot.loop.create_task(
                    channel.send(
                        f"🎉 Project **{project['name']}** (ID: {project_id}) is **COMPLETED**!\nReward: {project['reward']}"
                    )
                )
            else:
                print(f"[DEBUG] Could not get channel for project completion announcement.")
    else:
        print(f"[DEBUG] Project {project_id} Phase {current_phase_index} requirements not yet met.")

    save_json(ACTIVE_PROJECTS_FILE, projects)


def check_labor_completion(bot):
    """Process completed labor, update project contributions, and advance/complete project phases."""
    now = datetime.utcnow()
    active_projects = load_json(ACTIVE_PROJECTS_FILE)

    for filename in os.listdir("data/inventories/"):
        if not filename.endswith(".json"):
            continue

        character_name = filename[:-5]  # Extract character name from filename
        inventory = load_json(f"data/inventories/{filename}")

        if not inventory.get("active_labor"):
            continue

        try:
            completion_time = datetime.strptime(
                inventory["active_labor"]["completion_time"], "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            print(f"[DEBUG] Incorrect datetime format in {filename}.")
            continue  # Skip if there's a formatting issue

        if now >= completion_time:
            project_id = str(inventory["active_labor"]["project_id"])
            labor_amount = inventory["active_labor"]["labor_amount"]

            if project_id in active_projects:
                project = active_projects[project_id]
                current_phase_index = project.get("current_phase_index", 0)
                phase = project["phases"][current_phase_index]

                # Update labor contributions
                phase["contributed"]["labor"] = phase["contributed"].get("labor", 0) + labor_amount

                # Track the character's labor contribution
                project["contributors"].setdefault(character_name, []).append(
                    {"item": "labor", "amount": labor_amount}
                )

                # Check if the current phase's requirements are met
                required = phase.get("required", {})
                contributed = phase.get("contributed", {})
                phase_complete = all(
                    contributed.get(resource, 0) >= amount for resource, amount in required.items()
                )

                if phase_complete:
                    if current_phase_index + 1 < len(project["phases"]):
                        project["current_phase_index"] += 1
                        print(f"[DEBUG] Project {project_id} advanced to phase {project['current_phase_index']}.")
                    else:
                        project["status"] = "completed"
                        print(f"[DEBUG] Project {project_id} is now completed.")
                        channel = bot.get_channel(1333893155661021266)  # COMPLETED_PROJECTS_CHANNEL
                        if channel:
                            bot.loop.create_task(
                                channel.send(
                                    f"🎉 Project **{project['name']}** (ID: {project_id}) is **COMPLETED**!\nReward: {project['reward']}"
                                )
                            )
                        else:
                            print(f"[DEBUG] Could not find the completed projects channel.")

            # Reset the active labor for the character
            inventory["active_labor"] = None
            save_json(f"data/inventories/{filename}", inventory)
            save_json(ACTIVE_PROJECTS_FILE, active_projects)

            print(f"[DEBUG] {character_name} completed {labor_amount} hours of labor on project {project_id}.")


def find_wildcard_match(inventory, required_item):
    """Find a matching item in inventory for wildcard tools or components.

    If the required_item contains an asterisk (*), it is treated as a wildcard.
    For example, '* Axe' or 'Axe *' will return the first inventory item whose name contains 'axe'.
    """
    if "*" in required_item:
        base_name = required_item.replace("*", "").strip().lower()

        # If wildcard is at the beginning (before base_name) or the end (after base_name)
        for item in inventory["items"]:
            item_lower = item.lower()

            if required_item.startswith("*"):  # Wildcard before the base name
                if item_lower.endswith(base_name):
                    return item
            elif required_item.endswith("*"):  # Wildcard after the base name
                if item_lower.startswith(base_name):
                    return item
            else:  # Wildcard anywhere in the string (before and after)
                if base_name in item_lower:
                    return item
    return required_item  # Return original item if no wildcard or no match


def normalize_components(components):
    """
    Convert components to a dict if it's a list.
    E.g., ["* Log"] becomes {"* Log": 1}.
    """
    if isinstance(components, list):
        return {comp: 1 for comp in components}
    return components
