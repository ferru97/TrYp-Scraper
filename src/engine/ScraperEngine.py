import re
import logging
from bs4 import BeautifulSoup
from src.engine.tripadvisor.TripadvisorReviewsScraper import *
from src.engine.tripadvisor.TripadvisorAuthorScraper import *
from pprint import pprint      
import time            

TRIPADVISOR_SOURCE = "tripadvisor"

def getUserSet(usersList):
    usersSet = set()
    for user in usersList:
        usersSet.add(user.lower().strip())
    return usersSet

def logUsersNotFound(usersInfo, allUsersSet):
    logging.info(f"\tFound {len(usersInfo)} users out of [{len(allUsersSet)}]")
    usersFound = set()
    for user in usersInfo:
        usersFound.add(user.name)

    usersNotFound = list()
    for user in allUsersSet:
        if user not in usersFound:
            usersNotFound.append(user)

    if len(usersNotFound) > 0:
        logging.info(f"\tUsers not found: {usersNotFound}")


def scrapeRestaurant(source, driver, maxReviews, maxUsersSearchPages, usersList, restaurantLink, restaurantName):
    driver.get(restaurantLink)
    time.sleep(2)

    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(html, 'html.parser')
    usersSet = getUserSet(usersList)

    if source == TRIPADVISOR_SOURCE:
        usersInfo = getTripadvisorUsersInfo(soup, driver, maxUsersSearchPages, usersSet) 
    logUsersNotFound(usersInfo, usersSet)

    usersReview = list()
    for user in usersInfo:
        if source == TRIPADVISOR_SOURCE:
            usersReviewsList = getUserTripadvisorReviews(restaurantName, user.name, user.link, maxReviews, driver)
        usersReview.append(usersReviewsList)
    
    usersReview = [item for sublist in usersReview for item in sublist]
    
    #getUserReviews(restaurantName, "BeatrizG2", "/Profile/BeatrizG2", maxReviews, driver)

    logging.info(f"\tFound {len(usersReview)} reviews for restaurant [{restaurantName}]")

    return usersInfo, usersReview