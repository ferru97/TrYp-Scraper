import os
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from fake_useragent import UserAgent
from selenium import webdriver

CHROME_DRIVER_PATH = "resources/chromedriver.exe"
FIREFOX_DRIVER_PATH = "resources/geckodriver.exe"


def getSeleniumInstanceFirefox():
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"
    ua = UserAgent()
    user_agent = ua.random
    options = Options()
    options.add_argument("user-agent="+user_agent)
    firefoxService = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=firefoxService, options=options)
    return driver
