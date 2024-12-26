from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from os import getcwd
from os.path import join as joinpath

def pngify(path : str ,out : str ,delay : int = 2) -> None:

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    #getting the html file
    driver.get(f'{getcwd()}/{path}')

    driver.set_window_size(1350, 960)

    time.sleep(delay)

    driver.save_screenshot(out)

    driver.quit()
