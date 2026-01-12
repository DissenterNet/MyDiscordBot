---

# **🧑‍💼 Character Management Commands Guide**

---

## **🌱 \!life \<character\_name\>**

**Description:**  
 Create a **new character** with the specified name.

**Usage:** \!life Taco

### **How it Works:**

* The **character name is case-insensitive** and normalized (e.g., "Taco" and "taco" are treated the same).  
* **Creates a new inventory JSON** for the character based on a template.  
* **Locks the character** to the **Discord user** who created it.  
* **Prevents creation** if:  
  * The **character already exists**.  
  * The **user already owns 10 characters**.

### **Example Output:**

✅ Character Taco has been created and is linked to \[Discord Username\].

---

## **💀 \!death \<character\_name\>**

**Description:**  
 **Deletes a character’s inventory file**, effectively **killing** the character and freeing up a slot for a new character for the user.

**Usage:** \!death Taco

### **How it Works:**

* Can **only be executed by**:  
  * **The character's owner**.  
  * **The Discord server owner**.  
* **Posts a message with 👍 and 👎 reactions**.  
* **Deletes the character only if**:  
  * The **owner reacts with 👍**.  
  * **Deletes the confirmation message** after **👍, 👎, or 30 seconds**.

### **Example Output:**

☠️ Are you sure you want to kill Taco? React with 👍 to confirm or 👎 to cancel.

---

## **⚠️ Important Notes:**

* **Each user is limited to 10(for now) characters.**  
* **Character names are case-insensitive** but are stored with **the first letter capitalized**.

---

## **📅 `!availability` Commands Guide**

The `!availability` commands allow players to schedule their availability for game sessions, remove availability, and check their scheduled times.

---

### **🔹 `!availability add`**

**📌 Description:**  
This command adds a new availability entry for a player with a specified date and time range. The first time you use it, the bot will ask for your UTC timezone offset (e.g., \-5 for East Coast USA, \-8 for West Coast). This helps the bot store your local time for adding, removing, and viewing availability without manual calculations. The bot now also supports availability windows that span multiple days, such as \!availability add 2025-04-20 0420 0420, which sets your availability from 4:20 AM on 4-20-2025 to 4:20 AM on 4-21-2025.

**📜 Usage:**

\!availability add \<Date\> \<Start Time\> \<End Time\>

🔹 This means you are available on **February 15, 2025**, from **6:00 PM to 10:00 PM**.

**📋 Copy-Paste Template:**

\!availability add \<YYYY-MM-DD\> \<HH:MM\> \<HH:MM\>

*(Replace `<YYYY-MM-DD>` with the date and `<HH:MM>` with the time in 24-hour format.)*

---

### **🔹 `!availability remove`**

**📌 Description:**  
 This command removes a scheduled availability entry using a unique identifier (UUID). You can find the UUID by using `!availability list`.

**📜 Usage:**

\!availability remove \<UUID\>

*(Replace `<UUID>` with the unique identifier of the availability entry.)*

**✅ Example:**

\!availability remove 123e4567-e89b-12d3-a456-426614174000

🔹 This removes the specific availability entry associated with the given **UUID**.

---

### **🔹 `!availability list`**

**📌 Description:**  
 Displays a list of all scheduled availability entries for the user.

🔹 This will return a list of all availability times you have set, along with their corresponding **UUIDs**.

**📋 Copy-Paste Template:**

\!availability list  
---

### **💡 Notes**

* **Time Format:** The bot uses a 24-hour format and UTC for input times.  
  * ✅ **Correct:** `18:00` (6:00 PM)  
  * ❌ **Incorrect:** `6:00PM` (Use `18:00` instead)  
* **Date Format:** Use the standard **YYYY-MM-DD** format.  
  * ✅ **Correct:** `2025-02-15`  
  * ❌ **Incorrect:** `15/02/2025`  
* **Finding the UUID:**  
  * Use `!availability list` to view all scheduled times and their corresponding **UUIDs**.  
  * Use the UUID when removing a specific entry.

---

### **🎯 Quick Summary**

| Command | Description | Example |
| ----- | ----- | ----- |
| `!availability add <Date> <Start> <End>` | Adds availability | `!availability add 2025-02-15 18:00 22:00` |
| `!availability remove <UUID>` | Removes an entry | `!availability remove 123e4567-e89b-12d3-a456-426614174000` |
| `!availability list` | Shows all scheduled availability | `!availability list` |

---

# **🛠️ `!craft` Command Guide**

The `!craft` command allows players to craft items using materials in their inventory. Below are detailed instructions for using all crafting-related commands.

---

## **🔹 `!craft`**

**📌 Description:**  
 This command allows a character to start crafting an item, as long as they have the required materials and tools in their inventory.

**📜 Usage:**

\!craft \<Character Name\> \<Item Name\>

**✅ Example:**

\!craft Taco Wooden Mallet

🔹 This command makes the character **Taco** start crafting a **Wooden Mallet**, assuming they have the necessary materials.

**📋 Copy-Paste Template:**

\!craft \<YourCharacterName\> \<ItemName\>

*(Replace `<YourCharacterName>` with your character’s name and `<ItemName>` with the item you want to craft.)*

---

## 

## 

## 

## **🔹 `!crafting status WIP`**

**📌 Description:**  
 Checks the progress of an ongoing crafting task for a character.

**📜 Usage:**

\!crafting status \<Character Name\>

🔹 This command checks what **Taco** is currently crafting and how much time is left.

**📋 Copy-Paste Template:**

\!crafting status \<YourCharacterName\>

*(Replace `<YourCharacterName>` with your character’s name.)*

---

## **🔹 `!crafting cancel WIP`**

**📌 Description:**  
 Cancels an active crafting task for a character. **This will NOT refund materials**.

**📜 Usage:**

\!crafting cancel \<Character Name\>

🔹 This cancels **Taco’s** current crafting task.

**📋 Copy-Paste Template:**

\!crafting cancel \<YourCharacterName\>

*(Replace `<YourCharacterName>` with your character’s name.)*

---

## 

## **💡 Important Notes**

* **Crafting Time:** Most items take time to craft. You can check progress with `!crafting status`.  
* **Materials & Tools:**  
  * You must have **all required materials and tools** in your inventory.  
  * Missing components will prevent crafting from starting.  
* **Canceling Crafting:**  
  * **Cancelling does NOT return materials**.  
  * Use carefully to avoid wasting resources.

---

## **🎯 Quick Summary**

| Command | Description | Example |
| ----- | ----- | ----- |
| `!craft <Character Name> <Item Name>` | Starts crafting an item | `!craft Taco Wooden Mallet` |
| `!crafting status <Character Name>` | Checks crafting progress | `!crafting status Taco` |
| `!crafting cancel <Character Name>` | Cancels an active crafting task | `!crafting cancel Taco` |

---

# 

# 

# 

# 

# **🛠️ `!disassemble` Command Guide**

The `!disassemble` command allows players to break down items into their base components. Some components may have a chance to break, and if they do, they will be replaced using data from `broken.json`.

---

## **🔹 `!disassemble`**

**📌 Description:**  
 This command starts the disassembly of an item, returning its original crafting components based on the **reverse of the crafting recipe**.

**📜 Usage:**

\!disassemble \<Character Name\> \<Item Name\>

**✅ Example:**

\!disassemble Taco Wooden Mallet

🔹 This command makes the character **Taco** start disassembling a **Wooden Mallet**.

**📋 Copy-Paste Template:**

\!disassemble \<YourCharacterName\> \<ItemName\>

*(Replace `<YourCharacterName>` with your character’s name and `<ItemName>` with the item you want to break down.)*

---

## 

## 

## **🔹 `!disassembling status WIP`**

**📌 Description:**  
 Checks the progress of an ongoing disassembly task for a character.

**📜 Usage:**

\!disassembling status \<Character Name\>

🔹 This command checks what **Taco** is currently disassembling and how much time is left.

**📋 Copy-Paste Template:**

\!disassembling status \<YourCharacterName\>

*(Replace `<YourCharacterName>` with your character’s name.)*

---

## **🔹 `!disassembling cancel WIP`**

**📌 Description:**  
 Cancels an active disassembly task for a character. **This will NOT return the item being disassembled**.

**📜 Usage:**

\!disassembling cancel \<Character Name\>

🔹 This cancels **Taco’s** current disassembly task.

**📋 Copy-Paste Template:**

\!disassembling cancel \<YourCharacterName\>

*(Replace `<YourCharacterName>` with your character’s name.)*

---

## **💡 Important Notes**

* **Reversed Crafting:**  
  * Disassembly follows the **reverse** of the crafting recipe.  
  * Outputs become components, and components become outputs.  
* **Chance of Breaking Components:**  
  * Some components may **break** when disassembled.  
  * If a component breaks, it is replaced using **`broken.json`**.  
* **Disassembly Time:**  
  * Similar to crafting, some items take time to disassemble.  
  * Check progress using `!disassembling status`.  
* **Canceling Disassembly:**  
  * **Canceling does NOT return the original item**.  
  * Use carefully to avoid losing resources.

---

## **🎯 Quick Summary**

| Command | Description | Example |
| ----- | ----- | ----- |
| `!disassemble <Character Name> <Item Name>` | Starts disassembling an item | `!disassemble Taco Wooden Mallet` |
| `!disassembling status <Character Name>` | Checks disassembly progress | `!disassembling status Taco` |
| `!disassembling cancel <Character Name>` | Cancels an active disassembly task | `!disassembling cancel Taco` |

---

# 

# **🎭 `!rp` (Roleplay) Command Guide**

The `!rp` command allows players to send roleplay messages as their characters. It also includes the `!setavatar` command to set a custom character avatar.

---

## **🔹 `!rp`**

**📌 Description:**  
 This command allows a character to send a roleplay message in the chat. The message will be displayed as if it came from the character.

**📜 Usage:**

\!rp \<Character Name\> \<Message\>

**✅ Example:**

\!rp Taco The forest is dense and quiet... too quiet.

🔹 This makes the character **Taco** send the message:  
 `Taco: “The forest is dense and quiet... too quiet.”`

**📋 Copy-Paste Template:**

\!rp \<YourCharacterName\> \<YourMessage\>

*(Replace `<YourCharacterName>` with your character’s name and `<YourMessage>` with your roleplay text.)*

---

## 

## 

## **🔹 `!emote`**

**📌 Description:**  
 Sends a roleplay action/emote instead of dialogue.

**📜 Usage:**

\!emote \<Character Name\> \<Action\>

**✅ Example:**

\!emote Taco draws his sword, ready for battle.

🔹 This makes the character **Taco** display the action as:  
 `*Taco draws his sword, ready for battle.*`

**📋 Copy-Paste Template:**

\!emote \<YourCharacterName\> \<YourAction\>

*(Replace `<YourCharacterName>` with your character’s name and `<YourAction>` with the action you want to perform.)*

---

## 

## 

## 

## 

## 

## **🔹 `!setavatar`**

**📌 Description:**  
 Sets a custom avatar image for a character. The avatar will be displayed whenever the character speaks using `!rp`.

**📜 Usage:**

\!setavatar \<Character Name\> \<Image URL\>

**✅ Example:**

\!setavatar Taco https://example.com/taco-avatar.png

🔹 This sets **Taco’s** avatar to the image at the provided URL.

**📋 Copy-Paste Template:**

\!setavatar \<YourCharacterName\> \<ImageURL\>

*(Replace `<YourCharacterName>` with your character’s name and `<ImageURL>` with a valid image link.)*

---

## 

## 

## 

## 

## 

## **💡 Important Notes**

* **Roleplay messages appear as if they are spoken by the character.**  
* **Emotes (`!emote`)** allow for actions rather than dialogue.  
* **Avatars must be valid image URLs** (ending in `.png`, `.jpg`, or `.gif`).  
* **If no avatar is set**, the character will display messages without an image.

---

## **🎯 Quick Summary**

| Command | Description | Example |
| ----- | ----- | ----- |
| `!rp <Character Name> <Message>` | Sends a roleplay message | `!rp Taco The wind howls...` |
| `!rp emote <Character Name> <Action>` | Sends a roleplay action/emote | `!emote Taco sharpens his blade.` |
| `!setavatar <Character Name> <Image URL>` | Sets a character’s avatar | `!setavatar Taco https://example.com/avatar.png` |

---

# 

# 

# 

# **🔎 `!scavenge` Command Guide**

The `!scavenge` command allows players to search for resources in the environment. Players can either scavenge **generally** for random materials or **specifically** for a certain resource type.

---

## **🔹 `!scavenge`**

**📌 Description:**  
 Initiates a **scavenging** attempt that lasts **1 hour**. Players can choose to scavenge **randomly** or **target** a specific resource type.

**📜 Usage:**

\!scavenge \<Character Name\> \[Resource Type\]

* **General Scavenging:**  
  * `!scavenge <Character Name>` → 10 rolls, 50% chance per roll to find an item.  
* **Specific Resource Scavenging:**  
  * `!scavenge <Character Name> <Resource Type>` → 5 rolls, 50% chance per roll to find an item.

🔹 This makes the character **Taco** scavenge for **random materials**.

\!scavenge Taco wood

🔹 This makes **Taco** scavenge **specifically for wood**.

**📋 Copy-Paste Template:**

\!scavenge \<YourCharacterName\> \[ResourceType\]

*(Replace `<YourCharacterName>` with your character’s name. Optionally, replace `[ResourceType]` with a specific resource.)*

---

## **🔹 `!scavenge status WIP`**

**📌 Description:**  
 Checks if a character is currently scavenging and how much time is left.

**📜 Usage:**

\!scavenge status \<Character Name\>

**✅ Example:**

\!scavenge status Taco

🔹 This checks **Taco’s** scavenging progress.

**📋 Copy-Paste Template:**

\!scavenge status \<YourCharacterName\>

*(Replace `<YourCharacterName>` with your character’s name.)*

---

## 

## 

## 

## 

## 

## 

## **🔹 `!scavenge cancel WIP`**

**📌 Description:**  
 Cancels an **active scavenging task**. **This will NOT return the lost time**.

**📜 Usage:**

\!scavenge cancel \<Character Name\>

**✅ Example:**

\!scavenge cancel Taco

🔹 This cancels **Taco’s** scavenging.

**📋 Copy-Paste Template:**

\!scavenge cancel \<YourCharacterName\>

*(Replace `<YourCharacterName>` with your character’s name.)*

---

## 

## 

## 

## 

## 

## 

## **💡 Important Notes**

* **Scavenging takes 1 hour** to complete.  
* **General scavenging rolls 10 times** (each roll has a 50% chance of finding an item).  
* **Targeted scavenging rolls 5 times** (each roll has a 50% chance of finding an item from the specified category).  
* **Cancelling scavenging does NOT refund time**.  
* **A character can only scavenge if they are not crafting or disassembling**.

---

## **🎯 Quick Summary**

| Command | Description | Example |
| ----- | ----- | ----- |
| `!scavenge <Character Name>` | Starts general scavenging | `!scavenge Taco` |
| `!scavenge <Character Name> <Resource Type>` | Starts targeted scavenging | `!scavenge Taco wood` |
| `!scavenge status <Character Name>` | Checks scavenging progress | `!scavenge status Taco` |
| `!scavenge cancel <Character Name>` | Cancels an active scavenging task | `!scavenge cancel Taco` |

---

# 

# 

Here’s a clear and updated guide for the **Session Cog Commands (`session.py`)** based on your current and refactored version:

---

## **📜 Session Commands Guide**

These commands manage your characters’ stats, track their progress, and view inventories.

### **📝 \!session \<session\_id\> \<character\_name\> \<xp\_gained\> \<gold\_earned\>**

**Description:**  
 Log an adventure session, updating your character’s XP and gold.  
 **Usage:**

\!session 001 Taco 500 300 50

**Effect:**

* Adds `500 XP` to **Taco**.  
* Adds `300 gold` and subtracts `50 gold` (expenses), netting `+250 gold`.  
* The session is logged with the `session_id` ("001").  
* Posts a summary to the channel and a bookkeeping channel (if configured).

---

### 

### **📊 \!stats**

**Description:**  
 View a summary of all your characters' XP and Gold.  
 **Usage:**

\!stats

**Effect:**

* Lists all characters you own and their current XP and Gold.

Example Output:  
 Your Characters:

Taco: XP: 500, Gold: 250

Burrito: XP: 1200, Gold: 900

* 

---

### **📦 \!inventory**

**Description:**  
 Receive a **full inventory list in DM** (split into multiple messages if necessary).  
 **Usage:** **\!inventory \<character\_name\>**

**Effect:**

* Sends the character’s inventory via **direct message**.  
* Splits into multiple messages **if the inventory is too large** (Discord's 2000-character limit).

**Note:**  
 If your **DMs are closed**, the bot will notify you.

* Character names are **case-insensitive**, but are normalized to `Capitalized` when displayed.  
* Items in inventories are **sorted alphabetically** for easier reading.

---

# **🏗 Group Projects Commands Guide**

Group projects are large-scale community tasks requiring players to **contribute materials and labor** toward a common goal. Projects progress **through multiple phases**, and each phase may require different resources.

---

## **🆕 \!start\_project \<project\_type\>**

**Description:**  
 Start a new group project based on a project type from `projects.json`. **Only available to the GM and eventually a character to be chosen by the players as project manager.**

**Usage:**

\!start\_project gravel\_road

* Starts a **Gravel Road** project if it exists in the `projects.json` file.  
* Each project progresses through **multiple phases** with different resource and labor requirements.

**Example Output:**

✅ Project Gravel Road (ID: 1\) has been started\!

---

## **📜 \!list\_projects**

**Description:**  
 List all **active group projects** and their current phases.

**Usage:**

\!list\_projects

**Example Output:**

🛠️ Active Projects:

\- Gravel Road (ID: 1), Phase: Gather Gravel

---

## **🪵 \!contribute \<character\_name\> \<project\_id\>**

**Description:**  
 Contribute **resources** from your character’s inventory to the project’s current phase.

**Usage:** \!contribute Taco 1 gravel 50

**Requirements:**

* Your character must have **the specified resource** in their inventory.  
* Contributions count **toward the current phase** of the project.

**Wildcard Matching:**

* Projects may have requirements like `* Planks`, meaning **any resource starting with "wood"** (e.g., `Oak Planks`, `Cedar Planks`) will contribute.

**Example Output:**

✅ Taco contributed 50 gravel to project Gravel Road (ID: 1).

---

## **👷 \!work\_on\_project \<character\_name\> \<project\_id\>**

**Description:**  
 Assign your character to **work (labor)** on a project for a specified number of hours.

**Usage:**

\!work\_on\_project Taco 1 4

**Requirements:**

* The character **must not be crafting, scavenging, disassembling, or laboring** on another task.  
* Labor is required in some project phases (e.g., “Lay Road”).

**Example Output:**

🔨 Taco is now laboring on project 1 for 4 hours.

* Once labor is complete, it contributes **the hours worked** to the project’s labor requirement.

---

## **🔍 \!check\_project \<project\_id\>**

**Description:**  
 Check the **progress and requirements** of a specific project phase.

**Usage:** \!check\_project 1

**Example Output:**

Project: Gravel Road (ID: 1\)

Status: active

Current Phase: Gather Gravel

Requirements:

\- gravel: 50/100

---

## **🔄 Project Phase & Completion Handling**

* **Phases automatically advance** when **all resource and labor requirements are met**.  
* When the **final phase is completed**, the project status becomes **"completed"**.

---

## **⚠️ Important Notes:**

* **Character Activity Lock:**  
   A character **cannot work on a project** if they are already:  
  * Crafting  
  * Scavenging  
  * Disassembling  
  * Laboring on another project  
* **Case Insensitive:**  
   All commands and inputs for projects, resources, and characters **are case-insensitive**.

---

