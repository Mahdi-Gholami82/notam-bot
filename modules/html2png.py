import time
from folium import Map
from selenium import webdriver

def pngify(map : Map ,html_path,out : str ,delay : int = 2) -> None:

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)

    map.save(html_path)

    driver.get(html_path)

    driver.set_window_size(1350, 960)

    time.sleep(delay)

    driver.save_screenshot(out)

    driver.quit()
