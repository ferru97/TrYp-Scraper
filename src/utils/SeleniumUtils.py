import os
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver

CHROME_DRIVER_PATH = "resources/chromedriver.exe"
FIREFOX_DRIVER_PATH = "resources/geckodriver.exe"


def getSeleniumInstanceFirefox():
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"
    firefoxService = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=firefoxService)
    return driver
