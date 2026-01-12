
## main.py

- [x] ✅
- [ ] move_item cant move two word items
- [ ] add case insensitivity to !contribute for group projects
- [x] set limit to how long a character can labor in work_on_project for group projects
- [ ] investigate !life in the management cog to align the two templates line 10 V line 90
- [ ] Fix !scavenge to not allow a character name that doesn't exist scavenge
- [ ] Add rewards for donations to group projects
- [ ] Write code to allow players with a spell to add it to others spell books for free or for profit.
- [ ] Find way to avoid duplicating the subclasses for all the different classes.
- [ ] Clue: Historic sites of shadow attacks during the fall stopped when reaching a field of some sort. The characters could Discover the origin point at the center of the field.


## availability.py

- [x] ✅


## commands.py

- [x] ✅


## crafting.py

- [x] ✅


## disassemble.py

- [x] ✅


## group_projects.py

- [ ] ✅


## honor.py

- [x] ✅


## rollplay.py

- [x] ✅
- [x] Send image to random DM


## scavenge.py

- [x] ✅


## session.py

- [ ] ✅


## trading.py

- [x] ✅



## .JSONs

### recipes.json

- [ ] ✅


### scavenge.json

- [ ] ✅


### broken.json

- [ ] ✅


### projects.json

- [ ] ✅



Sure thing! Here's a **brief guide** on how to **run and manage your Discord bot with `pm2`**:

---

## **Running and Managing Your Discord Bot with pm2**

### **1. Install pm2 (If You Haven't)**

Open a terminal and install pm2 globally:

```bash
npm install -g pm2
```

### **2. Navigate to Your Bot Folder**

Open your terminal and navigate to your bot’s project folder:

```bash
cd C:\Users\Stev\PycharmProjects\ADVbot
```

### **3. Start the Bot with pm2**

Start your bot using pm2:

```bash
pm2 start main.py --name "my-discord-bot" --interpreter python
```

- `main.py`: Your bot’s main Python file.
- `--name "my-discord-bot"`: Optional name for easier management.
- `--interpreter python`: Specifies Python as the interpreter.

### **4. Check the Bot’s Status**

View your bot’s status:

```bash
pm2 list
```

You should see your bot with the **status "online"**.

### **5. View Logs**

Check the bot’s output logs:

```bash
pm2 logs my-discord-bot
```

Stop viewing logs by pressing `Ctrl + C`.

### **6. Restart the Bot**

Restart your bot:

```bash
pm2 restart my-discord-bot
```

### **7. Stop the Bot**

Stop the bot but keep it in pm2:

```bash
pm2 stop my-discord-bot
```

### **8. Delete the Bot (Remove from pm2)**

Remove the bot completely from pm2:

```bash
pm2 delete my-discord-bot
```

### **9. Automatically Start on Reboot (Optional)**

If you want your bot to **start automatically when your computer reboots**:

```bash
pm2 startup
```

Follow the instructions it gives you.

Save the current process list so it restarts on reboot:

```bash
pm2 save
```

---

### **Common Troubleshooting**

- If you get `ModuleNotFoundError: No module named 'discord'`, activate your virtual environment and make sure pm2 is using it.
- You can **specify your virtual environment Python interpreter**:
    
    ```bash
        pm2 start main.py --name "RPGspotBot" --interpreter "C:\Users\Stev\PycharmProjects\ADVbot\.venv\Scripts\python.exe"
    ```
    

---
