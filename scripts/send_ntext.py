import os
import sys

current_path = os.getcwd()
sys.path.append(current_path)

import re
import asyncio
import telegram
from telegram.constants import ParseMode
from telegram.error import NetworkError, RetryAfter
from config import CHANNEL_ID, DATABASE_PATH, TOKEN
from modules.dbManager import DataBaseManager


def get_notam_rest(notam,notam_id):
    notam = notam.replace('\n',' ')

    match = re.search(rf'{notam_id}(.*)CREATED:', notam)        

    if match:
        rest = match.group(1)
    return rest

async def send_messages(bot_token,notams,chat_id):
    bot = telegram.Bot(token=bot_token)
    c = 0
    for notam in notams:

        #parsing the notam string and seperating the differant parts of it
        notam_db_id,notam_id,notam_text,created_at = notam
        notam_rest = get_notam_rest(notam_text,notam_id)
        created_at = created_at.replace('-',r'\-')

        c += 1
        print(c ,notam_id , sep=' *** ' )
        emoji = emoji_selector(notam_text)
        text = f"{emoji}{notam_id}\n```text\n{notam_rest}```\nCREATED AT: {created_at}"
        try:
            await bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN_V2)

            db.set_is_sent(notam_db_id)
        #waiting for the telegram flood control limit to pass and then trying again
        except RetryAfter as error:
            waiting_time = error.retry_after+1
            print(f"Telegram flood control limit reached waiting for : {waiting_time} seconds...")
            await asyncio.sleep(waiting_time)
            try:
                await bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN_V2)
            except:
                continue
        except NetworkError as error:
            print(f"Failed to connect. Error: {error}")
            break
        except Exception as error:
            print(f'Error : {error}')

        await asyncio.sleep(1)

    #deleting the old notam ids that no longer exist
    db.clean_db()


def emoji_selector(notam):
    if 'GUN FIRING' in notam:
        return '🔴'
    elif 'ROCKET LAUNCHES' in notam:
        return '🔵'
    elif 'RPA' in notam:
        return '🟣'
    return '⚫️'
        

if __name__ == '__main__':
    
    db = DataBaseManager(
                     DATABASE_PATH,
                     initialize_update=True,
                     retry_for=1
                     )
    
    notams = db.get_not_sent_notams()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_messages(TOKEN,notams,CHANNEL_ID))
    #telegram closes the loop event automatically
