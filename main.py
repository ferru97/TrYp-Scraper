import os
import sys
import time
import logging
import argparse
import validators
import pandas as pd
import src.utils.SeleniumUtils as SeleniumUtils
from src.engine.tripadvisor.TripadvisorScraperEngine import *
from urllib.parse import urlparse

INPUT_FILE_DIRECTORY = "input/"
OUTPUT_FILE_DIRECTORY = "output/"

TRIPADVISOR_SOURCE = "tripadvisor"
YELP_SOURCE = "yelp"

DF_TRIPADVISOR_LINK = "TripAdvisor"
YP_LINK = "Yelp"
DF_RESTAURANT_NAME = "Name"
DF_PROCESSED = "Processed"
DF_NUM_REVIEWS = "Processed"

def _loadInputFile(filename):
    inputFilePath = os.path.join(INPUT_FILE_DIRECTORY, filename)
    df = pd.read_csv(inputFilePath)
    if not DF_NUM_REVIEWS in df.columns:
        df[DF_NUM_REVIEWS] = 0
    if not DF_PROCESSED in df.columns:
        df[DF_PROCESSED] = "N"

    df.to_csv(inputFilePath, index=False)    
    logging.info(f'Loaded dataset with {len(df.index)} records')
    return df

def _updateInputFile(filename, df):
    inputFilePath = os.path.join(INPUT_FILE_DIRECTORY, filename)
    df.to_csv(inputFilePath, index=False)   


def _acceptPrivacyPolicy(driver, source):
    if source == TRIPADVISOR_SOURCE:
        domain = "https://www.tripadvisor.com/"
    else:
        domain = "https://www.yelp.it/"

    logging.info(f"Accept privacy policy for [{domain}]' and press ENTER...")
    driver.get(domain)
    input()
        

def _saveData(userData, reviewsData, websiteName):
    reviewsData = [data.getCsvRecord() for data in reviewsData]
    userOutputFile = os.path.join(OUTPUT_FILE_DIRECTORY, f"{websiteName}_restaurants.csv")
    reviewsOutputFile = os.path.join(OUTPUT_FILE_DIRECTORY, f"{websiteName}_restaurants_reviews.csv")
    
    withHeaderRestaurant = os.path.exists(userOutputFile) == False
    outputRestaurantDf = pd.DataFrame(userData)
    outputRestaurantDf.to_csv(userOutputFile, sep='\t', quotechar='"', encoding='utf-8', mode='a', header=withHeaderRestaurant)

    withHeaderReview = os.path.exists(reviewsOutputFile) == False
    outputRviewsDf = pd.DataFrame(reviewsData)
    outputRviewsDf.to_csv(reviewsOutputFile, sep='\t', quotechar='"', encoding='utf-8', mode='a', header=withHeaderReview)  


def processTripadvisor(driver, maxReviews, maxUsersSearchPages, usersList, restaurantLink, restaurantName, restaurantsDataset, index):
    usersInfo, usersReview = scrapeTripadvisorRestaurant(driver, maxReviews, maxUsersSearchPages, usersList, restaurantLink, restaurantName)
    restaurantsDataset.loc[index, DF_PROCESSED] = "Y"
    return  usersInfo, usersReview  

def generateRestaurantUsersMap(usersFileName):
    usersDataset = _loadInputFile(usersFileName)
    restaurantUsersMap = dict()
    for _, row in usersDataset.iterrows():
        if row["restaurant_ID"] not in restaurantUsersMap:
            restaurantUsersMap[row["restaurant_ID"]] = list()
        restaurantUsersMap[row["restaurant_ID"]].append(row["user_name"])
    return restaurantUsersMap


def run(filename, usersFileName, maxReviews, maxUsersSearchPages, source):
    restaurantsDataset = _loadInputFile(filename)
    restaurantUsersMap = generateRestaurantUsersMap(usersFileName)
    datasetSize = len(restaurantsDataset.index)
    driver = SeleniumUtils.getSeleniumInstanceFirefox()
    
    if source == TRIPADVISOR_SOURCE:
        restaurantLinkHeader = DF_TRIPADVISOR_LINK
    else:
        restaurantLinkHeader = YP_LINK

    #_acceptPrivacyPolicy(driver, source)    


    logging.info("Scraping process started...")

    for index, restaurant in restaurantsDataset.iterrows():
        restaurantId = index + 1
        if restaurantId not in restaurantUsersMap:
            logging.info(f"{index+1}/{datasetSize} Restaurant [{restaurantName}] not available in users review file")
            continue

        restaurantLink = str(restaurant[restaurantLinkHeader])
        restaurantName =  restaurant[DF_RESTAURANT_NAME]

        if restaurant[DF_PROCESSED] == "Y":
            logging.info(f"{index+1}/{datasetSize} Restaurant [{restaurantName}] already processed...")
            continue

        if validators.url(restaurantLink) == False:
            logging.error(f"{index+1}/{datasetSize} Invalid link for restaurant [{restaurantName}]!")
            continue

        try:
            timeStart = time.time()
            logging.info(f"{index+1}/{datasetSize} Scraping restaurant [{restaurantName}] from [{source}]...")
            if source == TRIPADVISOR_SOURCE:
                usersInfo, usersReview = processTripadvisor(driver, maxReviews, maxUsersSearchPages, restaurantUsersMap[restaurantId], restaurantLink, restaurantName, restaurantsDataset, index)

            timeEnd = time.time()
            logging.info(f"\tFinished scraping restaurant [{restaurantName}] in {int(timeEnd-timeStart)} seconds")

            if len(usersReview) > 0:
                logging.info("Saving results....")
                _saveData(usersInfo, usersReview, source)
                _updateInputFile(filename, restaurantsDataset)
        except Exception as e:
            logging.warning(f"{index+1}/{restaurant.size} Error while processing restaurant [{restaurantName}]! : {str(e)}")

    
    _saveData(usersInfo, usersReview, source)
    _updateInputFile(filename, restaurantsDataset)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    logging.info("YUMMY SCOUT!\n")

    parser = argparse.ArgumentParser(description='TrYp Scraper')
    parser.add_argument('--users_file', required=True, help='input users file name')
    parser.add_argument('--file', required=True, help='input file name')
    parser.add_argument('--max-reviews', required=True, type=int, help='maximum number of reviews to fetch for each restaurant')
    parser.add_argument('--max-users-search-pages', required=True, type=int, help='maximum of reviews pages to ')
    parser.add_argument('--source', required=True, help='source to scrape from: tripadvisor or yp')
    args = parser.parse_args()

    if args.source not in [TRIPADVISOR_SOURCE, YELP_SOURCE]:
        logging.critical(f"Invalid source [{args.source}], choose between [{TRIPADVISOR_SOURCE}] and [{YELP_SOURCE}]")
        sys.exit()

    run(args.file, args.users_file, args.max_reviews, args.max_users_search_pages, args.source)
