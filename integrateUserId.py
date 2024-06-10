import os
import pandas as pd
import argparse
import logging
import src.utils.SeleniumUtils as SeleniumUtils
from bs4 import BeautifulSoup
from src.engine.yelp.YelpReviewsAndAuthorScraper import loadNextPage
import math

INPUT_FILE_DIRECTORY = "input2/"
USER_ID = "user_id_link"


def findUsersLink(driver, restaurantLink, reviews, maxRev):
    userNameMap = dict()
    for rev in reviews:
        if rev["user_name"] not in userNameMap:
          userNameMap[rev["user_name"]] = list()
        userNameMap[rev["user_name"]].append(rev)  

    driver.get(restaurantLink)
    expandedHtml = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(expandedHtml, 'html.parser')

    reviewsTag = soup.findAll("li", {"class": "y-css-1jp2syp"})
    for reviewTag in reviewsTag:
        try:
            name = reviewTag.find('a', {"class": "y-css-12ly5yx"}).getText().strip()
            text = reviewTag.find('span', {"class": "raw__09f24__T4Ezm"}).getText().strip()
            if name in userNameMap:
                pass
        except:
            pass




def run(userFile, reviewsFile, restaurantFile):
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
                restaurantUserMap[0].append(review)
                continue
            else:
                if review["restaurant_ID"] not in restaurantUserMap:
                    restaurantUserMap[review["restaurant_ID"]] = list()
                restaurantUserMap[review["restaurant_ID"]].append(review)

    driver = SeleniumUtils.getSeleniumInstanceFirefox()
    for restaurantId, reviews in restaurantUserMap.items():
        try:
            restaurant = restaurantDataset.loc[restaurantDataset['id'] == restaurantId].iloc[0]
            restaurantLink = restaurant["Yelp"]
            findUsersLink(driver, restaurantLink, reviews, 100)
            #reviewsDataset.to_csv(reviewsInputFilePath, index=False)
        except:
            pass  
        


    #reviewsDataset.to_csv(reviewsInputFilePath, index=False)

    #driver = SeleniumUtils.getSeleniumInstanceFirefox()
    #datasetSize = len(userDataset.index)
    #for index, user in userDataset.iterrows():

    logging.info(f"Done!")



if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    parser = argparse.ArgumentParser(description='TrYp Scraper')
    parser.add_argument('--restaurant_file', required=True, help='input restaurants file name')
    parser.add_argument('--yelp_user_file', required=True, help='input restaurants file name')
    parser.add_argument('--yelp_reviews_file', required=True, help='input restaurants file name')
    args = parser.parse_args()

    run(args.yelp_user_file, args.yelp_reviews_file, args.restaurant_file)
