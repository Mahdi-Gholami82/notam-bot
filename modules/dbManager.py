import sqlite3
import re
from time import strftime, strptime
from config import DATABASE_PATH, NOTAM_URL
from modules.notamScrapper import scrap_notam
from modules.coordinateTools import dms_to_dd

conn = sqlite3.connect(DATABASE_PATH)
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
        match = re.search(r'(.+)Q\).*CREATED:\s*(.+)SOURCE', searching_notam)        
    else :
        match = re.search(r'(.+)A\).*CREATED:\s*(.+)\s*SOURCE', searching_notam)
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

    matches = re.finditer(r'RADIUS\s*(\d+)\s*KM.*?(\d[\d\.]{5,10}[NS]).*?(\d[\d\.]{5,10}[EW])|(\d[\d\.]{5,10}[NS]).*?(\d[\d\.]{5,10}[EW])', notam)
    for match in matches:
        try:
            radius = float(match.group(1))
            latitude = match.group(2)
            longitude = match.group(3)
        except:
            radius = None
            latitude = match.group(4)
            longitude = match.group(5)


        match_result = [dms_to_dd(latitude),dms_to_dd(longitude), radius]
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
    
class DataBaseManager:
    def __init__(self,database_path : str,initialize_update = False,retry_for = 0):
        self.initialize_update = initialize_update
        self.database_path = database_path

        self.stripped_notams = list()
        self.as_of = str() 
        self.number_of_notams = int()
        self.updated = bool()

        conn = sqlite3.connect(database_path)
        with conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
        if initialize_update:
            for retry in range(retry_for + 1):
                self.updated = self.update_db()

                if self.updated :
                    break


    def update_db(self):
        scrapped_notams = scrap_notam(NOTAM_URL)

        # checking if scrapping notams was successful
        if scrapped_notams:
            notams, as_of, self.number_of_notams = scrapped_notams
            self.as_of = as_of
            # double checking
            if int(self.number_of_notams) == len(notams):
                print('Updating notams...')
                with conn:
                    cursor = conn.cursor()  
                    cursor.execute("INSERT OR REPLACE INTO db_variables (name,value) VALUES (?, ?)", ('as_of', as_of))
                    cursor.execute('SELECT notam_text FROM notams')
                    notam_texts = cursor.fetchall()
                for notam in notams:
                    if not notam.strip() in notam_texts:
                        save_notam(notam)

            self.stripped_notams = [notam.strip() for notam in notams]   
            return True
        
        print("failed to update.")
        notams, self.number_of_notams = None,None
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM db_variables WHERE name=:as_of",{'as_of':'as_of'})
            self.as_of = cursor.fetchone()[0]
        return False
    
    def get_not_sent_notams(self):
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT notam_db_id,notam_id,notam_text,created_at FROM notams WHERE is_sent=0 
                        ORDER BY STRFTIME("%Y-%m-%d %H:%M:%S", created_at)""")
            not_sent_notams = cursor.fetchall()
        return not_sent_notams
    
    def get_all_coordinated_notams(self):
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT DISTINCT 
                                notam_id
                                FROM notams n
                                INNER JOIN coordinates c ON n.notam_db_id = c.notam_db_id;
                            """)
            fetch = cursor.fetchall()  
            coordinated_notams = list(sum(fetch,()))  
        return coordinated_notams   

    def get_all_coordinates(self,notam_id) -> dict[str,list]:
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

    def get_notam_text(self,notam_id):
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT notam_text FROM notams WHERE notam_id=:notam_id',{'notam_id' : notam_id})
            notam_texts = cursor.fetchall()
            notam_text = ''.join(sum(notam_texts,())[0])

        return notam_text
    
    def set_is_sent(self,notam_db_id):
        with conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notams SET is_sent=1 WHERE notam_db_id=:notam_db_id",{'notam_db_id':notam_db_id})


    def clean_db(self):
        if self.updated:
            print('cleaning the database...')
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute('SELECT notam_db_id,notam_text FROM notams WHERE is_sent=1 AND created_at < datetime(\'now\',\'-2 day\')')
                notams_in_db = cursor.fetchall()  
                for notam_in_db in notams_in_db:

                    notam_db_id,notam_text = notam_in_db
                    notam_text_stripped = notam_text.strip()
                    if notam_text_stripped not in self.stripped_notams:
                        cursor.execute('DELETE FROM notams WHERE notam_db_id=:notam_db_id;',{'notam_db_id':notam_db_id})
