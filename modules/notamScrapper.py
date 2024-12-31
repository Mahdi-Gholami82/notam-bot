import re
from requests import get
from bs4 import BeautifulSoup


def scrap_notam(notam_link: str) -> iter:
    try:
        html_text = get(notam_link).text
        soup = BeautifulSoup(html_text,'lxml')
        notams = soup.find_all('td',class_="textBlack12",valign="top",width='')
        find_non = soup.find('td',class_="textRed12",align="",height="").text
        number_of_notams = re.search(r'Number of NOTAMs:\s*?(\d+)',find_non).group(1)
        print(f'{number_of_notams=}')
        notams = [notam.text for notam in notams]
        as_of = soup.find('span',class_='textRed12').text
        return notams,as_of,int(number_of_notams)
    except Exception as e:
        print(f'scrapping failed : {e}')
        return None