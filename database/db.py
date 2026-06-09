# DONT REMOVE CREDITS
# Developer: [ Eva Rose ] (https://t.me/EvaRoseX)
# Join TG Channel: https://t.me/ERBotsUpdate
# Ask Doubt On Telegram: @EvaRoseX
# DEVELOPER: BY EVA ROSE






import motor.motor_asyncio
import time  
from config import DB_URI, DB_NAME
from pyrogram.errors import MessageNotModified

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user  # Tech VJ user collection
        
    def new_user(self, id):
        return dict(
            id=id,
            join_date=time.time(),
            upload_count=0,
            dump_channel=None,
            session=None,
            api_id=None,
            api_hash=None,
            last_verified=0,
            thumbnail=None  # Added for safe dynamic fallback
        )
        
    async def add_user(self, id, *args, **kwargs):
        user = self.new_user(id)
        await self.col.insert_one(user)
        
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False
        
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
        
    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users
        
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    # 🔑 ALL LOGIN FUNCTIONS (REQUIRED FOR /LOGIN)
    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get("session") if user else None

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}}, upsert=True)

    async def rem_session(self, id):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': None}}, upsert=True)

    async def get_api_id(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get("api_id") if user else None

    async def set_api_id(self, id, api_id):
        await self.col.update_one({'id': int(id)}, {'$set': {'api_id': api_id}}, upsert=True)

    async def get_api_hash(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get("api_hash") if user else None

    async def set_api_hash(self, id, api_hash):
        await self.col.update_one({'id': int(id)}, {'$set': {'api_hash': api_hash}}, upsert=True)

    # 🔐 TOKEN VERIFICATION TIMEOUT FUNCTION
    async def update_verification(self, user_id):
        current_time = time.time()
        await self.col.update_one(
            {"id": int(user_id)},
            {"$set": {"last_verified": current_time}},
            upsert=True
        )

    async def is_user_verified(self, user_id, expire_hours):
        user = await self.col.find_one({"id": int(user_id)})
        if not user:
            return False
        last_verified = user.get("last_verified", 0)
        current_time = time.time()
        expire_seconds = expire_hours * 3600
        if (current_time - last_verified) < expire_seconds:
            return True 
        return False 

    # 🖼️ DATABASE-BACKED THUMBNAIL LOGIC ADDED BY GEMINI
    async def get_thumbnail(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get("thumbnail") if user else None

    async def set_thumbnail(self, id, thumbnail):
        await self.col.update_one({'id': int(id)}, {'$set': {'thumbnail': thumbnail}}, upsert=True)

    async def rem_thumbnail(self, id):
        await self.col.update_one({'id': int(id)}, {'$set': {'thumbnail': None}}, upsert=True)


# Database client instance setup
db = Database(DB_URI, DB_NAME)


# ----------------------------------------------------
# AUTOMATIC DUMP FORWARDER LOGIC BY EVAROSE
# ----------------------------------------------------

async def get_dump_channel(user_id):
    user = await db.col.find_one({"id": int(user_id)})
    if user:
        return user.get("dump_channel")
    return None

async def set_dump_channel(user_id, channel_id):
    await db.col.update_one(
        {"id": int(user_id)},
        {"$set": {"dump_channel": channel_id}},
        upsert=True
    )

async def auto_forward_to_dump(client, user_id, message_to_copy):
    dump_id = await get_dump_channel(user_id)
    if dump_id:
        try:
            await message_to_copy.copy(chat_id=int(dump_id))
        except Exception as e:
            print(f"Dump forward error: {e}")


# -------------------------------------------------------------
# 🔐 ONE-TIME USE TOKEN SYSTEM GLOBAL FUNCTIONS
# -------------------------------------------------------------

async def save_active_token(user_id, token_id):
    await db.col.update_one(
        {"id": int(user_id)},
        {"$set": {"active_token": token_id}},
        upsert=True
    )

async def validate_and_consume_token(user_id, token_id):
    user = await db.col.find_one({"id": int(user_id)})
    if not user:
        return False
        
    active_token = user.get("active_token", None)
    
    if active_token and active_token == token_id:
        await db.col.update_one(
            {"id": int(user_id)},
            {"$set": {"active_token": None}}
        )
        return True
    return False


# DONT REMOVE CREDITS
# Developer: [ Eva Rose ] (https://t.me/EvaRoseX)
# Join TG Channel: https://t.me/ERBotsUpdate
# Ask Doubt On Telegram: @EvaRoseX
# DEVELOPER: BY EVA ROSE
