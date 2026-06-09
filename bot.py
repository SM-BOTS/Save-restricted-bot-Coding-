# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

# 🚀 IMPORT PYROMOD BEFORE CLIENT TO INJECT MODS
import pyromod
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGIN_SYSTEM

# --- Initial Patch For Pyromod V3 KeyError ---
if not hasattr(Client, 'listeners'):
    Client.listeners = {}

# Direct string registration to bypass missing enum modules
Client.listeners['message'] = {}
Client.listeners['MESSAGE'] = {}

if STRING_SESSION is not None and LOGIN_SYSTEM == False:
    TechVJUser = Client("EvaRose", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
    TechVJUser.start()
else:
    TechVJUser = None

class Bot(Client):

    def __init__(self):
        super().__init__(
            "evarose login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="EvaRose"),
            workers=150,
            sleep_threshold=5
        )

    async_to_sync_wrap = None # Safe reset for sync handler wrappers

    async def start(self):
        await super().start()
        # Force double check during instance initialization
        if not hasattr(self, 'listeners') or not self.listeners:
            self.listeners = {}
        if 'message' not in self.listeners:
            self.listeners['message'] = {}
            
        print('Bot Started Powered By @EvaRoseX')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

if __name__ == "__main__":
    bot = Bot()
    bot.run()

# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
