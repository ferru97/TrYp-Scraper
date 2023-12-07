import os
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

CHROME_DRIVER_PATH = "resources/chromedriver.exe"
FIREFOX_DRIVER_PATH = "resources/geckodriver.exe"

def getSeleniumInstanceChrome():
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"
    options = webdriver.ChromeOptions()
    options.add_argument("enable-automation");
    options.add_argument("--window-size=1920,1080");
    options.add_argument("--no-sandbox");
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions");
    options.add_argument("--disable-dev-shm-usage");
    options.add_argument("--dns-prefetch-disable");
    options.add_argument("--disable-gpu");
    options.add_argument("--log-level=3")
    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def getSeleniumInstanceFirefox():
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"
    driver = webdriver.Firefox()
    return driver
