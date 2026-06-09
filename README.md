# 🤖 SAVE RESTRICTED CONTENT TELEGRAM BOT

### 👑 CREDITS & OWNERSHIP:
* **Core Developer & Framework Architect:** [@kingvj01](https://t.me/kingvj01) ❣️
* **Original Repository Base:** [@EvaRoseX](https://t.me/EvaRoseX) 🌹
* **Official Automated Updates:** [@vj_bots](https://t.me/vj_bots) 🤖
* **Support Group:** [@vj_bot_disscussion](https://t.me/vj_bot_disscussion) 🔍

---

A powerful, optimized, and multi-functional Telegram Bot built using **Python** and the **Pyrogram** library. This bot allows users to download and save restricted content (photos, videos, documents, audios, and text) from private or public channels/groups effortlessly.

---

## 🌟 KEY FEATURES

* **Restricted Content Bypass:** Seamlessly download files from channels with saving/forwarding restrictions.
* **Clean Interactive UI:** Fixed, clutter-free standard normal text buttons for advanced user configurations.
* **Advanced Settings Panel:**
    * 🔑 **Session Management:** Securely link or log out account sessions.
    * 📢 **Dump Channel:** Automatically back up all downloaded files to a custom private channel.
    * ✍️ **Custom Branding Caption:** Apply a personalized caption to downloaded text or files.
    * 🖼️ **Custom Thumbnail:** Lock a global permanent thumbnail for document and video uploads.
* **Auto-Deletion System:** Automatically purges batch downloaded files after 5 minutes to prevent copyright flags.
* **Token Verification Lock:** Optional URL shortener integration to protect the bot with a 12-hour verification bypass loop.
* **Real-time Activity Logs:** Sends instant detailed notifications to a private `LOG_CHANNEL` when new users join.

---

## 🛠️ ENVIRONMENT VARIABLES & CONFIGURATION

Configure the following variables in your `config.py` or system environment dashboard:

| Variable Name | Description | Required |
| :--- | :--- | :--- |
| `API_ID` | Your Telegram API ID from my.telegram.org. | **Yes** |
| `API_HASH` | Your Telegram API Hash from my.telegram.org. | **Yes** |
| `BOT_TOKEN` | The bot token generated via BotFather. | **Yes** |
| `STRING_SESSION` | Pre-configured Pyrogram String Session for account bypass. | No |
| `LOG_CHANNEL` | ID of the private log channel for active tracking. | **Yes** |
| `START_PIC` | Direct Telegram link of the start menu welcome image. | **Yes** |
| `LOGIN_SYSTEM` | Enable or disable custom user session authentication (`True`/`False`). | **Yes** |
| `SHORTENER_URL` | Domain API shortener endpoint for verification token. | No |
| `SHORTENER_API` | Token key for shortener tracking link bypass. | No |

---

## 🚀 DEPLOYMENT GUIDE

### 1. Local Setup
```bash
# Clone the repository
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd your-repo-name

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 bot.py
