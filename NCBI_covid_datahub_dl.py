#!/usr/bin/env python3

__author__ = "Po-E Li, B10, LANL"
__copyright__ = "LANL 2020"
__license__ = "GPL"
__version__ = "22.03.21"
__email__ = "po-e@lanl.gov"

import os
import time
import sys
import argparse as ap
import json
import logging
from tkinter import W
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M',
)

def parse_params():
    p = ap.ArgumentParser(prog='gisaid_EpiCoV_downloader.py',
                          description="""Download EpiCoV sequences from GISAID. WARNING: By using this software you agree GISAID's Terms of Use and reaffirm your understanding of these terms.""")

    p.add_argument('-o', '--outdir',
                   metavar='[STR]', type=str, required=False,
                   help="Output directory")

    p.add_argument('-l', '--location',
                   metavar='[STR]', type=str, required=False, default=None,
                   help="sample location")

    p.add_argument('-ht', '--host',
                   metavar='[STR]', type=str, required=False, default='Human',
                   help="Specify a host of the sample. Default is human.")

    p.add_argument('-cs', '--colstart',
                   metavar='[YYYY-MM-DD]', type=str, required=False, default=None,
                   help="collection starts date")

    p.add_argument('-ce', '--colend',
                   metavar='[YYYY-MM-DD]', type=str, required=False, default=None,
                   help="collection ends date")

    p.add_argument('-ss', '--substart',
                   metavar='[YYYY-MM-DD]', type=str, required=False, default=None,
                   help="submitssion starts date")

    p.add_argument('-se', '--subend',
                   metavar='[YYYY-MM-DD]', type=str, required=False, default=None,
                   help="submitssion ends date")

    p.add_argument('-t', '--timeout',
                   metavar='[INT]', type=int, required=False, default=90,
                   help="set action timeout seconds. Default is 90 secs.")

    p.add_argument('-r', '--retry',
                   metavar='[INT]', type=int, required=False, default=5,
                   help="retry how many times when the action fails. Default is 5 times.")

    p.add_argument('-i', '--interval',
                   metavar='[INT]', type=int, required=False, default=3,
                   help="time interval between retries in second(s). Default is 3 seconds.")

    p.add_argument('-nnd', '--nonextstraindata',
                   action='store_true', help='Do not download nextstrain data')

    p.add_argument('--normal',
                   action='store_true', help='run firefox in normal mode.')

    p.add_argument('--ffbin',
                   metavar='[STR]', type=str, required=False,
                   help="Specify the path of firefox binary.")

    p.add_argument('--version',
                   action='store_true', help='print version number.')

    args_parsed = p.parse_args()
    if not args_parsed.outdir:
        args_parsed.outdir = os.getcwd()
        logging.info(f"Output directory set to {args_parsed.outdir}...")
    
    return args_parsed


def download_ncbi_datahub(
        normal,    # normal mode (quite)
        wd,        # output dir
        loc,       # location
        host,      # host
        cs,        # collection start date
        ce,        # collection end date
        ss,        # submission start date
        se,        # submission end date
        to,        # timeout in sec
        rt,        # num of retry
        iv,        # interval in sec
        nnd,       # do not download nextstrain data
        ffbin      # firefox binary path
    ):
    """Download sequences and metadata from EpiCoV GISAID"""

    # output directory
    if not os.path.exists(wd):
        os.makedirs(wd, exist_ok=True)


    logging.info("Opening browser...")
    
    options = FirefoxOptions()

    if not normal:
        options.add_argument("--headless")

    # MIME types
    mime_types = "application/octet-stream"
    mime_types += ",application/excel,application/vnd.ms-excel"
    mime_types += ",application/pdf,application/x-pdf"
    mime_types += ",application/x-bzip2"
    mime_types += ",application/x-gzip,application/gzip"

    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", wd)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
    options.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
    options.set_preference("pdfjs.disabled", True)
    
    serv = None
    if ffbin:
        options.binary_location = ffbin
        serv = Service(ffbin)

    driver = webdriver.Firefox(options=options)

    # driverwait
    # driver.implicitly_wait(30)
    wait = WebDriverWait(driver, to)

    # open GISAID
    logging.info("Opening website SARS-CoV-2 Data Hub...")
    driver.get('https://www.ncbi.nlm.nih.gov/labs/virus/vssi/#/virus?SeqType_s=Nucleotide&VirusLineage_ss=SARS-CoV-2,%20taxid:2697049')
    logging.info(driver.title)
    assert 'NCBI' in driver.title

    time.sleep(5)

    # click Download button
    logging.info("Clicking Download button...")
    dl_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@class='ncbi-report-download']")))
    dl_button.click()

    # select CSV format
    logging.info("Selecting format...")
    dl_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//label[contains(text(), "CSV format")]')))
    dl_button.click()

    dl_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[contains(text(), "Next")]')))
    dl_button.click()

    # selecting Download All Records
    logging.info("Selecting all records...")
    # dl_button = wait.until(EC.element_to_be_clickable(
    #     (By.XPATH, '//button[contains(text(), "Download All Records")]')))
    # dl_button.click()

    dl_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[contains(text(), "Next")]')))
    dl_button.click()

    # selecting SRA Accession and Country
    logging.info("Selecting columns...")

    actions = ActionChains(driver)

    # checkbox SRA Accession
    # dl_button = driver.find_element_by_xpath('/html/body/ngb-modal-window/div/div/div[2]/uswds-ncbi-app-muti-step-form/div/div/div/span[3]/form/div/div[1]/div[1]/div[2]/label')
    dl_button = driver.find_element(by=By.XPATH, value='/html/body/ngb-modal-window/div/div/div[2]/uswds-ncbi-app-muti-step-form/div/div/div/span[3]//label[contains(text(), "SRA Accession")]')
    actions.move_to_element(dl_button).click()
    # checkbox Country
    # dl_button = driver.find_element_by_xpath('/html/body/ngb-modal-window/div/div/div[2]/uswds-ncbi-app-muti-step-form/div/div/div/span[3]/form/div/div[1]/div[3]/div[1]/label')
    dl_button = driver.find_element(by=By.XPATH, value='/html/body/ngb-modal-window/div/div/div[2]/uswds-ncbi-app-muti-step-form/div/div/div/span[3]//label[contains(text(), "Country")]')
    actions.move_to_element(dl_button).click()
    actions.perform()
    # button Download
    dl_button = driver.find_element(by=By.XPATH, value='/html/body/ngb-modal-window/div/div/div[2]/uswds-ncbi-app-muti-step-form/div/div/div/span[3]/button[2]')
    dl_button.click()
    #actions.move_to_element(dl_button).click()

    time.sleep(5)

    logging.info("Downloading...")

    # Opening Firefox downloading window
    fn = wait_downloaded_filename(wait, driver, 600)
    logging.info(f" -- downloaded")

    # close driver
    driver.quit()

def wait_downloaded_filename(wait, driver, waitTime=180):
    # logging.info(f"Opening Firefox downloading window...")
    driver.execute_script("window.open()")
    wait.until(EC.new_window_is_opened)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("about:downloads")
    time.sleep(1)

    endTime = time.time()+waitTime
    while True:
        try:
            # progress = driver.execute_script("return document.querySelector('.downloadContainer progress:first-of-type').value")
            fileName = driver.execute_script("return document.querySelector('.downloadContainer description:first-of-type').value")
            dldetail = driver.execute_script("return document.querySelector('.downloadDetailsNormal').value")
            logging.info(f" -- downloading to {fileName}")

            while "time left" in dldetail:
                time.sleep(1)
                dldetail = driver.execute_script("return document.querySelector('.downloadDetailsNormal').value")
                # progress = driver.execute_script("return document.querySelector('.downloadContainer progress:first-of-type').value")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
            return fileName
        except:
            logging.info(f" -- retry in 1 sec")
            time.sleep(1)
            pass

        if time.time() > endTime:
            logging.info(f" -- timeout")
            break

def main():
    argvs = parse_params()

    if argvs.version:
        print(f"v{__version__}")
        exit(0)

    logging.info(f"GISAID EpiCoV Utility v{__version__}")
    download_ncbi_datahub(
        argvs.normal,
        argvs.outdir,
        argvs.location,
        argvs.host,
        argvs.colstart,
        argvs.colend,
        argvs.substart,
        argvs.subend,
        argvs.timeout,
        argvs.retry,
        argvs.interval,
        argvs.nonextstraindata,
        argvs.ffbin
    )
    logging.info("Completed.")


if __name__ == "__main__":
    main()
