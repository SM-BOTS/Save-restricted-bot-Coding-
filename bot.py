# Don't Remove Credit Tg - @EvaRoseX
import pyromod
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGIN_SYSTEM

if STRING_SESSION is not None and LOGIN_SYSTEM == False:
    # 🌟 CHANGE HERE TO EVAROSEUSER
    EvaRoseUser = Client("EvaRose", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
    EvaRoseUser.start()
else:
    EvaRoseUser = None
