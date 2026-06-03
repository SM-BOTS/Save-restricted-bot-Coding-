# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME
from database.db import db, get_dump_channel, set_dump_channel
from EvaRose.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [
        [
            InlineKeyboardButton("❣️ Developer", url = "https://t.me/kingvj01")
        ],[
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')
        ],[
            # Is line me callback_data="settings_cmd" hona chahiye
            InlineKeyboardButton('⚙️ 𝙱𝚘𝚝 𝚂𝚎𝚝𝚝𝚒𝚗𝚐𝚜', callback_data='settings_cmd') 
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    # Joining chat
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
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:    
                        await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(WAITING_TIME)
        if LOGIN_SYSTEM == True:
            try:
                await acc.disconnect()
            except:
                pass                				
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    if CHANNEL_ID:
        try:
            chat = int(CHANNEL_ID)
        except:
            chat = message.chat.id
    else:
        chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
            
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass


# ----------------------------------------------------
# FINAL STABLE DUMP CHANNEL SETTINGS MENU BY EVAROSE
# ----------------------------------------------------
from pyrogram.errors import MessageNotModified

@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message):
    user_id = message.from_user.id
    dump_id = await get_dump_channel(user_id)
    
    if dump_id:
        text = f"**⚙️ 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂**\n\n📢 **Current Channel:** `{dump_id}`"
    else:
        text = f"**⚙️ 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂**\n\n📢 **Current Channel:** _Abhi set nahi hai (Not Set)_"
        
    buttons = [
        [
            InlineKeyboardButton("⚙️ 𝚂𝙴𝚃 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", callback_data="set_dump_info"),
            InlineKeyboardButton("❌ 𝚁𝙴𝙼𝙾𝚅𝙴 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", callback_data="rem_dump")
        ]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^settings_cmd$"))
async def settings_callback(client, callback_query):
    user_id = callback_query.from_user.id
    dump_id = await get_dump_channel(user_id)
    
    if dump_id:
        text = f"**⚙️ 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂**\n\n📢 **Current Channel:** `{dump_id}`"
    else:
        text = f"**⚙️ 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂**\n\n📢 **Current Channel:** _Abhi set nahi hai (Not Set)_"
        
    buttons = [
        [
            InlineKeyboardButton("⚙️ 𝚂𝙴𝚃 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", callback_data="set_dump_info"),
            InlineKeyboardButton("❌ 𝚁𝙴𝙼𝙾𝚅𝙴 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", callback_data="rem_dump")
        ]
    ]
    try:
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except MessageNotModified:
        await callback_query.answer("Aap pehle se hi settings menu me hain! 😉")


@Client.on_callback_query(filters.regex("^set_dump_info$"))
async def set_dump_callback(client, callback_query):
    try:
        await callback_query.message.edit_text(
            "⚙️ **𝖢𝖧𝖠𝖭𝖭𝖤𝖫 𝖲𝖤𝖳 𝖪𝖠𝖱𝖭𝖤 𝖪𝖠 𝖳𝖠𝖱𝖨𝖪𝖠:**\n\n"
            "1️⃣ Pehle bot ko apne channel me **Admin** bana lijiye.\n"
            "2️⃣ Phir yahan aakar ye command bhejiye:\n"
            "👉 `/setchannel` aapki_channel_id\n\n"
            "**Example:**\n"
            "`/setchannel -100123456789`"
        )
    except MessageNotModified:
        pass


@Client.on_message(filters.command("setchannel") & filters.private)
async def set_channel_via_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Galti:** Command ke sath Channel ID bhi bhejiye!\n\n**Example:** `/setchannel -100123456789`")
        
    raw_id = message.command[1]
    try:
        channel_id = int(raw_id)
        chat = await client.get_chat(channel_id)
        
        await set_dump_channel(message.from_user.id, channel_id)
        await message.reply_text(f"✅ **Success!** `{chat.title}` aapka dump channel set ho gaya hai.\nAb aap `/settings` check kar sakte hain.")
    except ValueError:
        await message.reply_text("❌ **Error:** Sahi format me Channel ID bhejiye (ID hamesha `-100` se shuru hoti hai).")
    except Exception as e:
        await message.reply_text("❌ **Error:** Bot aapke channel me nahi hai ya admin nahi hai. Pehle bot ko admin banayein, phir command bhejein.")


@Client.on_callback_query(filters.regex("^rem_dump$"))
async def remove_dump_callback(client, callback_query):
# ----------------------------------------------------
# FINAL DIRECT DUMP CHANNEL SETTINGS BY EVAROSE
# ----------------------------------------------------
from pyrogram.errors import MessageNotModified

@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message):
    user_id = message.from_user.id
    dump_id = await get_dump_channel(user_id)
    
    if dump_id:
        text = f"**⚙️ 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂**\n\n📢 **Current Channel:** `{dump_id}`"
    else:
        text = f"**⚙️ 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂**\n\n📢 **Current Channel:** _Abhi set nahi hai (Not Set)_"
        
    buttons = [
        [
            InlineKeyboardButton("⚙️ 𝚂𝙴𝚃 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", callback_data="set_dump_info"),
            InlineKeyboardButton("❌ 𝚁𝙴𝙼𝙾𝚅𝙴 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", callback_data="rem_dump")
        ]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^settings_cmd$"))
async def settings_callback(client, callback_query):
    user_id = callback_query.from_user.id
    dump_id = await get_dump_channel(user_id)
    
    if dump_id:
        text = f"**⚙️ 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂**\n\n📢 **Current Channel:** `{dump_id}`"
    else:
        text = f"**⚙️ 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂**\n\n📢 **Current Channel:** _Abhi set nahi hai (Not Set)_"
        
    buttons = [
        [
            InlineKeyboardButton("⚙️ 𝚂𝙴𝚃 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", callback_data="set_dump_info"),
            InlineKeyboardButton("❌ 𝚁𝙴𝙼𝙾𝚅𝙴 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", callback_data="rem_dump")
        ]
    ]
    try:
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except MessageNotModified:
        await callback_query.answer("Aap pehle se hi settings menu me hain! 😉")


@Client.on_callback_query(filters.regex("^set_dump_info$"))
async def set_dump_callback(client, callback_query):
    await callback_query.message.delete()
    
    # Send normal message to request ID
    msg = await client.send_message(
        callback_query.from_user.id,
        "⚙️ **𝖢𝖧𝖠𝖭𝖭𝖤𝖫 𝖲𝖤𝖳 𝖪𝖠𝖱𝖭𝖤 𝖪𝖠 𝖳𝖠𝖱𝖨𝖪𝖠:**\n\n"
        "1️⃣ Pehle bot ko apne channel me **Admin** bana lijiye.\n"
        "2️⃣ Phir apne channel ki ID (Jaise `-100xxxxxxxxxx`) direct yahan niche reply me bhejiye:"
    )
    
    # Direct message input waiting method
    try:
        response = await client.listen(chat_id=callback_query.from_user.id, timeout=300)
        if response and response.text:
            raw_id = response.text.strip()
            channel_id = int(raw_id)
            
            # Save to Database straight away
            await set_dump_channel(callback_query.from_user.id, channel_id)
            await response.reply_text(f"✅ **Success!** Aapki Dump Channel ID (`{channel_id}`) successfully save ho gayi hai!\nAb aap /settings check kar sakte hain.")
    except ValueError:
        await client.send_message(callback_query.from_user.id, "❌ **Error:** Sahi format me sirf Channel ID bhejiye (ID hamesha `-100` se shuru hoti hai).")
    except Exception as e:
        await client.send_message(callback_query.from_user.id, "⏱️ **Timeout ya Error:** Aapne ID bhejne me der kar di ya koi aur dikkat aayi. Phir se koshish karein.")


@Client.on_callback_query(filters.regex("^rem_dump$"))
async def remove_dump_callback(client, callback_query):
    user_id = callback_query.from_user.id
    dump_id = await get_dump_channel(user_id)
    
    if not dump_id:
        await callback_query.answer("⚠️ Aapka koi channel pehle se set nahi hai!", show_alert=True)
        return
        
    await set_dump_channel(user_id, None)
    try:
        await callback_query.message.edit_text(
            "❌ **Aapka Dump Channel successfully remove kar diya gaya hai!**\n\nNaya channel jodne ke liye fir se `/settings` use karke check karein."
        )
    except MessageNotModified:
        pass
