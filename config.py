from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChannel
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import asyncio

API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
SESSION = 'userbot'
LOG_CHANNEL = -1001234567890  # Ganti sesuai kebutuhan

client = TelegramClient(SESSION, API_ID, API_HASH)

# Data penyimpanan sementara
global_muted_users = set()
global_banned_users = set()
global_kicked_users = set()
banned_channels = set()

GCAST_KEYWORDS = ['join', 'subscribe', 'support', 'https://t.me/', 't.me/']

# Banned rights for channel/user
BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True
)

# ✅ Helper: Extract user ID dari argumen atau balasan
async def get_target_user(event):
    args = event.pattern_match.group(1)
    if args:
        try:
            return int(args)
        except:
            return None
    reply = await event.get_reply_message()
    if reply:
        return reply.sender_id
    return None

# ✅ GMUTE
@client.on(events.NewMessage(pattern=r"\.gmute(?:\s|$)(.*)"))
async def gmute(event):
    user_id = await get_target_user(event)
    if user_id:
        global_muted_users.add(user_id)
        await event.reply(f"✅ User `{user_id}` telah di-GMUTE.")
    else:
        await event.reply("❌ Balas pesan atau beri ID user.")

# ✅ UNGMUTE
@client.on(events.NewMessage(pattern=r"\.ungmute(?:\s|$)(.*)"))
async def ungmute(event):
    user_id = await get_target_user(event)
    if user_id in global_muted_users:
        global_muted_users.remove(user_id)
        await event.reply(f"✅ User `{user_id}` telah di-UNGmute.")
    else:
        await event.reply("❌ User tidak dalam daftar GMUTE.")

# ✅ GBAN
@client.on(events.NewMessage(pattern=r"\.gban(?:\s|$)(.*)"))
async def gban(event):
    user_id = await get_target_user(event)
    if user_id:
        global_banned_users.add(user_id)
        try:
            await client(EditBannedRequest(event.chat_id, user_id, BANNED_RIGHTS))
        except:
            pass
        await event.reply(f"✅ User `{user_id}` di-GBAN.")
    else:
        await event.reply("❌ Balas pesan atau beri ID user.")

# ✅ UNGBAN
@client.on(events.NewMessage(pattern=r"\.ungban(?:\s|$)(.*)"))
async def ungban(event):
    user_id = await get_target_user(event)
    if user_id in global_banned_users:
        global_banned_users.remove(user_id)
        try:
            await client.edit_permissions(event.chat_id, user_id, view_messages=True)
        except:
            pass
        await event.reply(f"✅ User `{user_id}` di-UNGBAN.")
    else:
        await event.reply("❌ User tidak dalam daftar GBAN.")

# ✅ GKICK
@client.on(events.NewMessage(pattern=r"\.gkick(?:\s|$)(.*)"))
async def gkick(event):
    user_id = await get_target_user(event)
    if user_id:
        global_kicked_users.add(user_id)
        try:
            await client.kick_participant(event.chat_id, user_id)
        except:
            pass
        await event.reply(f"✅ User `{user_id}` di-GKICK.")
    else:
        await event.reply("❌ Balas pesan atau beri ID user.")

# ✅ UNGKICK
@client.on(events.NewMessage(pattern=r"\.ungkick(?:\s|$)(.*)"))
async def ungkick(event):
    user_id = await get_target_user(event)
    if user_id in global_kicked_users:
        global_kicked_users.remove(user_id)
        await event.reply(f"✅ User `{user_id}` di-UNGKICK.")
    else:
        await event.reply("❌ User tidak dalam daftar GKICK.")

# 🔐 Anti-GCAST otomatis GMUTE
@client.on(events.NewMessage())
async def anti_gcast_handler(event):
    if event.sender_id in global_muted_users:
        await event.delete()
        return

    text = event.raw_text or ''
    if any(keyword.lower() in text.lower() for keyword in GCAST_KEYWORDS):
        if event.sender_id and event.sender_id not in global_muted_users:
            global_muted_users.add(event.sender_id)
            await event.delete()
            await client.send_message(LOG_CHANNEL, f"🚫 GCAST terdeteksi. User `{event.sender_id}` telah di-GMUTE.")

# 🔐 Anti-CHANNEL: Ban channel otomatis
@client.on(events.NewMessage())
async def anti_channel_handler(event):
    if isinstance(event.message.peer_id, PeerChannel):
        ch_id = event.message.peer_id.channel_id
        if ch_id not in banned_channels:
            banned_channels.add(ch_id)
            try:
                await client.edit_permissions(event.chat_id, ch_id, view_messages=True)
            except:
                pass
            await event.delete()
            await client.send_message(LOG_CHANNEL, f"🚨 Channel `{ch_id}` dibanned karena mengirim pesan.")

print("🔥 Userbot Telegram aktif...")
client.start()
client.run_until_disconnected()
