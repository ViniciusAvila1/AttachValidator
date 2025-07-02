from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from config import settings
import os

def iniciar_driver(com_download=False):
    options = Options()

    download_path = None
    if com_download:
        download_path = os.path.join(os.getcwd(), "attachments")
        os.makedirs(download_path, exist_ok=True)

        options.add_experimental_option("prefs", {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True  # forçar download de PDFs
        })

    options.add_argument("--start-maximized")

    # Inicializa o driver com as opções configuradas
    driver = webdriver.Chrome(service=Service(), options=options)
    wait = WebDriverWait(driver, 30)

    # Abre o sistema automaticamente
    driver.get(settings.URL_SISTEMA)

    return driver, wait, download_path
