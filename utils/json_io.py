import os
import json

RECIPES_FILE = "data/recipes.json"   # Recipes file
SCAVENGE_FILE = "data/scavenge.json"   # Scavenge loot table


def load_json(filepath):
    """Load a JSON file, returning an empty dict if it doesn't exist."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        return json.load(f)


def save_json(filepath, data):
    """Save data to a JSON file, creating directories if necessary."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def load_recipes():
    """Load crafting recipes."""
    if not os.path.isfile(RECIPES_FILE):
        return {}
    with open(RECIPES_FILE, "r") as f:
        return json.load(f)


def load_scavenge_table():
    """Load the scavenge loot table (grouped by resource type)."""
    if not os.path.isfile(SCAVENGE_FILE):
        return {}
    with open(SCAVENGE_FILE, "r") as f:
        return json.load(f)
