import re
from bs4 import BeautifulSoup
from src.model.Review import Review
from src.model.Author import Author
from selenium.webdriver.common.by import By
from src.engine.tripadvisor.TripadvisorAuthorScraper import getAuthorObj
import time
import logging
from urllib.parse import urlparse

DEFAULT_EMPTY = "--"
TAGS_TEXT_SEPARATOR = " "           

def loadNextPage(soup, driver, url, page):
    try:
        nextPage = 10 * page
        nextPageUrl = url + "&start=" + str(nextPage)
        driver.get(nextPageUrl)
        time.sleep(2.5)

        expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(expandedHtml, 'html.parser')

        pageInfo = soup.find("div", {'class':'css-1aq64zd'})
        currentPageInfo = pageInfo.getText(separator=TAGS_TEXT_SEPARATOR).split(" ")
        isLastPage = int(currentPageInfo[0]) >= int(currentPageInfo[2]) 
        return isLastPage, soup
    except Exception as e:
        pass
    return True, None  

def _getTagsReview(soup):
    tagsMap = dict()
    try:
        tags = soup.findAll('div', {'data-testid':re.compile('^impact-count')})
        for tag in tags:
            tagsInfo = [t.strip() for t in tag.getText(separator=TAGS_TEXT_SEPARATOR).strip().split(" ")]
            if len(tagsInfo) > 0:
                key = ' '.join(tagsInfo[0:-1]).strip()
                tagsMap["reviewTag_"+key] = tagsInfo[-1]
    except Exception as e:
        pass
    
    return tagsMap

def _getTagsCompliment(soup):
    tagsMap = dict()
    try:
        tags = soup.findAll('div', {'data-testid':re.compile('^impact-compliment')})
        for tag in tags:
            tagsInfo = [t.strip() for t in tag.getText(separator=TAGS_TEXT_SEPARATOR).strip().split(" ")]
            if len(tagsInfo) > 0:
                key = ' '.join(tagsInfo[0:-1]).strip()
                tagsMap["complimentTag_"+key] = tagsInfo[-1]
    except Exception as e:
        pass
    
    return tagsMap

def _getStarReview(soup, stars):
    try:
        reToFind = '^' + stars + " st"
        starsReviews = soup.find('div', {'aria-label':re.compile(reToFind)})
        return starsReviews["aria-label"].strip().split(" ")[-1].replace("(","").replace(")","")
    except Exception as e:
        return DEFAULT_EMPTY
    
def _getTopCategoryies(soup):
    try:
        categoryInfoMap = dict()
        topCategoryList = soup.findAll('li', {'class':'y-css-1cnhxbi'})
        for category in topCategoryList:
            categoryInfo = [c.strip() for c in category.getText(separator=TAGS_TEXT_SEPARATOR).strip().split(" ")]
            if len(categoryInfo) > 0:
                key = ' '.join(categoryInfo[0:-1]).strip()
                categoryInfoMap["topCategory_"+key] = categoryInfo[-1].replace("(","").replace(")","")
        return categoryInfoMap 
    except Exception as e:
        return DEFAULT_EMPTY    
    
def _getOnYelpSince(soup):
    try:
        divs = soup.findAll("div", {"class" : "y-css-1iy1dwt"})
        for div in divs:
            divContent = div.getText(separator=TAGS_TEXT_SEPARATOR)
            paragraph = div.findAll("p")
            if len(paragraph) == 2 and ('Yelping since' in divContent or 'Su Yelp da' in divContent):
                return paragraph[1].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY
    return DEFAULT_EMPTY  

def _getElite(soup):
    try:
        spans = soup.findAll("span", {"class": "y-css-1cn4gbs"})
        for span in spans:
            text = span.getText()
            if "Elite" in text:
                return text.split()[1]
        return "0.0"
    except:
        return "0.0"


def getAuthorName(soup):
    try:
        nameTag = soup.find("div", {"class": "y-css-blvhhm"})
        return nameTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY


def getAuthorLocation(soup):
    try:
        divs = soup.findAll("div", {"class": "y-css-1iy1dwt"})
        for div in divs:
            divContent = div.getText(separator=TAGS_TEXT_SEPARATOR)
            paragraph = div.findAll("p")
            if len(paragraph) == 2 and ('Location' in divContent or 'Sede' in divContent):
                return paragraph[1].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY


def getAuthorStats(soup, statsName):
    try:
        stat = soup.find("div", {"aria-label": statsName})
        return stat.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY

def getYelpUser(driver, link):
    logging.info(f"\tFetching user {link}")
    baseUrl = "https://yelp.com"
    driver.get(baseUrl + link)
    time.sleep(2.5)

    expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(expandedHtml, 'html.parser')

    userObj = Author()
    userObj.name = getAuthorName(soup)
    userObj.friends = getAuthorStats(soup, "Friends")
    userObj.photos = getAuthorStats(soup, "Photos")
    userObj.reviews = getAuthorStats(soup, "Reviews")
    userObj.city = getAuthorLocation(soup)
    userObj.tagsReviewMap = _getTagsReview(soup)
    userObj.tagsComplimentMap = _getTagsCompliment(soup)
    userObj.topCategoryMap = _getTopCategoryies(soup)
    userObj.distributionTerrible = _getStarReview(soup, "1")
    userObj.distributionPoor = _getStarReview(soup, "2")
    userObj.distributionAverage = _getStarReview(soup, "3")
    userObj.distributionVeryGood = _getStarReview(soup, "4")
    userObj.distributionExcellent = _getStarReview(soup, "5")
    userObj.memberSince = _getOnYelpSince(soup)
    userObj.elite = _getElite(soup)
    
    return userObj