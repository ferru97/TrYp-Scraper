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

def _getReviewRestaurantNameAndLink(soup):
    try:
        retuaurantTag = soup.find('div', {'class': "yelp-emotion-16lye5o"})
        restaurantLink = retuaurantTag.find('a')
        return restaurantLink.getText(separator=TAGS_TEXT_SEPARATOR), restaurantLink["href"]
    except Exception as e:
        return DEFAULT_EMPTY, DEFAULT_EMPTY
    
def _getReviewRestaurantCategory(soup):
    try:
        categoryies = list()
        retuaurantTag = soup.find('div', {'class': "yelp-emotion-16lye5o"})
        restaurantLink = retuaurantTag.findAll('a')
        for link in restaurantLink:
            if "/search?" in link["href"]:
                categoryies.append(link.getText(separator=TAGS_TEXT_SEPARATOR))
        return ",".join(categoryies)
    except Exception as e:
        return DEFAULT_EMPTY
    
def _getReviewRestaurantLocation(soup):
    try:
        retuaurantTag = soup.find('div', {'class': "yelp-emotion-16lye5o"})
        restaurantInfo = retuaurantTag.findAll('p')
        return restaurantInfo[1].getText(separator=TAGS_TEXT_SEPARATOR)
    except Exception as e:
        return DEFAULT_EMPTY 

def _getReviewDate(soup):
    try:
        restuaurantTagInfo = soup.find('div', {'class': "yelp-emotion-19pbem2"})
        dateSpan = restuaurantTagInfo.find("span", {"class" : "yelp-emotion-v293gj"})
        return dateSpan.getText(separator=TAGS_TEXT_SEPARATOR)
    except Exception as e:
        return DEFAULT_EMPTY 
    
def _getReviewStars(soup):
    try:
        restuaurantTagInfo = soup.find('div', {'class': "css-10n911v"})
        starTag = restuaurantTagInfo.find("div", {"class" : "yelp-emotion-9tnml4"})
        return starTag["aria-label"].split(" ")[0]
    except Exception as e:
        return DEFAULT_EMPTY     

def _getReviewtext(soup):
    try:
        paragraphs = soup.findAll("p")
        for p in paragraphs:
            if "comment_" in " ".join(p["class"]):
                return p.getText(separator=TAGS_TEXT_SEPARATOR)
    except Exception as e:
        pass
    return DEFAULT_EMPTY  

def _getReviewLikes(soup, index):
    try:
        likeButtons = soup.findAll("span", {'class':'yelp-emotion-kbraxm'})
        info = likeButtons[index].getText(separator=TAGS_TEXT_SEPARATOR).split(" ")
        return info[2]
    except Exception as e:
        pass
    return DEFAULT_EMPTY  

def _loadNextPage(soup, driver, url, page):
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

def _getReview(soup, userLink):
    review = Review()
    try:
        restaurantName, restaurantLink = _getReviewRestaurantNameAndLink(soup)
        review.restaurantLink = restaurantLink
        review.restaurant = restaurantName
        review.category = _getReviewRestaurantCategory(soup)
        review.locaition = _getReviewRestaurantLocation(soup)
        review.date = _getReviewDate(soup)
        review.starsValue = _getReviewStars(soup) 
        review.text = _getReviewtext(soup)
        review.useful = _getReviewLikes(soup, 0)
        review.funny = _getReviewLikes(soup, 1)
        review.cool = _getReviewLikes(soup, 2)
        review.user = userLink
    except Exception as e:
        pass
    return review

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
        topCategoryList = soup.findAll('li', {'class':'css-1dnq2xk'})
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
        divs = soup.findAll("div", {"class" : "css-1qn0b6x"})
        for div in divs:
            divContent = div.getText(separator=TAGS_TEXT_SEPARATOR)
            paragraph = div.findAll("p")
            if len(paragraph) == 2 and ('Yelping since' in divContent or 'Su Yelp da' in divContent):
                return paragraph[1].getText(separator=TAGS_TEXT_SEPARATOR)
    except:
        return DEFAULT_EMPTY
    return DEFAULT_EMPTY   

def getYelpUserReviews(restaurantName, userObj, maxReviews, driver):
    logging.info(f"\tFetching reviews of user {userObj.name}")
    baseUrl = urlparse(driver.current_url).netloc
    if "https" not in baseUrl:
        baseUrl = "https://" + baseUrl
    driver.get(baseUrl + userObj.link)
    time.sleep(2)

    expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(expandedHtml, 'html.parser')

    userObj.tagsReviewMap = _getTagsReview(soup)
    userObj.tagsComplimentMap = _getTagsCompliment(soup)
    userObj.topCategoryMap = _getTopCategoryies(soup)
    userObj.distributionTerrible = _getStarReview(soup, "1")
    userObj.distributionPoor = _getStarReview(soup, "2")
    userObj.distributionAverage = _getStarReview(soup, "3")
    userObj.distributionVeryGood = _getStarReview(soup, "4")
    userObj.distributionExcellent = _getStarReview(soup, "5")
    userObj.memberSince = _getOnYelpSince(soup)

    reviewsUrl = driver.current_url.replace("user_details", "user_details_reviews_self")
    driver.get(reviewsUrl)
    time.sleep(2)  

    expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(expandedHtml, 'html.parser')
    
    lastPage = False
    page = 0
    reviews = list()
    while len(reviews) < maxReviews and lastPage == False:
        reviewsBox = soup.findAll('li', {'class':'yelp-emotion-3xeaoc'})
        for reviewBox in reviewsBox:
            reviewObj = _getReview(reviewBox, userObj.link)
            reviews.append(reviewObj)

        page = page + 1
        lastPage, soup =_loadNextPage(soup, driver, reviewsUrl, page)
    
    return reviews