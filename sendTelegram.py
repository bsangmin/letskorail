import telegram
import json

# Your Telegram bot token
with open("secret/info.json", "r") as f:
    info = json.load(f)

TOKEN = info['token']
CHAT_ID = 6189787800

async def sendTelegram(_text):
    bot = telegram.Bot(token=TOKEN)
    await bot.send_message(text=_text,chat_id=CHAT_ID)