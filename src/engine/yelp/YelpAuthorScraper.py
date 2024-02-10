import logging
from bs4 import BeautifulSoup
from src.model.Author import Author
from selenium.webdriver.common.by import By
import time
import logging
from pprint import pprint  

DEFAULT_EMPTY = "--"
TAGS_TEXT_SEPARATOR = " "

def _nextReviewPage(driver, page):
    try:
        url = driver.current_url
        url = url.split("?")[0]
        url = url + "?start=" + str(10*page)
        driver.get(url)
        time.sleep(2)
        
        hmtl = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(hmtl, 'html.parser')

        navigator = soup.find("div", {"aria-label": "Pagination navigation"})
        pageLimitTag = navigator.find("span", {"class": "css-chan6m"})
        pageLimits = pageLimitTag.text.split("of")

        return int(pageLimits[0].strip()) >= int(pageLimits[1].strip())
    except:
        return True


def getAuthorNameAndLink(soup):
    try:
        links = soup.findAll("a")
        for link in links:
            if "/user_details" in link["href"] and link.getText(separator=TAGS_TEXT_SEPARATOR).strip() != '':
                return link.getText(separator=TAGS_TEXT_SEPARATOR), link["href"]
    except:
        return DEFAULT_EMPTY, DEFAULT_EMPTY 
    

def getAuthorLocation(soup):
    try:
        location = soup.find("span", {"class" : "css-qgunke"})
        return location.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY 
    

def getAuthorStats(soup, statsName):
    try:
        stat = soup.find("div", {"aria-label" : statsName})
        return stat.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY     


def getAuthorObj(soup):
    author = Author()
    try:
        name, link = getAuthorNameAndLink(soup)
        author.link = link
        author.name = name
        author.friends = getAuthorStats(soup, "Friends")
        author.photos = getAuthorStats(soup, "Photos")
        author.reviews = getAuthorStats(soup, "Reviews")
        author.city = getAuthorLocation(soup)
    except:
        return Author()  
    return author 


def getYelpUsersInfo(soup, driver, maxReviewsPage, usersSet):
    logging.info(f"\tStart finding users")
    usersObjList = list()

    usersFound = set()
    isLastPage = False
    currentPage = 0
    while len(usersObjList) < len(usersSet) and currentPage < maxReviewsPage and isLastPage == False:
        hmtl = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(hmtl, 'html.parser')

        reviewsListTag = soup.find(attrs={'id':'reviews'})
        if reviewsListTag is None:
            logging.warning(f"No more users available")
            break;
        
        for review in reviewsListTag.findAll("li"):
            try:
                newUser = getAuthorObj(review)
                if  newUser.link is not DEFAULT_EMPTY and newUser.link not in usersFound:
                    usersFound.add(newUser.link)
                    usersObjList.append(newUser)
            except:
                pass

        if isLastPage:
            break
        else:
            currentPage = currentPage + 1
            isLastPage = _nextReviewPage(driver, currentPage)

    return usersObjList
