import os

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
  
driver = webdriver.Chrome(executable_path=os.getenv("CHROMEWEBDRIVER"))  

def pytest_setup_options():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    return options
