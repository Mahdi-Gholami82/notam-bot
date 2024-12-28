import os
import sys

current_path = os.getcwd()
sys.path.append(current_path)

import asyncio
import telegram
from telegram.error import NetworkError
from folium import Map
from config import CHANNEL_ID, HTML_PATH, IMAGE_PATH, TOKEN, DATABASE_PATH
from modules.dbManager import DataBaseManager
from modules.html2png import pngify
from modules.mapify import add_date_and_time, add_map_guide, draw_all_ntms

#sending the map image in an specified telegram channel using a bot
async def send_image_map(bot_token,path,chat_id,date):
    bot = telegram.Bot(bot_token)

    with open(path,'rb') as photo:
        caption = f'🇮🇷 Map daily update\n\n 📅 {date}'
        try:
            await bot.send_photo(chat_id,photo,caption)
        except NetworkError as error:
            print(f'Failed to connect to telegram servers : {error}')

if __name__ == '__main__':

    db = DataBaseManager(
                     DATABASE_PATH,
                     initialize_update=True,
                     retry_for=1
                     )
    notams= db.get_all_coordinated_notams()
    as_of = db.as_of

    #creating the map
    iran_center = [32.4279, 53.6880]
    my_map = Map(location=iran_center,zoom_start=6,zoom_control=False, tiles="Cartodb dark_matter")
    draw_all_ntms(notams,my_map,db)
    add_date_and_time(as_of,my_map)

    #adding the map guide
    add_map_guide(my_map)

    #saving the map and converting it to a png image
    pngify(my_map,HTML_PATH,IMAGE_PATH)

    db.clean_db()

    #sending the final map image to the telegram channel
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_image_map(TOKEN,IMAGE_PATH,CHANNEL_ID,as_of))