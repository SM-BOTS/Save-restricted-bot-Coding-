# DONT REMOVE CREDITS
# Developer: [ Eva Rose ] (https://t.me/EvaRoseX)
# Join TG Channel: https://t.me/ERBotsUpdate
# Ask Doubt On Telegram: @EvaRoseX
# DEVELOPER: BY EVA ROSE


import os

# Login feature, if you want then True , if you don't want then False
LOGIN_SYSTEM = bool(os.environ.get('LOGIN_SYSTEM', True)) # True or False

if LOGIN_SYSTEM == False:
    # if login system is False then fill your tg account session below 
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
else:
    STRING_SESSION = None

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "33361737"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "7cd3bda26b08957a7205bbe8a51e6e90")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "8391386178"))
FORCE_CLEAN_CAPTION = True
# --- Welcome Image Settings ---
START_IMAGE_SHOW = True  # Agar image chahiye toh True rakho, nahi chahiye toh False kar do
START_IMAGE_URL = "https://i.ibb.co/LzSg5v39/photo-2026-06-09-15-56-22-7649425174667722768.jpg"  # Apni image ka direct link
# --- Auto Delete Settings ---
# Time seconds me hona chahiye (Udaharan: 300 seconds = 5 minutes)
AUTO_DELETE_TIME = 300
# Your Channel Id In Which Bot Upload Downloaded Video/File/Message etc.
# And Make Your Bot Admin In this channel with full rights.
# if you don't want to upload in channel then leave it blank don't fill anything.
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")

# Isme apne log channel ki ID daal dena (jaise -100xxxxxxxxx)
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1004214402860"))

# --- MULTI-SHORTENER CONFIGURATION (ALAG-ALAG) ---
VERIFY_EXPIRE_HOURS = int(os.environ.get("VERIFY_EXPIRE_HOURS", 24)) 
BOT_USERNAME = os.environ.get("BOT_USERNAME", "Heysgetwrebot")

# 🌐 Website ka domain (Example: vplink.co, gplinks.in)
SHORTENER_URL = os.environ.get("SHORTENER_URL", "vplink.in")

# 🔑 Shortener website se mili hui aapki Secret API Key
SHORTENER_API = os.environ.get("SHORTENER_API", "643cf7208bfdc009d2e1f953905840a9619d48ca")

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "mongodb+srv://gxmon239:f4l7bKrhka3Fh2cV@cluster0.qmblwql.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "evarose")

# Increase time as much as possible to avoid floodwait, spamming and tg account ban issues.
WAITING_TIME = int(os.environ.get("WAITING_TIME", "10")) # time in seconds

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
