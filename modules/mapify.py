from folium import Map, Element
from folium.vector_layers import Polygon,Circle
from modules.dbManager import DataBaseManager
import sqlite3

conn = sqlite3.connect('saved_notams.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")
conn.commit()

def draw_ntm_on_map(map : Map, color : str, coordinates : tuple,shape_type : str) -> None:
    if shape_type == 'circle':
        for coordinate in coordinates:
            Circle(
                location = coordinate[:2],
                radius = coordinate[-1],
                stroke = True,
                color = color,
                weight=2,
                fill =True,
                fill_color = color,
                fill_opacity = 0.4,
            ).add_to(map)
    elif shape_type == 'polygon':
        Polygon(
            locations=coordinates,
            stroke = True,
            color = color,
            weight=2,
            fill =True,
            fill_color = color,    
            fill_opacity = 0.4,
        ).add_to(map)

def draw_all_ntms(notams,map : Map,db : DataBaseManager):
    print(f'adding {len(notams)} highlighted area\'s to the map')
    for notam in notams:
        coordinates_with_radius, coordinates_without_radius = db.get_all_coordinates(notam)
        # coordinates = get_all_coordinates(notam)
        notam_text = db.get_notam_text(notam)
        if 'GUN FIRING' in notam_text:
            color = 'Red'
        elif 'ROCKET LAUNCHES' in notam_text:
            color = 'Blue'
        elif 'RPA' in notam_text:
            color = 'Purple'
        else :
            continue


        if coordinates_with_radius:
            draw_ntm_on_map(map,
                            color,
                            coordinates_with_radius,
                            'circle'
                            )
        if coordinates_without_radius:
            draw_ntm_on_map(map,
                            color,
                            coordinates_without_radius,
                            'polygon'
                            )
            
def add_date_and_time(dt,map : Map) -> None:
    date_html = f'''
    <div style="
        position: fixed; 
        bottom: 0px; left: 0px; width: auto; height: 29px;min-width: 400px;
        border:2px solid grey; z-index:9999; font-size:18px;
        background-color:white;">
        <p>  As of: {dt}</p>
    </div>
    '''
    map.get_root().html.add_child(Element(date_html))
