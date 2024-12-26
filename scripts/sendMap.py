import sys

sys.path.append('D:\\notamlinux\\notamlinux')

from modules.dbManager import DataBaseManager
import asyncio
import telegram
from telegram.error import NetworkError
from config import CHANNEL_ID, HTML_PATH, IMAGE_PATH, TEMPLATE_PATH, TOKEN, DATABASE_PATH
from folium import Map
from PIL import Image
from modules.html2png import pngify
from modules.mapify import add_date_and_time, draw_all_ntms

#sending the map image in an specified telegram channel using a bot
async def send_image_map(bot_token,path,chat_id,date):
    bot = telegram.Bot(bot_token)

    with open(path,'rb') as photo:
        caption = f'🇮🇷 Map daily update\n\n 📅 {date}'
        try:
            await bot.send_photo(chat_id,photo,caption)
        except NetworkError as error:
            print(f'Failed to connect to telegram servers : {error}')

def add_template(template_path : Image,image_path : Image):
    img = Image.open(image_path).convert('RGBA')
    template = Image.open(template_path).convert('RGBA')
    img.alpha_composite(template)
    img.save(image_path)

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

    #saving the map and converting it to a png image
    my_map.save(HTML_PATH)
    pngify(HTML_PATH,IMAGE_PATH)

    #adding the map guide
    add_template(TEMPLATE_PATH,IMAGE_PATH)

    #sending the final map image to the telegram channel
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_image_map(TOKEN,IMAGE_PATH,CHANNEL_ID,as_of))