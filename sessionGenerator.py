import os.path

from dotenv import load_dotenv, find_dotenv
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

load_dotenv(find_dotenv())

api_id = os.getenv("API_ID")
api_hash = os.getenv('API_HASH')

if os.path.exists("tg.session"):
    os.remove("tg.session")

bot = TelegramClient(
    "tg",
    api_id,
    api_hash,
)


def main():
    bot.start()
    session_string = StringSession.save(bot.session)
    print("Below is your session string:\n")
    print(session_string)


main()
