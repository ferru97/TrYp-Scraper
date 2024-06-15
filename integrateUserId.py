import os
import pandas as pd
import argparse
import logging
import src.utils.SeleniumUtils as SeleniumUtils
from bs4 import BeautifulSoup
import math
import time

INPUT_FILE_DIRECTORY = "input2/"
USER_ID = "user_id_link"

def loadNextPage(driver, url, page):
    try:
        nextPage = 10 * page
        nextPageUrl = url + "?start=" + str(nextPage)
        driver.get(nextPageUrl)
        time.sleep(4)

        expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(expandedHtml, 'html.parser')

        return soup
    except Exception as e:
        pass
    return None  

def jaccard_sim(text1, text2):
    set1 = set(text1.split())
    set2 = set(text2.split())
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)


def findUsersLink(driver, restaurantLink, reviews, maxPages, reviewsDf):
    userNameMap = dict()
    for rev in reviews:
        if (rev[1])["user_name"] not in userNameMap:
          reviewsDf.loc[rev[0], "user_id_link"] = "NOT_FOUND_2"
          userNameMap[(rev[1])["user_name"]] = list()
        userNameMap[(rev[1])["user_name"]].append(rev)  

    driver.get(restaurantLink)
    time.sleep(4)
    expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(expandedHtml, 'html.parser')

    totalReviews = len(reviews)
    reviewsFound = 0
    stop = False
    page = 0
    while reviewsFound < totalReviews and stop == False:
        try:
            reviewsTag = soup.findAll("li", {"class": "y-css-1jp2syp"})
            stop, reviewsFound = findReview(reviewsDf, userNameMap, reviewsTag, totalReviews, reviewsFound)
            stop = stop == True or page > maxPages
            page = page + 1
            soup = loadNextPage(driver, restaurantLink, page)
        except:
            pass    
        

def findReview(reviewsDf, userNameMap, reviewsTag, totalReviews, reviewsFound):
    for reviewTag in reviewsTag:
        try:
            nameTag = reviewTag.find('a', {"class": "y-css-12ly5yx"})
            name = nameTag.getText().strip()
            link = nameTag["href"]
            text = reviewTag.find('span', {"class": "raw__09f24__T4Ezm"}).getText().strip()
            if name in userNameMap:
                for userReview in userNameMap[name]:
                    if (userReview[1])["user_id_link"] == "NOT_FOUND" or (userReview[1])["user_id_link"] == "NOT_FOUND_2":
                        similarity = jaccard_sim((userReview[1])["review_text"], text)
                        if similarity >= 0.70:
                            logging.info(f"Found user {name} - Reviews found {reviewsFound}/{totalReviews}")
                            reviewsDf.loc [userReview[0], "user_id_link"] = link
                            reviewsFound = reviewsFound + 1
                            if reviewsFound == totalReviews:
                                return True, reviewsFound
        except:
            continue
    return False, reviewsFound


def run(userFile, reviewsFile, restaurantFile, maxPages):
    restaurantInputPath = os.path.join(INPUT_FILE_DIRECTORY, restaurantFile)
    restaurantDataset = pd.read_csv(restaurantInputPath)

    userInputFilePath = os.path.join(INPUT_FILE_DIRECTORY, userFile)
    userDataset = pd.read_excel(userInputFilePath)

    reviewsInputFilePath = os.path.join(INPUT_FILE_DIRECTORY, reviewsFile)
    reviewsDataset = pd.read_csv(reviewsInputFilePath)

    restaurantUserMap = dict()
    restaurantUserMap[0] = list()
    for index, review in reviewsDataset.iterrows():
        if review[USER_ID] == "NOT_FOUND":
            if  math.isnan(review["restaurant_ID"]):
                restaurantUserMap[0].append((index,review))
                continue
            else:
                if review["restaurant_ID"] not in restaurantUserMap:
                    restaurantUserMap[review["restaurant_ID"]] = list()
                restaurantUserMap[review["restaurant_ID"]].append((index,review))

    driver = SeleniumUtils.getSeleniumInstanceFirefox()
    size = len(restaurantUserMap)
    i = 1
    for restaurantId, reviews in restaurantUserMap.items():
        try:
            restaurant = restaurantDataset.loc[restaurantDataset['id'] == restaurantId].iloc[0]
            logging.info(f"Restaurant {i}/{size}")
            restaurantLink = restaurant["Yelp"]
            findUsersLink(driver, restaurantLink, reviews, maxPages, reviewsDataset)
            i = i + 1
            logging.info(f"Saveing...")
            reviewsDataset.to_csv(reviewsInputFilePath, index=False)
        except:
            pass  


    logging.info(f"Done!")



if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    parser = argparse.ArgumentParser(description='TrYp Scraper')
    parser.add_argument('--restaurant_file', required=True, help='input restaurants file name')
    parser.add_argument('--yelp_user_file', required=True, help='input restaurants file name')
    parser.add_argument('--yelp_reviews_file', required=True, help='input restaurants file name')
    parser.add_argument('--yelp_reviews_max_page', required=True, help='input restaurants file name')
    args = parser.parse_args()

    run(args.yelp_user_file, args.yelp_reviews_file, args.restaurant_file, int(args.yelp_reviews_max_page))