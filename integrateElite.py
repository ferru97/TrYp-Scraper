import os
import pandas as pd
import argparse
import logging
import src.utils.SeleniumUtils as SeleniumUtils
from src.engine.yelp.YelpOnlyAuthorScraper import getYelpUser
import time

INPUT_FILE_DIRECTORY = "input/"
OUTPUT_FILE_DIRECTORY = "output/"
ELITE_COLUMN = "ELITE"

def updateDf(userObj, userDataset, index):
    if userDataset.loc[index, "name"] == "--":
        userDataset.loc[index, "name"] = userObj.name
        userDataset.loc[index, "friends"] = userObj.friends
        userDataset.loc[index, "photos"] = userObj.photos
        userDataset.loc[index, "reviews"] = userObj.reviews
        userDataset.loc[index, "city"] = userObj.city
        userDataset.loc[index, "tagsReviewMap"] = str(userObj.tagsReviewMap)
        userDataset.loc[index, "tagsComplimentMap"] = str(userObj.tagsComplimentMap)
        userDataset.loc[index, "distributionTerrible"] = userObj.distributionTerrible
        userDataset.loc[index, "distributionPoor"] = userObj.distributionPoor
        userDataset.loc[index, "distributionAverage"] = userObj.distributionAverage
        userDataset.loc[index, "distributionVeryGood"] = userObj.distributionVeryGood
        userDataset.loc[index, "distributionExcellent"] = userObj.distributionExcellent
        userDataset.loc[index, "memberSince"] = userObj.memberSince
    if userDataset.loc[index, "ELITE"] == "--":
        userDataset.loc[index, "ELITE"] = userObj.elite

def run(filename):
    inputFilePath = os.path.join(INPUT_FILE_DIRECTORY, filename)
    userDataset = pd.read_csv(inputFilePath)

    if not ELITE_COLUMN in userDataset:
        userDataset[ELITE_COLUMN] = "--"

    logging.info("Scraping process started...")

    driver = SeleniumUtils.getSeleniumInstanceFirefox()
    driver.get("https://yelp.com")
    time.sleep(2.5)

    datasetSize = len(userDataset.index)
    for index, user in userDataset.iterrows():
        if user["ELITE"] != "--" and user["name"] != "--":
            continue
        try:
            userLink = user["link"]
            logging.info(f"{index + 1}/{datasetSize} User: {userLink}")
            userObj = getYelpUser(driver, userLink)
            updateDf(userObj, userDataset, index)
            userDataset.to_csv(inputFilePath, index=False)
        except Exception as e:
            logging.info(f"Error fetching {userLink}, {e}")

    logging.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    parser = argparse.ArgumentParser(description='TrYp Scraper')
    parser.add_argument('--yelp_user_file', required=True, help='input restaurants file name')
    args = parser.parse_args()

    run(args.yelp_user_file)