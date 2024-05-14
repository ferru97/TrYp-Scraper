import os
import pandas as pd
import argparse
import logging
import src.utils.SeleniumUtils as SeleniumUtils
from bs4 import BeautifulSoup
import time
import re

INPUT_FILE_DIRECTORY = "input/"
ELITE_COLUMN = "ELITE"

def getElite(driver, link):
    try:
        driver.get("https://www.yelp.com" + link)
        time.sleep(2)
        html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = BeautifulSoup(html, 'html.parser')

        eliteLinks = soup.find_all("a", href=re.compile("user_details_years_elite"))
        for link in eliteLinks:
            span = link.find("span")
            if span is not None:
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
        userName = user["name"]
        if user[ELITE_COLUMN] is not None and str(user[ELITE_COLUMN]).replace(".","").isnumeric() :
            logging.info(f"{index+1}/{datasetSize} Skip user: {userName} already computed")
            continue

        elite = getElite(driver, user["link"])
        logging.info(f"{index+1}/{datasetSize} User: {userName} Elite: {elite}")

        userDataset.loc[index, ELITE_COLUMN] = elite
        userDataset.to_csv(inputFilePath, sep=";", index=False)

    logging.info(f"Done!")




if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    parser = argparse.ArgumentParser(description='TrYp Scraper')
    parser.add_argument('--yelp_user_file', required=True, help='input restaurants file name')
    args = parser.parse_args()

    run(args.yelp_user_file)
