import os
import json

INVENTORY_DIR = "data/inventories/"


def get_inventory_file(character_name: str) -> str:
    """Return the file path for a character's JSON file."""
    normalized = normalize_character_name(character_name)
    file_path = os.path.join(INVENTORY_DIR, f"{normalized}.json")
    return file_path


def load_inventory(character_name):
    """Load a character's inventory, initializing it if missing."""
    inventory_file = get_inventory_file(character_name)
    if not os.path.exists(inventory_file):
        return {
            "character_name": "",
            "discord_name": "",
            "total_xp": 0,
            "total_gold": 0,
            "items": {},
            "active_crafting": None,
            "active_scavenge": None,
            "active_disassembling": None,
            "active_labor": None,
        }
    with open(inventory_file, "r") as f:
        return json.load(f)


def save_inventory(character_name: str, data: dict):
    """Save a character's data to its JSON file."""
    normalized = normalize_character_name(character_name)
    os.makedirs(INVENTORY_DIR, exist_ok=True)
    file_path = get_inventory_file(normalized)
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"[DEBUG] save_character: Successfully saved '{normalized}' to '{file_path}'")
    except Exception as e:
        print(f"[DEBUG] save_character: Error saving '{file_path}' for '{normalized}': {e}")


def normalize_character_name(name):
    """Normalize a character name by trimming whitespace and capitalizing the first letter."""
    return name.strip().lower().capitalize()


def modify_item(character, section, item_name, amount):
    """Modify the amount of an item or gold/xp in a character's section."""
    if section in ["total_gold", "total_xp"]:
        character[section] += amount
        if character[section] < 0:
            character[section] = 0  # Optional safeguard against negative values
    else:
        if section not in character:
            character[section] = {}

        if item_name not in character[section]:
            character[section][item_name] = 0

        character[section][item_name] += amount

        if character[section][item_name] <= 0:
            del character[section][item_name]
