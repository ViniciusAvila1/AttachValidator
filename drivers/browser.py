from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from config import settings

def iniciar_driver():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 30)
    driver.get(settings.URL_SISTEMA)
    return driver, wait
