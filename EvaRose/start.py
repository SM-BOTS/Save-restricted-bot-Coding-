# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import pyrogram
import re
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME, START_IMAGE_SHOW, START_IMAGE_URL
from database.db import db, get_dump_channel, set_dump_channel
from EvaRose.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}
    USER_FILES = {}
    USER_STATES = {}  # User state track karne ke liye dict

# Caption cleaner utility function
def clean_bad_caption(caption_text):
    if not caption_text:
        return None
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
    buttons = [
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("❣️ Developer", url="https://t.me/kingvj01")],
        [InlineKeyboardButton("🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/vj_bot_disscussion"),
         InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜ2024_ᴄʜ2024", url="https://t.me/vj_bots")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    welcome_text = f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>"
    
    if START_IMAGE_SHOW == True and START_IMAGE_URL:
        try:
            await client.send_photo(chat_id=message.chat.id, photo=START_IMAGE_URL, caption=welcome_text, reply_markup=reply_markup, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await client.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=reply_markup, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            print(f"Welcome Image Error: {e}")
    else:
        await client.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=reply_markup, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(chat_id=message.chat.id, text=f"{HELP_TXT}")

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="**Batch Successfully Cancelled.**")

# 📸 Photo/Text handling logic update
@Client.on_message((filters.text | filters.photo) & filters.private)
async def save(client: Client, message: Message):
    user_id = message.from_user.id
    
    # ⚙️ Custom Thumbnail save karne ka logic
    if batch_temp.USER_STATES.get(user_id) == "awaiting_thumbnail":
        if not message.photo:
            await message.reply_text("❌ **Kripya ek Photo bhejiye!** Thumbnail ke liye sirf images hi valid hain.")
            return
        
        # Photo ki file id nikal kar database me save karenge
        thumb_id = message.photo.file_id
        try:
            await db.set_thumbnail(user_id, thumb_id)
        except AttributeError:
            pass # Agar db file me function na ho toh handle ke liye
            
        batch_temp.USER_STATES[user_id] = None # Reset state
        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]])
        await message.reply_text("✅ **Custom Thumbnail successfully save ho gaya!**\n\nAb jo bhi videos ya documents aap save karenge, unpar ye thumbnail lag kar aayega.", reply_markup=back_button)
        return

    # ⚙️ Handling Channel ID input when user clicks "Set Channel"
    if batch_temp.USER_STATES.get(user_id) == "awaiting_channel_id":
        if message.text:
            try:
                channel_id = int(message.text)
                await set_dump_channel(user_id, channel_id) 
                batch_temp.USER_STATES[user_id] = None 
                back_button = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]])
                await message.reply_text(f"✅ **Success!** Aapka log channel successfully set ho gaya hai:\n`{channel_id}`\n\n⚠️ **Zaroori:** Bot ko is channel me **Admin** banana mat bhooliyega.", reply_markup=back_button)
            except ValueError:
                await message.reply_text("❌ **Galat Format!** Kripya sirf numeric ID bhejiye (Jaise: -100123456789).")
        return

    # Agar text nahi hai (jaise user ne direct bina kisi state ke random photo bhej di) toh function ko aage na badhayein
    if not message.text:
        return

    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            try:
                await TechVJUser.join_chat(message.text)
            except Exception as e: 
                await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
                return
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired:
            await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

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
            except:
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
        else:
            if TechVJUser is None:
                await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                return
            acc = TechVJUser
                
        batch_temp.IS_BATCH[message.from_user.id] = False
        batch_temp.USER_FILES[message.from_user.id] = []

        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            else:
                username = datas[3]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            await asyncio.sleep(WAITING_TIME)

        if LOGIN_SYSTEM == True:
            try:
                await acc.disconnect()
            except:
                pass                                
        batch_temp.IS_BATCH[message.from_user.id] = True

        if batch_temp.USER_FILES.get(message.from_user.id):
            try:
                total_sent = len(batch_temp.USER_FILES[message.from_user.id])
                notif_msg = await client.send_message(chat_id=message.chat.id, text=f"✅ **Task Completed Successfully!**\n\nAapki total **{total_sent}** files upload kar di gayi hain.\n\n⚠️ **NOTE:** Security reasons ki wajah se yeh saari files agle **5 minutes** me automatically delete ho jayegi! Kripa karke tab tak inhe forward kar lein.")
            except Exception as e:
                print(f"Notification error: {e}")

async def handle_private(client: Client, acc, message: Message, chatid, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty:
        return 
    msg_type = get_message_type(msg)
    if not msg_type:
        return 

    chat = message.chat.id
    user_dump = await get_dump_channel(message.from_user.id)

    if batch_temp.IS_BATCH.get(message.from_user.id):
        return 
    if "Text" == msg_type:
        try:
            text_msg = clean_bad_caption(msg.text)
            sent_msg = await client.send_message(chat, text_msg, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if sent_msg:
                batch_temp.USER_FILES[message.from_user.id].append(sent_msg.id)
            if user_dump and sent_msg:
                try:
                    await sent_msg.copy(int(user_dump))
                except:
                    pass
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading...**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        if os.path.exists(f'{message.id}downstatus.txt'):
            os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        if os.path.exists(f'{message.id}downstatus.txt'):
            os.remove(f'{message.id}downstatus.txt')
        return await smsg.delete()
        
    if batch_temp.IS_BATCH.get(message.from_user.id):
        return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))
    caption = clean_bad_caption(msg.caption)
    if batch_temp.IS_BATCH.get(message.from_user.id):
        return 
            
    # 🖼️ Custom Thumbnail logic handler
    try:
        custom_thumb_id = await db.get_thumbnail(message.from_user.id)
    except:
        custom_thumb_id = None

    uploaded_msg = None
    if "Document" == msg_type:
        try:
            # Agar custom thumbnail hai toh use download karo, nahi toh original thumb use karo
            ph_path = await client.download_media(custom_thumb_id) if custom_thumb_id else await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        try:
            uploaded_msg = await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None:
            os.remove(ph_path)
            
    elif "Video" == msg_type:
        try:
            ph_path = await client.download_media(custom_thumb_id) if custom_thumb_id else await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        try:
            uploaded_msg = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None:
            os.remove(ph_path)
            
    elif "Animation" == msg_type:
        try:
            uploaded_msg = await client.send_animation(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    elif "Sticker" == msg_type:
        try:
            uploaded_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     
    elif "Voice" == msg_type:
        try:
            uploaded_msg = await client.send_voice(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    elif "Audio" == msg_type:
        try:
            ph_path = await client.download_media(custom_thumb_id) if custom_thumb_id else await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None
        try:
            uploaded_msg = await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None:
            os.remove(ph_path)
    elif "Photo" == msg_type:
        try:
            uploaded_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if uploaded_msg:
        batch_temp.USER_FILES[message.from_user.id].append(uploaded_msg.id)
    if uploaded_msg and user_dump:
        try:
            await uploaded_msg.copy(chat_id=int(user_dump))
        except Exception as e:
            print(f"Dump forward error: {e}")
    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    if os.path.exists(file):
        os.remove(file)
    try:
        await client.delete_messages(message.chat.id, [smsg.id])
    except:
        pass

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

# 🔘 Updates Callback Query Handler
@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user_id = query.from_user.id

    if query.data == "settings":
        await query.answer()
        user_dump = await get_dump_channel(user_id)
        current_status = f"`{user_dump}`" if user_dump else "Not Set"
        
        try:
            is_logged_in = await db.get_session(user_id)
            has_thumb = await db.get_thumbnail(user_id)
        except:
            is_logged_in = None
            has_thumb = None
            
        login_status = "🔑 Logged In" if is_logged_in else "🔒 Not Logged In"
        thumb_status = "🖼️ Set" if has_thumb else "❌ Not Set"
        
        # Grid format buttons
        settings_buttons = InlineKeyboardMa
