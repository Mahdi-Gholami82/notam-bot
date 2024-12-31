import sqlite3
from folium import Map, Element
from folium.vector_layers import Polygon,Circle
from modules.coordinateTools import sort_coordinates
from modules.dbManager import DataBaseManager

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
        if coordinates_without_radius and len(coordinates_without_radius) > 2:
            draw_ntm_on_map(map,
                            color,
                            sort_coordinates(coordinates_without_radius),
                            'polygon',
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

def add_map_guide(map : Map):
    map_guide_svg = """
    <svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 231.54 212.78">
    <defs>
        <style>
        .cls-1 {
            fill: #0302f8;
        }

        .cls-2, .cls-3 {
            fill: #fff;
        }

        .cls-4, .cls-5 {
            opacity: .8;
        }

        .cls-4, .cls-6 {
            fill: #878787;
        }

        .cls-7 {
            fill: red;
        }

        .cls-3, .cls-8 {
            font-family: BebasNeue-Regular, 'Bebas Neue';
            font-size: 33px;
        }

        .cls-9 {
            fill: #820a85;
        }
        </style>
    </defs>
    <g id="Layer_1-2" data-name="Layer 1">
        <g id="Rectangle_1" data-name="Rectangle 1" class="cls-5">
        <rect class="cls-6" width="231.54" height="135.88" rx="25.47" ry="25.47"/>
        </g>
        <text id="map_guide_text" data-name="map guide text" class="cls-8" transform="translate(18.91 39.04)"><tspan class="cls-7" x="0" y="0">• </tspan><tspan class="cls-2" x="15.18" y="0">Gun fire</tspan><tspan class="cls-9" x="0" y="39.6">• </tspan><tspan class="cls-2" x="15.18" y="39.6">RPA</tspan><tspan class="cls-1" x="0" y="79.2">• </tspan><tspan class="cls-2" x="15.18" y="79.2">ROCKET LAUNCH</tspan></text>
        <rect id="Rectangle_2" data-name="Rectangle 2" class="cls-4" x="24.95" y="146.44" width="182.33" height="41.56" rx="20.56" ry="20.56"/>
        <text class="cls-3" transform="translate(48.83 178.5)"><tspan x="0" y="0">@ir_notams</tspan></text>
    </g>
    </svg>
    """

    # Embed the SVG as a floating element
    floating_element = f"""
    <div style="position: absolute; bottom: 60px; left: 40px; z-index: 1000; width: 231.75px; height: 188.67px;">
        {map_guide_svg}
    </div>
    """
    map.get_root().html.add_child(Element(floating_element))

