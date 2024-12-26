import sys
sys.path.append('D:\\notamlinux\\notamlinux')
#//home//notamste//notamlinux//notambot


from time import strftime, strptime, time
from config import NOTAM_URL
from modules.notamScrapper import scrap_notam
import sqlite3
import re
from modules.coordinateTools import dms_to_dd, sort_coordinates

conn = sqlite3.connect('saved_notams.db')
with conn:
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

def convert_time_standard(time : str):
    time_format = "%d %b %Y %H:%M:%S"
    standard_time_format = "%Y-%m-%d %H:%M:%S"
    time_obj = strptime(time.strip(),time_format)
    standard_time = strftime(standard_time_format,time_obj)
    return standard_time



def notam_parser(notam : str):
    searching_notam = notam.replace('\n',' ')
    if 'Q)' in searching_notam :
        match = re.search(r'(.*)Q\).*CREATED:\s*(.*)SOURCE', searching_notam)        
    else :
        match = re.search(r'(.*)A\).*CREATED:\s*(.*)\s*SOURCE', searching_notam)
    if match:
        id = match.group(1)
        created = convert_time_standard(match.group(2).strip())
    return id.strip(), notam.strip() , created


def get_coordinates(notam : str):
    coordinates = []
    radius = str()
    latitude = str()
    longitude = str()
    notam = notam.replace('\n',' ')

    matches = re.finditer(r'(RADIUS\s*\d+\s*KM.*?)?(\d{6}[NS]).*?(\d{6}[EW])', notam)
    for match in matches:
        radius = re.search(r'RADIUS\s*(\d+)\s*KM',str(match.group(1)))
        if radius : 
            radius = float(radius.group(1))
        latitude = dms_to_dd(match.group(2))
        longitude = dms_to_dd(match.group(3))

        match_result = [latitude, longitude, radius]
        coordinates.append(match_result)

    return coordinates


def save_notam(notam):
    with conn :
        cursor = conn.cursor()
        try:
            parsed_notam = notam_parser(notam)
            cursor.execute('INSERT OR IGNORE INTO notams (notam_id,notam_text,created_at,is_sent) VALUES (?, ?, ?, ?)', (*parsed_notam,0))
            coordinates = get_coordinates(notam)

            # getting the notam id in db
            cursor.execute('SELECT notam_db_id FROM notams WHERE notam_text=:notam',{'notam' : notam})
            notam_db_id = int(cursor.fetchone()[0])

            cursor.execute('SELECT * FROM coordinates WHERE notam_db_id=:notam_db_id',{'notam_db_id':notam_db_id})
            existing_coordinates = cursor.fetchone()
            
            if coordinates and not existing_coordinates:
                query ="""INSERT INTO coordinates  (latitude,longitude,radius,notam_db_id) VALUES (?, ?, ?, ?)"""
                for coordinate in coordinates:
                    cursor.execute(query,(*coordinate,notam_db_id))
        except Exception as e:
            print(f'Exception: {e}')
            return

def get_notam_db_id(notam):
    with conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notams WHERE notam_text=:notam',{'notam' : notam})
        notam_db_id = cursor.fetchone()
    return notam_db_id[0]



def set_is_sent(notam_db_id):
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE notams SET is_sent=1 WHERE notam_db_id=:notam_db_id",{'notam_db_id':notam_db_id})

def get_total():
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT notam_db_id FROM notams")
        return cursor.fetchall()

if __name__ == '__main__':
    pass
else :
    # updating the data base with new notams when imported as module <<<<<<
    Updated = False
    scrapped_notams = scrap_notam(NOTAM_URL)
    if scrapped_notams:
        notams, as_of, number_of_notams = scrapped_notams
        if int(number_of_notams) == len(notams):
            print('Updating notams...')
            Updated = True
            with conn:
                cursor.execute("INSERT OR REPLACE INTO db_variables (name,value) VALUES (?, ?)", ('as_of', as_of))
                cursor = conn.cursor()
                cursor.execute('SELECT notam_text FROM notams')
                notam_texts = cursor.fetchall()
            for notam in notams:
                if not notam.strip() in notam_texts:
                    save_notam(notam)

        stripped_notams = [notam.strip() for notam in notams]   
        # >>>>>>
    else:
        notams, number_of_notams = None,None
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM db_variables WHERE name=:as_of",{'as_of':'as_of'})
            as_of = cursor.fetchone()[0]


def get_not_sent_notams():
    with conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT notam_db_id,notam_id,notam_text,created_at FROM notams WHERE is_sent=0 
                       ORDER BY STRFTIME("%Y-%m-%d %H:%M:%S", created_at)""")
        not_sent_notams = cursor.fetchall()
    return not_sent_notams

def get_all_coordinated_notams():
    with conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT DISTINCT 
                            notam_id
                            FROM notams n
                            INNER JOIN coordinates c ON n.notam_db_id = c.notam_db_id;
                        """)
        fetch = cursor.fetchall()  
        coordinated_notams = list(sum(fetch,()))  
    return coordinated_notams, as_of

def get_all_coordinates(notam_id) -> dict[str,list]:
    with conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT coordinates.latitude, coordinates.longitude, coordinates.radius
            FROM notams INNER JOIN coordinates ON notams.notam_db_id = coordinates.notam_db_id
            WHERE notams.notam_id = :notam_id AND coordinates.radius IS NOT NULL;""",{'notam_id':notam_id})
        coordinates_with_radius = cursor.fetchall()

        cursor.execute("""SELECT coordinates.latitude, coordinates.longitude
            FROM notams INNER JOIN coordinates ON notams.notam_db_id = coordinates.notam_db_id
            WHERE notams.notam_id = :notam_id AND coordinates.radius IS NULL;""",{'notam_id':notam_id})
        coordinates_without_radius = cursor.fetchall()

    return  coordinates_with_radius, coordinates_without_radius

def get_notam_text(notam_id):
    with conn:
        cursor = conn.cursor()
        cursor.execute('SELECT notam_text FROM notams WHERE notam_id=:notam_id',{'notam_id' : notam_id})
        notam_texts = cursor.fetchall()
        notam_text = ''.join(sum(notam_texts,())[0])

    return notam_text


def clean_db():
    if Updated:
        print('cleaning the database...')
        with conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute('SELECT notam_db_id,notam_text FROM notams WHERE is_sent=1')
            notams_in_db = cursor.fetchall()  
            for notam_in_db in notams_in_db:

                notam_db_id,notam_text = notam_in_db
                notam_text_stripped = notam_text.strip()
                if notam_text_stripped not in stripped_notams:
                    cursor.execute('DELETE FROM notams WHERE notam_db_id=:notam_db_id;',{'notam_db_id':notam_db_id})