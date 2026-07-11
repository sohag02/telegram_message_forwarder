# Telegram Message Forwarder Userbot

A powerful, self-hosted Telegram userbot designed to automatically forward messages from configured source chats to destination chats. Written in Python utilizing [Telethon](https://github.com/LonamiWebs/Telethon) and [aiosqlite](https://github.com/omnilib/aiosqlite).

## 🚀 Features

- **Dynamic Mapping Management**: Add, delete, and list message routing configurations directly via Telegram commands.
- **Smart Reply Tracking**: Automatically maps replies from source chats. If a reply is forwarded, it is sent as a reply to the corresponding forwarded message in the destination chat instead of a standalone message.
- **Bypass Forward Restrictions**: Automatically falls back to copying message contents (text, media, and formatting) if the source chat restricts message forwarding.
- **Clickable Channel Links**: The `.list` command automatically resolves chat entity IDs to clickable Telegram links for channels, groups, and users.
- **High-Performance Database Store**: Uses SQLite with Write-Ahead Logging (WAL) and synchronous mode optimizations for logging and looking up message mappings.
- **Modern Package Management**: Ready for Python 3.13+ and managed seamlessly with [uv](https://github.com/astral-sh/uv).
- **Structured Logs**: Configured with rotating file logs (`logs/forwarder.log`) to keep track of successful forwards, warnings, and errors.

---

## 📋 Prerequisites

- **Python 3.13** or higher.
- **uv** (recommended package manager) or standard **pip**.
- Telegram `API_ID` and `API_HASH` (get them from [my.telegram.org](https://my.telegram.org)).

---

## ⚙️ Setup and Installation

### 1. Clone & Navigate to Workspace
```bash
git clone <repository-url>
cd forward_bot_new
```

### 2. Configure Environment Variables
Create a `.env` file in the root of the project directory with the following variables:
```ini
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=
```

### 3. Generate a Telegram Session String
Since this is a userbot, it runs on behalf of your user account. We use a `StringSession` to run the bot without needing to log in interactively every time.
Run the generator script:
```bash
uv run sessionGenerator.py
```
1. Enter your phone number (including country code) and the login code sent by Telegram.
2. The script will output a long session string.
3. Copy this string and paste it into the `SESSION_STRING` field in your `.env` file.

---

## 🏃 Running the Bot

Start the userbot using `uv`:
```bash
uv run run.py
```
You should see logs indicating that the database connection has been established, resources have been prepared, and the bot has successfully signed in.

---

## 💬 Usage & Commands

Commands are run by sending a message containing the prefix directly from your own Telegram account (self-messages or in any chat). Only messages sent by you (`event.out`) will trigger these commands.

| Command | Description | Example |
| :--- | :--- | :--- |
| **`.help`** | Displays the help message with available commands. | `.help` |
| **`.add <source_chat_id> <destination_chat_id>`** | Adds a new mapping from a source chat to a destination chat. | `.add -1001234567890 -1000987654321` |
| **`.delete <source_chat_id> <destination_chat_id>`** | Deletes a message forwarding mapping. | `.delete -1001234567890 -1000987654321` |
| **`.list`** | Lists all configured mappings with their status and hyperlinks to the chats. | `.list` |

*Note: Chat IDs are typically negative integers for channels and groups (e.g., `-1001234567890`).*

---

## 🗄️ Database Schema

The SQLite database is stored at `data/userbot.db` and consists of two main tables:

### 1. `mappings`
Stores the configured rules for where messages should be forwarded.
```sql
CREATE TABLE IF NOT EXISTS mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_chat_id INTEGER NOT NULL,
    destination_chat_id INTEGER NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    UNIQUE(source_chat_id, destination_chat_id)
);
```

### 2. `forwarded_messages`
Stores the relationship between original and forwarded messages, enabling correct reply nesting.
```sql
CREATE TABLE IF NOT EXISTS forwarded_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_chat_id INTEGER NOT NULL,
    source_message_id INTEGER NOT NULL,
    destination_chat_id INTEGER NOT NULL,
    destination_message_id INTEGER NOT NULL,
    UNIQUE(source_chat_id, source_message_id, destination_chat_id)
);
```

---

## 🛡️ License and Disclaimer

This project is intended for personal and educational use. Be aware that running userbots can occasionally lead to account restrictions if abused (e.g., excessive request rates leading to flood bans). Use responsibly.
