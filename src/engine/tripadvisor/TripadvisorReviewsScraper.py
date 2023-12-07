import re
from bs4 import BeautifulSoup
from src.model.Review import Review
from src.model.Author import Author
from selenium.webdriver.common.by import By
from src.engine.tripadvisor.TripadvisorAuthorScraper import getAuthorObj
import time
import logging

DEFAULT_EMPTY = "--"
TAGS_TEXT_SEPARATOR = " "

def _expandReviews(chrome, retry=True):
    try:
        spans = chrome.find_elements(By.TAG_NAME, 'span')
        spansMore = [span for span in spans if span.get_attribute("onclick") == "widgetEvCall('handlers.clickExpand',event,this);"]
        if len(spansMore) > 0:
            spansMore[0].click()
    except Exception as e:
        logging.error("Expand reviews exception, refreshing page...")
        if retry:
            chrome.refresh()
            time.sleep(2)
            #_nextReviewPage(chrome, False)
        else:
            raise e      


def _getReviewTitle(soup):
    try:
        infoTag = soup.find("div", {"class" : "muQub VrCoN"})
        titleTag = infoTag.findAll("div")
        return titleTag[0].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY 

def _getReviewRatingDate(soup):
    try:
        infoTag = soup.find("div", {"class" : "muQub VrCoN"})
        dateTag = infoTag.findAll("div")
        return dateTag[2].getText(separator=TAGS_TEXT_SEPARATOR).split(":")[1]
    except:
        return DEFAULT_EMPTY   

def _getReviewStars(soup):
    try:
        infoTag = soup.find("div", {"class" : "muQub VrCoN"})
        startsTag = infoTag.find("span")
        starValueClass = [val for val in startsTag["class"] if val.startswith("bubble_")]
        stars = starValueClass[0].split("_")[-1]
        return stars[0] + "." + stars[1]
    except:
        return DEFAULT_EMPTY 

def _getReviewText(soup):
    try:
        infoTag = soup.find("div", {"class" : "muQub VrCoN"})
        reviewTag = infoTag.findAll("div")
        return reviewTag[1].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY  
    
def _getReviewRestaurant(soup):
    try:
        restaurantLink = soup.findAll("a")
        return (restaurantLink[-1])["href"]
    except:
        return DEFAULT_EMPTY                  

def _getReview(reviewSoup, chrome, userName, restaurantName):
    review = Review()
    try:
        review.user = userName
        review.restaurant = restaurantName
        review.title = _getReviewTitle(reviewSoup)
        review.date = _getReviewRatingDate(reviewSoup)
        review.starsValue = _getReviewStars(reviewSoup)
        review.text = _getReviewText(reviewSoup)
        review.restaurnat = _getReviewRestaurant(reviewSoup)
    except Exception as e:
        pass
    
    return review


def loadMoreReviews(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2.5)

    try:
        showMoreButton = driver.find_element(By.XPATH, "//button[contains(@class, 'sOtnj ymEbx')]")
        if showMoreButton is not None:
            showMoreButton.click()
            time.sleep(2.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    except:
        pass


def getUserReviews(restaurantName, userName, userLink, maxReviews, driver):
    logging.info(f"\tFetching reviews of user {userName}")
    driver.get(userLink)
    time.sleep(2)

    expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(expandedHtml, 'html.parser')
    reviewsListTag = soup.find("div", {"id" : "content"})

    stop = False
    reviewsCard = reviewsListTag.findAll("div", {"class" :  re.compile("^trTZI ui_card section")})
    while stop == False and len(reviewsCard) < maxReviews:
        lastReviewsCards = len(reviewsCard)

        loadMoreReviews(driver)
        expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(expandedHtml, 'html.parser')
        reviewsCard = soup.findAll("div", {"class" :  re.compile("^trTZI ui_card section")})
        stop = lastReviewsCards == len(reviewsCard)

    reviews = list()
    for review in reviewsCard:
        reviews.append(_getReview(review, driver, userName, restaurantName))
    
    return reviews