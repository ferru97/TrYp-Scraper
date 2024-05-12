import os
import pandas as pd
import argparse
import logging
import src.utils.SeleniumUtils as SeleniumUtils
from bs4 import BeautifulSoup
import time

INPUT_FILE_DIRECTORY = "input/"
ELITE_COLUMN = "ELITE"

def getElite(driver, link):
    try:
        driver.get("https://www.yelp.com" + link)
        time.sleep(2)
        html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(html, 'html.parser')

        links = soup.findAll("a")
        for link in links:
            if "/user_details_years_elite" in link["href"]:    
                span = link.find("span")  
                return span.getText().split()[1]
        return "0"
    except:
        return "0"


def run(filename):
    inputFilePath = os.path.join(INPUT_FILE_DIRECTORY, filename)
    userDataset = pd.read_csv(inputFilePath, delimiter=";")

    if not ELITE_COLUMN in userDataset:
        userDataset[ELITE_COLUMN] = ""

    logging.info("Scraping process started...")

    driver = SeleniumUtils.getSeleniumInstanceFirefox()
    datasetSize = len(userDataset.index)
    for index, user in userDataset.iterrows():
        if len(user[ELITE_COLUMN]) > 0:
            continue

        userName = user["name"]
        logging.info(f"{index+1}/{datasetSize} User: {userName}")

        elite = getElite(driver, user["link"])
        print(elite)
        userDataset.loc[index, ELITE_COLUMN] = elite
        userDataset.to_csv(inputFilePath)

    logging.info(f"Done!")



if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    parser = argparse.ArgumentParser(description='TrYp Scraper')
    parser.add_argument('--yelp_user_file', required=True, help='input restaurants file name')
    args = parser.parse_args()

    run(args.yelp_user_file)
