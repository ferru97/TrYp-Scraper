import logging
from bs4 import BeautifulSoup
from src.model.Author import Author
from selenium.webdriver.common.by import By
import time
from pprint import pprint  

DEFAULT_EMPTY = "--"
TAGS_TEXT_SEPARATOR = " "

def _nextReviewPage(driver, retry=True):
    try:
        oldUrl = driver.current_url
        driver.execute_script("document.getElementsByClassName('nav next ui_button primary')[0].click()")
        newUrl = driver.current_url
        time.sleep(0.5)
        driver.get(driver.current_url)
        time.sleep(1)
        return oldUrl == newUrl
    except Exception as e:
        logging.error("Next page exception, refreshing page...")
        logging.error(e)
        if retry:
            driver.refresh()
            time.sleep(2)
            _nextReviewPage(driver, False)
        else:
            raise e

def _selectAllLanguages(driver):  
    divs = driver.find_elements(By.TAG_NAME, 'label')
    allLanguageButton = [div for div in divs if div.get_attribute("for") == "filters_detail_language_filterLang_ALL"]
    if len(allLanguageButton) > 0:
        allLanguageButton[0].click() 


def _openAuthorTab(soup, driver):  
    avatarTag = soup.find("div", {"class" : "memberOverlayLink clickable"})
    avatarTagID = avatarTag["id"]

    divAvatar = driver.find_elements(By.XPATH, f"//div[@id='{avatarTagID}']")
    driver.execute_script("arguments[0].click();", divAvatar[0])   

def _getAuthorName(soup):
    try:
        authorNameTag = soup.find("h3")
        return authorNameTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY     

def _getAuthorLevel(soup):
    try:
        authorLevelTag = soup.find("div", {"class" : "badgeinfo"})
        return authorLevelTag.getText(separator=TAGS_TEXT_SEPARATOR).replace('\n', '')
    except:
        return DEFAULT_EMPTY 

def _getAuthorMeberSince(soup):
    try:
        authorMemberinfo = soup.find("ul", {"class" : "memberdescriptionReviewEnhancements"})
        authorMemberSinceTag = authorMemberinfo.findAll("li")[0]
        return authorMemberSinceTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY 

def _getAuthorCity(soup):
    try:
        authorMemberinfo = soup.find("ul", {"class" : "memberdescriptionReviewEnhancements"})
        authorMemberCityTag = authorMemberinfo.findAll("li")[1]
        return authorMemberCityTag.getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY   

def _getAuthorStat(soup, statClass):
    try:
        reviewInfo = soup.findAll("li", {"class" : "countsReviewEnhancementsItem"})
        for info in reviewInfo:
            infoSpans = info.findAll("span")
            if statClass in (infoSpans[0])["class"]:
                return infoSpans[1].getText(separator=TAGS_TEXT_SEPARATOR)
        return DEFAULT_EMPTY  
    except:
        return DEFAULT_EMPTY    

def _getAuthorTags(soup):
    try:
        tagsList = list()
        tagUl = soup.find("ul", {"class" : "memberTagsReviewEnhancements"})
        tags = tagUl.findAll("li")
        for tag in tags:
            tagsList.append(tag.getText(separator=TAGS_TEXT_SEPARATOR))

        return ", ".join(tagsList)  
    except:
        return DEFAULT_EMPTY         

def _getReviewDistribution(soup, reviewIndex):
    try:
        reviewInfo = soup.findAll("span", {"class" : "rowCountReviewEnhancements rowCellReviewEnhancements"})
        return reviewInfo[reviewIndex].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY   

def _getAuthorLink(soup):
    try:
        allLinks = soup.findAll("a")
        for link in allLinks:
            if "/Profile" in link["href"]:
                return link["href"]
        return DEFAULT_EMPTY
    except:
        return DEFAULT_EMPTY                         

def getAuthorObj(soup, driver):
    author = Author()
    try:
        _openAuthorTab(soup, driver)
        time.sleep(0.5)

        expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(expandedHtml, 'html.parser')

        authorTab = soup.findAll("div", {"class" : "memberOverlay simple container moRedesign"})[-1]

        author.link = _getAuthorLink(authorTab)
        author.name = _getAuthorName(authorTab)
        author.level = _getAuthorLevel(authorTab)
        author.memberSince = _getAuthorMeberSince(authorTab)
        author.city = _getAuthorCity(authorTab) 
        author.contributions = _getAuthorStat(authorTab, "pencil-paper")
        author.helpful = _getAuthorStat(authorTab, "thumbs-up")
        author.cites = _getAuthorStat(authorTab, "globe-world")
        author.photos = _getAuthorStat(authorTab, "camera")
        author.tag = _getAuthorTags(authorTab)
        author.distributionExcellent = _getReviewDistribution(authorTab, 0)
        author.distributionVeryGood = _getReviewDistribution(authorTab, 1)
        author.distributionAverage = _getReviewDistribution(authorTab, 2)
        author.distributionPoor = _getReviewDistribution(authorTab, 3)
        author.distributionTerrible = _getReviewDistribution(authorTab, 4)

        #driver.find_elements(By.TAG_NAME, 'body')[0].click()
    except:
        return Author()  
    return author


def getUsersInfo(soup, driver, maxReviewsPage, usersSet):
    logging.info(f"\tStart finding users")
    usersObjList = list()

    isLastPage = False
    usersFound = 0
    reviewPageNumber = 0
    try:
        _selectAllLanguages(driver)
        time.sleep(1)

        while usersFound < len(usersSet) and reviewPageNumber < maxReviewsPage and isLastPage == False:
            reviewPageNumber += 1
            #_expandReviews(driver)
            #time.sleep(1)

            expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            soup = BeautifulSoup(expandedHtml, 'html.parser')

            detailTag = soup.find("div", {"data-tab" : "TABS_REVIEWS"})
            reviewsListTag = detailTag.find("div", {"data-contextchoice" : "DETAIL"})
            reviews = reviewsListTag.findAll("div", {"class": "review-container"})

            for review in reviews:
                try:
                    newUser = getAuthorObj(review, driver)
                    if newUser.name.lower().strip() in usersSet:
                        usersObjList.append(newUser)
                except:
                    pass
        
            if isLastPage:
                break
            else:
                isLastPage = _nextReviewPage(driver)
    except:
        pass
    return usersObjList