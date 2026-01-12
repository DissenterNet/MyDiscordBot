



Below is a detailed cheat sheet that explains how to format your recipes JSON to model real-life crafting and processing as closely as possible. This guide covers each field, when to use a string versus an array, and practical examples. Use this as a reference when adding or editing recipes.

---

# Recipe JSON Cheat Sheet

Your recipes JSON is structured by categories. Each category (like `"wood_processing"`, `"stone_processing"`, etc.) is an object containing one or more recipe definitions. Each recipe is itself an object with various keys that control its behavior.

## Top-Level Structure

- **Categories:**  
    The top-level object contains different categories for your recipes.  
    **Example:**
    
    ```json
    {
      "wood_processing": { ... },
      "stone_processing": { ... },
      "tool_crafting": { ... }
    }
    ```
    

## Recipe Object Fields

Each recipe in a category can have the following keys:

### 1. **components**

- **Type:** Object
- **Purpose:** Lists the required materials (components) and the amounts needed.
- **Wildcard Use:** You can include an asterisk (`*`) as a prefix to denote that any item matching the name can be used.
- **Example:**
    
    ```json
    "components": { "* Log": 1 }
    ```
    
    This means you need one log (of any type that includes "Log" in its name).

### 2. **quantity**

- **Type:** Number
- **Purpose:** Specifies the number of items produced by this recipe.
- **When to Use:** Use this field if the crafting process produces multiple units at once.
- **Example:**
    
    ```json
    "quantity": 4
    ```
    
    This means the recipe yields 4 of the finished product.

### 3. **requires**

- **Type:** String or Array
- **Purpose:** Indicates the tools or additional items required to execute the recipe.
- **When to Use a String:**
    - If there is only one required tool and you don’t need to list multiple options.
    - **Caution:** A string may be mistakenly processed as an iterable of characters by some code, so if there’s any chance of multiple tools or wildcards, use an array.
- **When to Use an Array:**
    - When you have multiple tools or when using wildcard syntax is important.
- **Examples:**
    - **As a String (simple case):**
        
        ```json
        "requires": "* Axe"
        ```
        
    - **As an Array (recommended for multiple options or to avoid issues):**
        
        ```json
        "requires": ["* Axe"]
        ```
        
    - **Multiple Tool Options:**
        
        ```json
        "requires": ["* Knife", "* Sword", "* Axe"]
        ```
        The array format ensures that each entry is treated as a full tool name rather than as individual characters.

### 4. **time**

- **Type:** Number
- **Purpose:** Represents the time required to complete the crafting process (typically in minutes).
- **Example:**
    
    ```json
    "time": 1
    ```
    

### 5. **disassemble**

- **Type:** Number
- **Purpose:** Indicates whether the crafted item can be disassembled. Conventionally, `1` means yes, and `0` means no.
- **Example:**
    
    ```json
    "disassemble": 1
    ```
    

### 6. **outputs**

- **Type:** Array
- **Purpose:** Specifies the byproducts or outputs you receive upon completing the recipe. This allows you to model situations like getting leftover material.
- **Structure:** Each entry in the array is an object with two keys:
    - **item:** The name of the output item.
    - **quantity:** The number of that item produced.
- **Example:**
    
    ```json
    "outputs": [
      { "item": "Wood Planks", "quantity": 4 },
      { "item": "Fibrous Material", "quantity": 5 }
    ]
    ```
    

---

## Complete Example

Below is an example that combines all of the fields:

```json
{
  "wood_processing": {
    "Wood Planks": {
      "components": { "* Log": 1 },
      "quantity": 4,
      "requires": ["* Axe"],
      "time": 1,
      "disassemble": 1,
      "outputs": [
        { "item": "Wood Planks", "quantity": 4 },
        { "item": "Fibrous Material", "quantity": 5 }
      ]
    },
    "Wooden Beams": {
      "components": { "* Log": 1 },
      "quantity": 1,
      "requires": ["* Axe"],
      "time": 1
    }
  },
  "stone_processing": {
    "Stone Axe": {
      "components": {
        "Rock": 1,
        "* Branch": 1,
        "Cordage": 5
      },
      "requires": ["*"],
      "time": 1,
      "disassemble": 1,
      "outputs": [
        { "item": "Fibrous Material", "quantity": 50 }
      ]
    },
    "Stone Knife": {
      "components": {
        "Rock": 1,
        "* Branch": 1,
        "Cordage": 5
      },
      "quantity": 1,
      "requires": ["0"],
      "time": 1,
      "disassemble": 1
    }
  },
  "tool_crafting": {
    "Wooden Mallet": {
      "components": { "* Branch": 1, "* Log": 1 },
      "quantity": 1,
      "requires": ["* Knife", "* Sword", "* Axe"],
      "time": 1
    }
  }
}
```

---

## Tips for Novices

- **JSON Basics:**  
    JSON is a text format that uses key-value pairs. Keys must be strings (enclosed in double quotes), and values can be strings, numbers, arrays, objects, booleans, or null.
    
- **Arrays vs. Strings:**
    
    - Use **arrays** (`[...]`) when you need to list multiple items. For example, if you have more than one tool requirement, an array prevents accidental splitting into individual characters.
    - Use **strings** (`"..."`) when you have a single item and are sure that it won’t be misinterpreted by your code. However, if there's any risk of misinterpretation (especially with wildcards), lean toward using an array.
- **Wildcards:**  
    To allow flexibility (for example, letting any type of axe be used), prefix the item with an asterisk (`*`). Your code should then interpret this as a wildcard match.  
    **Example:** `"* Axe"` can match `"Stone Axe"`, `"Fireman's Axe"`, etc.
    
- **Validation:**  
    Always validate your JSON using a tool like [JSONLint](https://jsonlint.com/) to ensure there are no syntax errors (e.g., missing commas, mismatched braces).
    
- **Consistency:**  
    Keep your naming consistent. For example, if you use `"Wood Planks"` in one recipe, don't accidentally use `"wood planks"` or `"WoodPlanks"` in another. JSON keys are case-sensitive.
    
- **No Comments in JSON:**  
    JSON doesn’t support comments. If you need notes, keep a separate documentation file.
    
- **Testing:**  
    Test your recipes in small increments. Start with a basic recipe, ensure it works, and then add more fields or complexity.
    

---

Below is an explanation of how you can model a recipe that requires a tool from a set of alternatives (for example, any one of ∗Axe,∗Knife,∗Sword* Axe, * Knife, * Sword) in addition to a fixed tool (like a Workbench). This approach uses nested arrays in the `"requires"` field so that you can specify “OR” requirements within one group and “AND” requirements between groups.

---

## Using Nested Arrays in the `"requires"` Field

### The Concept

- **Single Tool Requirement (AND):**  
    A simple string or array element means that tool must be present.  
    **Example:**
    
    ```json
    "requires": "Workbench"
    ```
    
    or
    
    ```json
    "requires": ["Workbench"]
    ```
    
    Both indicate that a Workbench is required.
    
- **Alternative Tool Requirement (OR):**  
    When you want to allow for multiple options (i.e. any one of several tools will work), you can nest an array inside the main `"requires"` array.  
    **Example:**
    
    ```json
    "requires": [
        ["* Axe", "* Knife", "* Sword"],
        "Workbench"
    ]
    ```
    
    This means that to craft the item, the character must have:
    
    - **At least one tool** that matches any of the wildcards `"* Axe"`, `"* Knife"`, or `"* Sword"`, **AND**
    - A **Workbench**.

### How It Works

- When your crafting code processes the `"requires"` field, it should:
    1. **Loop over each element** in the `"requires"` array.
    2. **If the element is a nested array:**
        - Check that **at least one** of the tools listed in that nested array is present in the player's inventory.
    3. **If the element is a string:**
        - Check that the required tool (or item) is present.
- This structure lets you model real-life scenarios where a task can be performed using multiple different tools that serve the same function.

### Example Recipe JSON

Below is an example of a recipe that requires the player to have either an axe, knife, or sword (using wildcards) along with a workbench:

```json
{
  "construction": {
    "Paper Cutting": {
      "components": { "Paper": 10 },
      "quantity": 1,
      "requires": [
        ["* Axe", "* Knife", "* Sword", "* Scissors", "* Razor Blade"],
        "Workbench"
      ],
      "time": 1,
      "disassemble": 0,
      "outputs": [
        { "item": "Cut Paper", "quantity": 1 }
      ]
    }
  }
}
```

In this recipe:

- The `"components"` field requires 10 Paper.
- The `"requires"` field is a nested array:
    - The **first element** is an array of alternatives: the player must have **at least one** tool that matches any of `"* Axe"`, `"* Knife"`, `"* Sword"`, `"* Scissors"`, or `"* Razor Blade"`.
    - The **second element** is the string `"Workbench"`, which means the player must also have a Workbench.
- The `"time"`, `"disassemble"`, and `"outputs"` fields are used as described earlier.

---

## Tips for a Novice

- **Use Arrays for Flexibility:**  
    When there is any possibility of multiple acceptable tools (even if it’s just one option now), use an array (or nested array) so that your code can iterate over all options. This prevents accidental processing of a string as individual characters.
    
- **Nested Arrays for Alternatives:**  
    Use nested arrays when you need to specify "any one of these tools will work." This makes the intention explicit:
    
    - Outer array elements represent independent requirements (AND).
    - Inner arrays represent alternative choices for that requirement (OR).
- **Consistency:**  
    Always use consistent casing and spacing. For instance, if you use `"* Axe"` in one recipe, do not mix it with `"*axe"` elsewhere unless you intentionally want different matching behavior.
    
- **Validation:**  
    Use a JSON validator (such as [JSONLint](https://jsonlint.com/)) to ensure your JSON is correctly formatted before using it in your bot.
    
- **Updating Your Code:**  
    Ensure your code that checks tool requirements is updated to handle nested arrays. Pseudocode for processing the `"requires"` field might look like:
    
    ```python
    def check_requirements(inventory, requirements):
        for req in requirements:
            if isinstance(req, list):
                # At least one of the alternatives must be present
                if not any(tool in inventory["items"] for tool in req):
                    return False
            else:
                if req not in inventory["items"]:
                    return False
        return True
    ```
    

