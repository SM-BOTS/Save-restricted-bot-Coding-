# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import pyrogram
import re
import aiohttp
import uuid
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME, BOT_USERNAME, SHORTENER_URL, SHORTENER_API, VERIFY_EXPIRE_HOURS
from database.db import db, get_dump_channel, set_dump_channel, save_active_token, validate_and_consume_token
from EvaRose.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}
    USER_FILES = {}
    CUSTOM_CAPTIONS = {}

# Token Generator Utility Function
async def get_verify_shortlink(user_id):
    token = str(uuid.uuid4())
    await save_active_token(user_id, token)
    long_url = f"https://t.me/{BOT_USERNAME}?start=verify_{token}"
    api_url = f"https://{SHORTENER_URL}/api?api={SHORTENER_API}&url={long_url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    res_data = await response.json()
                    if res_data.get("status") == "success":
                        return res_data.get("shortenedUrl")
    except Exception as e:
        print(f"Shortener API Error: {e}")
    return long_url

# Caption cleaner utility function (Perfect Overwrite & Fallback Version)
async def clean_bad_caption(user_id, caption_text):
    custom_cap = batch_temp.CUSTOM_CAPTIONS.get(user_id)
    if custom_cap:
        return custom_cap

    if caption_text:
        pattern = r"⏱️\s*\*?\s*Note:\s*\*?\s*Yeh\s*file\s*copyright\s*strikes\s*se\s*bachne\s*ke\s*liye\s*\(?5\s*minutes\)?\s*me\s*automatically\s*delete\s*ho\s*jayegi!?"
        cleaned = re.sub(pattern, "", caption_text, flags=re.IGNORECASE).strip()
        bad_strings = [
            "⏱️ **Note:** Yeh file copyright strikes se bachne ke liye **5 minutes** me automatically delete ho jayegi!",
            "⏱️ Note: Yeh file copyright strikes se bachne ke liye 5 minutes me automatically delete ho jayegi!"
        ]
        for bad_str in bad_strings:
            cleaned = cleaned.replace(bad_str, "")
        cleaned = cleaned.strip()
        return cleaned if cleaned else None
    return None

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(message.chat.id, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(message.chat.id, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        
    if len(message.command) > 1 and message.command[1].startswith("verify_"):
        token_id = message.command[1].split("_")[1]
        is_valid = await validate_and_consume_token(message.from_user.id, token_id)
        if is_valid:
            await db.update_verification(message.from_user.id)
            await message.reply_text("✅ **Verification Successful!** Ab aap agle 12 ghante tak bina kisi limit ke use kar sakte hain.")
            return
        else:
            await message.reply_text("❌ **Invalid Token:** Link dobara verify karein.")
            return

    buttons = [
        [InlineKeyboardButton("❣️ Developer", url="https://t.me/kingvj01")],
        [InlineKeyboardButton("🔍 sᴜᴘᴘᴏʀ體 ɢʀᴏᴜᴘ", url="https://t.me/vj_bot_disscussion"), InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜ2024_ᴄʜ2024", url="https://t.me/vj_bots")],
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data="settings_cmd")]
    ]
    await client.send_message(chat_id=message.chat.id, text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot.\n\nKnow how to use bot by - /help</b>", reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=message.id)

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(chat_id=message.chat.id, text=f"{HELP_TXT}")

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="**Batch Successfully Cancelled.**")

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    user_id = message.from_user.id

    # 🔐 TOKEN LOCK CHECK
    is_verified = await db.is_user_verified(user_id, VERIFY_EXPIRE_HOURS)
    if not is_verified and "https://t.me/" in message.text:
        verify_url = await get_verify_shortlink(user_id)
        btn = [[InlineKeyboardButton("🔐 Click Here To Verify", url=verify_url)]]
        await message.reply_text(text="⚠️ **Access Denied!**\n\nBot use karne ke liye aapko pehle **Verify** karna hoga.", reply_markup=InlineKeyboardMarkup(btn))
        return

    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            try: await TechVJUser.join_chat(message.text)
            except Exception as e: 
                await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
                return
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant: await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired: await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try: toID = int(temp[1].strip())
        except: toID = fromID

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                return
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except: return await message.reply("**Your Login Session Expired. /login Again**")
        else:
            if TechVJUser is None:
                await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                return
            acc = TechVJUser
				
        batch_temp.IS_BATCH[message.from_user.id] = False
        batch_temp.USER_FILES[message.from_user.id] = []

        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try: await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try: await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            else:
                username = datas[3]
                try: await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            await asyncio.sleep(WAITING_TIME)

        if LOGIN_SYSTEM == True:
            try: await acc.disconnect()
            except: pass                				
        batch_temp.IS_BATCH[message.from_user.id] = True

        if batch_temp.USER_FILES.get(message.from_user.id):
            try:
                total_sent = len(batch_temp.USER_FILES[message.from_user.id])
                notif_msg = await client.send_message(chat_id=message.chat.id, text=f"✅ **Task Completed!** Total **{total_sent}** files uploaded.\n\n⚠️ **NOTE:** Security reasons ki wajah se yeh files agle **5 minutes** me delete ho jayengi!")
                all_msg_ids = batch_temp.USER_FILES[message.from_user.id] + [notif_msg.id]
                asyncio.create_task(auto_delete_batch(client, message.chat.id, all_msg_ids, delay=300))
            except Exception as e: print(f"Notification error: {e}")

async def handle_private(client: Client, acc, message: Message, chatid, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 

    chat = message.chat.id
    user_dump = await get_dump_channel(message.from_user.id)

    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            text_msg = await clean_bad_caption(message.from_user.id, msg.text)
            sent_msg = await client.send_message(chat, text_msg, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if sent_msg: batch_temp.USER_FILES[message.from_user.id].append(sent_msg.id)
            if user_dump and sent_msg:
                try: await sent_msg.copy(int(user_dump))
                except: pass
            return 
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading...**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        if os.path.exists(f'{message.id}downstatus.txt'): os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        if os.path.exists(f'{message.id}downstatus.txt'): os.remove(f'{message.id}downstatus.txt')
        return await smsg.delete()
        
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))
    caption = await clean_bad_caption(message.from_user.id, msg.caption)
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
            
    uploaded_msg = None
    custom_thumb = await db.get_thumbnail(message.from_user.id)

    if "Document" == msg_type:
        try: ph_path = await acc.download_media(msg.document.thumbs[0].file_id) if not custom_thumb else custom_thumb
        except: ph_path = custom_thumb
        try: uploaded_msg = await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None and ph_path != custom_thumb: os.remove(ph_path)
    elif "Video" == msg_type:
        try: ph_path = await acc.download_media(msg.video.thumbs[0].file_id) if not custom_thumb else custom_thumb
        except: ph_path = custom_thumb
        try: uploaded_msg = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None and ph_path != custom_thumb: os.remove(ph_path)
    elif "Animation" == msg_type:
        try: uploaded_msg = await client.send_animation(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    elif "Sticker" == msg_type:
        try: uploaded_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     
    elif "Voice" == msg_type:
        try: uploaded_msg = await client.send_voice(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    elif "Audio" == msg_type:
        try: ph_path = await acc.download_media(msg.audio.thumbs[0].file_id) if not custom_thumb else custom_thumb
        except: ph_path = custom_thumb
        try: uploaded_msg = await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None and ph_path != custom_thumb: os.remove(ph_path)
    elif "Photo" == msg_type:
        try: uploaded_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if uploaded_msg: batch_temp.USER_FILES[message.from_user.id].append(uploaded_msg.id)
    if uploaded_msg and user_dump:
        try: await uploaded_msg.copy(chat_id=int(user_dump))
        except Exception as e: print(f"Dump forward error: {e}")
    if os.path.exists(f'{message.id}upstatus.txt'): os.remove(f'{message.id}upstatus.txt')
    if os.path.exists(file): os.remove(file)
    try: await client.delete_messages(message.chat.id, [smsg.id])
    except: pass

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except: pass
    try:
        msg.video.file_id
        return "Video"
    except: pass
    try:
        msg.animation.file_id
        return "Animation"
    except: pass
    try:
        msg.sticker.file_id
        return "Sticker"
    except: pass
    try:
        msg.voice.file_id
        return "Voice"
    except: pass
    try:
        msg.audio.file_id
        return "Audio"
    except: pass
    try:
        msg.photo.file_id
        return "Photo"
    except: pass
    try:
        msg.text
        return "Text"
    except: pass

async def auto_delete_batch(client, chat_id, message_ids, delay=300):
    await asyncio.sleep(delay)
    try: await client.delete_messages(chat_id, message_ids)
    except Exception as e: print(f"Batch Auto-delete error: {e}")

# ----------------------------------------------------
# SETTINGS ACTIONS INTERACTION GRID
# ----------------------------------------------------

@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message):
    user_id = message.from_user.id
    dump_id = await get_dump_channel(user_id)
    custom_cap = batch_temp.CUSTOM_CAPTIONS.get(user_id)
    session_exist = await db.get_session(user_id)
    thumb_exist = await db.get_thumbnail(user_id)
    
    text = "⚙️ **BOT ADVANCED SETTINGS**\n\n"
    text += f"🔐 **Account Session:** {'🟢 Active Logged-In' if session_exist else '🔴 Logged-Out'}\n"
    text += f"📢 **Dump Channel ID:** `{dump_id if dump_id else 'Not Set'}`\n"
    text += f"📝 **Branding Caption:** `{custom_cap if custom_cap else 'Not Set'}`\n"
    text += f"🖼️ **Custom Thumbnail:** {'🟢 Custom Set' if thumb_exist else '🔴 Default'}"
        
    buttons = [
        [InlineKeyboardButton("🔑 LOGIN ACCOUNT", callback_data="req_login"), InlineKeyboardButton("🚪 LOGOUT SESSION", callback_data="req_logout")],
        [InlineKeyboardButton("⚙️ SET DUMP", callback_data="set_dump_info"), InlineKeyboardButton("❌ REMOVE DUMP", callback_data="rem_dump")],
        [InlineKeyboardButton("✍️ SET CAPTION", callback_data="set_caption_info"), InlineKeyboardButton("🗑️ REMOVE CAPTION", callback_data="rem_caption")],
        [InlineKeyboardButton("🖼️ SET THUMBNAIL", callback_data="set_thumb_info"), InlineKeyboardButton("🗑️ REMOVE THUMB", callback_data="rem_thumb")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^settings_cmd$"))
async def settings_callback(client, callback_query):
    user_id = callback_query.from_user.id
    dump_id = await get_dump_channel(user_id)
    custom_cap = batch_temp.CUSTOM_CAPTIONS.get(user_id)
    session_exist = await db.get_session(user_id)
    thumb_exist = await db.get_thumbnail(user_id)
    
    text = "⚙️ **BOT ADVANCED SETTINGS**\n\n"
    text += f"🔐 **Account Session:** {'🟢 Active Logged-In' if session_exist else '🔴 Logged-Out'}\n"
    text += f"📢 **Dump Channel ID:** `{dump_id if dump_id else 'Not Set'}`\n"
    text += f"📝 **Branding Caption:** `{custom_cap if custom_cap else 'Not Set'}`\n"
    text += f"🖼️ **Custom Thumbnail:** {'🟢 Custom Set' if thumb_exist else '🔴 Default'}"
        
    buttons = [
        [InlineKeyboardButton("🔑 LOGIN ACCOUNT", callback_data="req_login"), InlineKeyboardButton("🚪 LOGOUT SESSION", callback_data="req_logout")],
        [InlineKeyboardButton("⚙️ SET DUMP", callback_data="set_dump_info"), InlineKeyboardButton("❌ REMOVE DUMP", callback_data="rem_dump")],
        [InlineKeyboardButton("✍️ SET CAPTION", callback_data="set_caption_info"), InlineKeyboardButton("🗑️ REMOVE CAPTION", callback_data="rem_caption")],
        [InlineKeyboardButton("🖼️ SET THUMBNAIL", callback_data="set_thumb_info"), InlineKeyboardButton("🗑️ REMOVE THUMB", callback_data="rem_thumb")]
    ]
    try: await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except MessageNotModified: await callback_query.answer("Settings updated profile loaded.")

@Client.on_callback_query(filters.regex("^req_login$"))
async def login_click_callback(client, callback_query):
    await callback_query.answer("Please use global /login command to link credentials!", show_alert=True)

@Client.on_callback_query(filters.regex("^req_logout$"))
async def logout_click_callback(client, callback_query):
    user_id = callback_query.from_user.id
    session_exist = await db.get_session(user_id)
    if not session_exist: return await callback_query.answer("Already Logged-Out!", show_alert=True)
    await db.rem_session(user_id)
    await callback_query.message.edit_text("🚪 **Session cleared from DB.**")

@Client.on_callback_query(filters.regex("^set_dump_info$"))
async def set_dump_callback(client, callback_query):
    await callback_query.message.delete()
    await client.send_message(chat_id=callback_query.from_user.id, text="Send your backup channel ID:")
    try:
        response = await client.listen(chat_id=callback_query.from_user.id, timeout=300)
        if response and response.text:
            channel_id = int(response.text.strip())
            await set_dump_channel(callback_query.from_user.id, channel_id)
            await response.reply_text("Channel saved successfully.")
    except Exception as e: await client.send_message(callback_query.from_user.id, f"Error: {e}")

@Client.on_callback_query(filters.regex("^rem_dump$"))
async def remove_dump_callback(client, callback_query):
    await set_dump_channel(callback_query.from_user.id, None)
    await callback_query.message.edit_text("Backup channel removed.")

@Client.on_callback_query(filters.regex("^set_caption_info$"))
async def set_caption_callback(client, callback_query):
    await callback_query.message.delete()
    await client.send_message(chat_id=callback_query.from_user.id, text="Send custom caption text:")
    try:
        response = await client.listen(chat_id=callback
