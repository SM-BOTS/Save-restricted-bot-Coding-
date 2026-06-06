# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import pyrogram
import re
import time
import requests
import uuid  # 👈 One-time random token generate karne ke liye added
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME, START_IMAGE_SHOW, START_IMAGE_URL, AUTO_DELETE_TIME, VERIFY_EXPIRE_HOURS, SHORTENER_URL, SHORTENER_API, BOT_USERNAME

# 🔐 Database se purane functions ke sath naye functions bhi import kar liye hain
from database.db import db, get_dump_channel, set_dump_channel, save_active_token, validate_and_consume_token

from EvaRose.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}
    USER_FILES = {}
    USER_STATES = {}  # User state track karne ke liye dict

# ⏱️ Auto-delete background task function
async def start_auto_delete(client, chat_id, message_id, delay):
    try:
        await asyncio.sleep(delay)
        await client.delete_messages(chat_id, message_id)
        print(f"🗑️ Automatically Deleted Message ID: {message_id}")
    except Exception as e:
        print(f"❌ Auto Delete Failed for {message_id}: {e}")

# Universal Shortener Link Generator (One-Time Token Fixed)
def get_any_shorturl(user_id):
    try:
        # 🎲 Ek unique random token ID generate karna
        unique_token = str(uuid.uuid4())[:8]
        
        # 💾 Is unique token ko database me background task ke roop me save karna
        loop = asyncio.get_event_loop()
        loop.create_task(save_active_token(user_id, unique_token)) # 👈 db. hata diya hai
        
        # 🔗 Bot ke start link me ab unique token_id pass hoga
        bot_link = f"https://t.me/{BOT_USERNAME}?start=verify_{user_id}_{unique_token}"
        
        clean_url = SHORTENER_URL.replace("https://", "").replace("http://", "").strip("/")
        final_api_call = f"https://{clean_url}/api?api={SHORTENER_API}&url={bot_link}"
        
        response = requests.get(final_api_call)
        try:
            res_json = response.json()
            if "shortenedUrl" in res_json: return res_json.get("shortenedUrl")
            elif "shortened_url" in res_json: return res_json.get("shortened_url")
            elif "url" in res_json: return res_json.get("url")
            elif "data" in res_json and "short_url" in res_json["data"]: return res_json["data"]["short_url"]
        except ValueError:
            if response.text.startswith("http"): return response.text.strip()
    except Exception as e:
        print(f"Universal Shortener API Error: {e}")
    return None

# Caption cleaner utility function
def clean_bad_caption(caption_text):
    if not caption_text:
        return None
    pattern = r"⏱️\s*\*?\s*Note:\s*\*?\s*Yeh\s*file\s*copyright\s*strikes\s*se\s*bachne\s*ke\s*liye\s*\(?.*?\)?\s*me\s*automatically\s*delete\s*ho\s*jayegi!?"
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
    
    # 🔐 ONE-TIME TOKEN VERIFICATION CHECK (Bypass se wapas aane par)
    if len(message.text.split()) > 1:
        param = message.text.split()[1]
        if param.startswith("verify_"):
            try:
                parts = param.split("_")
                verified_user_id = parts[1]
                token_id = parts[2]
                
                if str(verified_user_id) == str(message.from_user.id):
                    # Direct function call bina db. ke
                    is_token_valid = await validate_and_consume_token(message.from_user.id, token_id)
                    
                    if is_token_valid:
                        await db.update_verification(message.from_user.id)
                        await message.reply_text(
                            f"✅ **Verification Successful!**\n\n"
                            f"Aapka token successfully activate ho gaya hai. "
                            f"Ab aap agle **{VERIFY_EXPIRE_HOURS} hours** tak bot ko bina kisi ad ke use kar sakte hain! 🎉"
                        )
                        return
                    else:
                        await message.reply_text("❌ **This link has expired!**\n\nYeh verification link ek baar use ho chuka hai ya purana ho gaya hai. Kripya bot me naya link generate karein.")
                        return
                else:
                    await message.reply_text("❌ Galat verification link!")
                    return
            except Exception as e:
                await message.reply_text("❌ Verification parameter corrupt hai!")
                return

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

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    user_id = message.from_user.id
    
    # ⚙️ Handling Channel ID input when user clicks "Set Channel"
    if batch_temp.USER_STATES.get(user_id) == "awaiting_channel_id":
        try:
            channel_id = int(message.text)
            await set_dump_channel(user_id, channel_id) 
            batch_temp.USER_STATES[user_id] = None 
            back_button = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]])
            await message.reply_text(f"✅ **Success!** Aapka log channel successfully set ho gaya hai:\n`{channel_id}`\n\n⚠️ **Zaroori:** Bot ko is channel me **Admin** banana mat bhooliyega.", reply_markup=back_button)
        except ValueError:
            await message.reply_text("❌ **Galat Format!** Kripya sirf numeric ID bhejiye (Jaise: -100123456789).")
        return

    # 🔑 FIXED: Phone Number Input State Handle (Direct OTP Trigger)
    if batch_temp.USER_STATES.get(user_id) == "awaiting_phone_number":
        phone_number = message.text.strip()
        if not phone_number.startswith("+"):
            await message.reply_text("❌ **Galat Format!** Kripya number ko `+` aur country code ke sath bhejiye (Jaise: `+919876543210`).")
            return
            
        batch_temp.USER_STATES[user_id] = None # State reset
        
        # 🔄 Text badal kar automatic /login command trigger karna
        message.text = f"/login {phone_number}"
        
        # ⚡ Pom Pom repo ke original login handler ko call karna taaki OTP aa jaye
        from plugins.login import login_handler  # Agar aapki file ka naam plugins/login.py hai
        try:
            await login_handler(client, message)
        except Exception as e:
            # Agar upar wala import kaam na kare, toh system ko command execute karne do
            await message.reply_text("🔄 **Processing...** OTP mangwaya ja raha hai, kripya 10-15 seconds rukhein...")
            # Ye line aapke bot ke main handler ko bolti hai ki is message ko fir se read kare as a command
            await client.send_message(chat_id=message.chat.id, text=f"/login {phone_number}")
        return

    # --- 🔐 TOKEN VERIFICATION WALL START ---
    if "https://t.me/" in message.text and not message.text.startswith("/"):
        is_verified = await db.is_user_verified(user_id, VERIFY_EXPIRE_HOURS)
        
        if not is_verified:
            # Custom set shortener se dynamically link nikalna
            short_url = get_any_shorturl(user_id)
            
            if short_url:
                verify_buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔐 Click Here To Verify", url=short_url)]
                ])
                await message.reply_text(
                    f"⚠️ **Access Denied / Token Expired**\n\n"
                    f"Bot ko use karne ke liye aapko har **{VERIFY_EXPIRE_HOURS} hours** me ek baar verify karna zaroori hai.\n\n"
                    f"👉 Niche diye gaye button par click karke verify karein, uske baad bot automatically chalne lagega.",
                    reply_markup=verify_buttons
                )
            else:
                await message.reply_text("❌ Verification system me kuch takneeki kharabi hai, kripya thodi der baad koshish karein.")
            return
    # --- 🔐 VERIFICATION WALL END ---

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

        # 🔔 Jab saari batch files/single files upload ho jayein, tab end me ek single notification jayega
        if batch_temp.USER_FILES.get(message.from_user.id):
            try:
                total_sent = len(batch_temp.USER_FILES[message.from_user.id])
                delete_minutes = int(AUTO_DELETE_TIME / 60)
                
                notif_msg = await client.send_message(
                    chat_id=message.chat.id, 
                    text=f"🚨 **Notification:**\n\nAapki saari requested files (**{total_sent}**) deliver ho chuki hain.\n\n⚠️ **WARNING:** Security aur copyright strikes se bachne ke liye yeh saari files aur yeh notification text ab se **{delete_minutes} minutes** me permanently **auto-delete** ho jayenge!"
                )
                # Notification text message ko bhi baki files ke sath auto-delete timer par laga diya
                asyncio.ensure_future(start_auto_delete(client, message.chat.id, notif_msg.id, AUTO_DELETE_TIME))
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
        
    # 📝 Handling Text Messages
    if "Text" == msg_type:
        try:
            text_msg = clean_bad_caption(msg.text)
            sent_msg = await client.send_message(chat, text_msg, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if sent_msg:
                batch_temp.USER_FILES[message.from_user.id].append(sent_msg.id)
                asyncio.ensure_future(start_auto_delete(client, chat, sent_msg.id, AUTO_DELETE_TIME))
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
    
    # 📑 Safe Original Caption Recovery
    caption = clean_bad_caption(msg.caption)
    
    if batch_temp.IS_BATCH.get(message.from_user.id):
        return 
            
    uploaded_msg = None
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
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
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
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
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
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

# ⏱️ Active sent message tracker for auto-deletion
    if uploaded_msg:
        batch_temp.USER_FILES[message.from_user.id].append(uploaded_msg.id)
        asyncio.ensure_future(start_auto_delete(client, chat, uploaded_msg.id, AUTO_DELETE_TIME))

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


        None)
            await db.set_api_hash(user_id, None)
        except:
            pass

# 🔘 Updates Callback Query Handler (MESSAGE_NOT_MODIFIED ERROR FIXED)
@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user_id = query.from_user.id

    # 1️⃣ SETTINGS MENU OPEN KARNA
    if query.data == "settings":
        await query.answer()
        batch_temp.USER_STATES[user_id] = None
        
        user_dump = await get_dump_channel(user_id)
        current_status = f"`{user_dump}`" if user_dump else "Not Set"
        
        try:
            is_logged_in = await db.get_session(user_id)
        except:
            is_logged_in = None
            
        login_status = "🔑 Logged In" if is_logged_in else "🔒 Not Logged In"
        
        settings_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔑 Login", callback_data="btn_login"),
                InlineKeyboardButton("🚪 Logout", callback_data="btn_logout")
            ],
            [
                InlineKeyboardButton("➕ Set Channel", callback_data="set_channel"),
                InlineKeyboardButton("❌ Remove Channel", callback_data="remove_channel")
            ],
            [
                InlineKeyboardButton("⬅️ Back to Home", callback_data="back_home")
            ]
        ])
        
        try:
            await query.message.edit_text(
                f"⚙️ **Bot Settings Menu**\n\n"
                f"👤 **User:** {query.from_user.mention}\n"
                f"🔑 **Status:** {login_status}\n"
                f"📢 **Log Channel:** {current_status}\n\n"
                f"Niche diye gaye buttons se setup manage karein:",
                reply_markup=settings_buttons
            )
        except MessageNotModified:
            pass # Error safe bypass

    # 2️⃣ SET CHANNEL BUTTON CLICK LOGIC
    elif query.data == "set_channel":
        await query.answer()
        batch_temp.USER_STATES[user_id] = "awaiting_channel_id"
        
        cancel_button = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="settings")]])
        try:
            await query.message.edit_text(
                "📢 **Set Log Channel ID**\n\n"
                "Kripya apne us channel ki **Numeric ID** bhejiye jahan aap files forward (dump) karna chahte hain.\n\n"
                "👉 **Example:** `-100123456789`\n\n"
                "⚠️ **Zaroori:** ID bhejne se pehle bot ko us channel me **Admin** zaroor bana dena!",
                reply_markup=cancel_button
            )
        except MessageNotModified:
            pass

    # 3️⃣ REMOVE CHANNEL BUTTON CLICK LOGIC
    elif query.data == "remove_channel":
        await query.answer()
        batch_temp.USER_STATES[user_id] = None 
        await set_dump_channel(user_id, None) 
        
        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]])
        try:
            await query.message.edit_text(
                "✅ **Success!** Aapka log/dump channel successfully remove kar diya gaya hai.",
                reply_markup=back_button
            )
        except MessageNotModified:
            pass

    # 4️⃣ BACK TO HOME BUTTON CLICK LOGIC
    elif query.data == "back_home":
        await query.answer()
        batch_temp.USER_STATES[user_id] = None
        
        buttons = [
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("❣️ Developer", url="https://t.me/kingvj01")],
            [InlineKeyboardButton("🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/vj_bot_disscussion"),
             InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜ", url="https://t.me/vj_bots")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        welcome_text = f"<b>👋 Hi {query.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>"
        try:
            await query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        except MessageNotModified:
            pass

    # 5️⃣ 🔑 LOGIN BUTTON CLICK LOGIC (DIRECT PHONE NUMBER PROCESS)
    elif query.data == "btn_login":
        await query.answer()
        
        try:
            is_logged_in = await db.get_session(user_id)
        except:
            is_logged_in = None

        if is_logged_in:
            try:
                await query.message.edit_text(
                    "⚠️ **Aap pehle se logged in hain!**\n\nAgar aapko naya account jodna hai, toh pehle niche diye gaye button se **Logout** kijiye.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]])
                )
            except MessageNotModified:
                pass
            return

        # 🔥 CRITICAL FIX: State set karna message edit se pehle hoga taaki har haal me state change ho!
        batch_temp.USER_STATES[user_id] = "awaiting_phone_number"
        
        cancel_button = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="settings")]])
        try:
            await query.message.edit_text(
                "🔑 **Telegram Login Process**\n\n"
                "Kripya apna Telegram **Phone Number** neeche format me bhejiye:\n\n"
                "👉 **Example:** `+919876543210`\n\n"
                "⚠️ **Zaroori:** Country code (jaise India ke liye `+91`) lagana zaroori hai!",
                reply_markup=cancel_button
            )
        except MessageNotModified:
            pass

    # 6️⃣ 🚪 LOGOUT BUTTON CLICK LOGIC (DIRECT DATABASE SE SESSION CLEAR)
    elif query.data == "btn_logout":
        await query.answer()
        try:
            is_logged_in = await db.get_session(user_id)
        except:
            is_logged_in = None
        
        if not is_logged_in:
            try:
                await query.message.edit_text(
                    "❌ **Aap logged in nahi hain!**\n\nLogout karne ke liye pehle login hona zaroori hai.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]])
                )
            except MessageNotModified:
                pass
            return
            
        await db.rem_session(user_id)
        try:
            await db.set_api_id(user_id, None)
            await db.set_api_hash(user_id, None)
        except:
            pass
            
        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Settings", callback_data="settings")]])
        try:
            await query.message.edit_text(
                "✅ **Successfully Logged Out!**\n\nAapka Telegram session is bot se surakshit tarike se hata diya gaya hai.",
                reply_markup=back_button
            )
        except MessageNotModified:
            pass
