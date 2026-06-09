# Don't Remove Credit Tg - @EvaRoseX
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@EvaRoseX
# Ask Doubt on telegram @EvaRoseX_Support

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGIN_SYSTEM

if STRING_SESSION is not None and LOGIN_SYSTEM == False:
    EvaRoseUser = Client("EvaRose", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
    EvaRoseUser.start()
else:
    EvaRoseUser = None

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

    async def start(self):
        await super().start()
        print('Bot Started Powered By @EvaRoseX')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

if __name__ == "__main__":
    bot = Bot()
    bot.run()

# Don't Remove Credit Tg - @EvaRoseX
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@EvaRoseX
# Ask Doubt on telegram @EvaRoseX_Support
