#!/usr/bin/env python

import os
import time
import argparse as ap
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GISAID_FASTA = 'gisaid_cov2020_sequences.fasta'
GISAID_TABLE = 'gisaid_cov2020_acknowledgement_table.xls'


def parse_params():
    p = ap.ArgumentParser(prog='gisaid_EpiCoV_download.py',
                          description="""Download all EpiCoV sequcnes from GISAID""")

    p.add_argument('-u', '--username',
                   metavar='[STR]', nargs=1, type=str, required=True,
                   help="GISAID username")

    p.add_argument('-p', '--password',
                   metavar='[STR]', nargs=1, type=str, required=True,
                   help="GISAID password")

    p.add_argument('-o', '--outdir',
                   metavar='[STR]', type=str, required=False, default=None,
                   help="Output directory")

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

    p.add_argument('-m', '--meta',
                   action='store_true', help='download metadata')

    p.add_argument('--headless',
                   action='store_true', help='turn on headless mode')

    args_parsed = p.parse_args()
    if not args_parsed.outdir:
        args_parsed.outdir = os.getcwd()
    return args_parsed


def download_gisaid_EpiCoV(uname, upass, headless, wd, cs, ce, ss, se, meta_dl):
    # output directory
    if not os.path.exists(wd):
        os.makedirs(wd, exist_ok=True)

    wd = os.path.abspath(wd)
    GISAID_FASTA = f'{wd}/gisaid_cov2020_sequences.fasta'
    GISAID_TABLE = f'{wd}/gisaid_cov2020_acknowledgement_table.xls'
    GISAID_JASON = f'{wd}/gisaid_cov2020_metadata.json'
    metadata = []

    # start fresh
    try:
        os.remove(GISAID_FASTA)
        os.remove(GISAID_TABLE)
    except OSError:
        pass

    print("Opening browser...")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", wd)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/octet-stream,application/excel,application/vnd.ms-excel")
    #profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_profile=profile, options=options)

    # driverwait
    wait = WebDriverWait(driver, 10)

    # open GISAID
    print("Opening website GISAID...")
    driver.get('https://platform.gisaid.org/epi3/frontend')
    time.sleep(7)
    print(driver.title)
    assert 'GISAID' in driver.title

    # login
    print("Logining to GISAID...")
    username = driver.find_element_by_name('login')
    username.send_keys(uname)
    password = driver.find_element_by_name('password')
    password.send_keys(upass)
    driver.execute_script("return doLogin();")
    time.sleep(10)

    # navigate to EpiFlu
    print("Navigating to EpiCoV...")
    epicov_tab = driver.find_element_by_xpath("//div[@id='main_nav']//li[3]/a")
    epicov_tab.click()
    time.sleep(10)
    print("Browsing EpiCoV...")
    browse_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Browse")]')));
    browse_tab.click()
    time.sleep(5)

    # set dates
    date_inputs = driver.find_elements_by_css_selector(
        "div.sys-form-fi-date input")
    dates = (cs, ce, ss, se)
    for dinput, date in zip(date_inputs, dates):
        if date:
            dinput.send_keys(date)

    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(5)

    # download
    print("Downloading the sequence file and the table...")
    button = driver.find_element_by_xpath(
        "/html/body/form/div[5]/div/div[2]/div/div[2]/div[2]/table/tbody/tr/td[3]/button")
    button.click()
    elem = driver.find_element_by_xpath(
        "/html/body/form/div[5]/div/div[3]/div[1]/div/center[1]/a")
    script = elem.get_attribute("onclick")
    driver.execute_script(f"return {script}")
    time.sleep(7)

    # iterate each pages
    if meta_dl:
        page_num = 1
        print("Retrieving metadata...")
        while True:
            tbody = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//tbody[@class='yui-dt-data']"))
            )

            for tr in tbody.find_elements_by_tag_name("tr"):
                td = tr.find_element_by_tag_name("td")
                td.click()

                # have to click the first row twice to start the iframe
                iframe = None
                try:
                    iframe = wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                    )
                except:
                    td.click()
                    iframe = wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                    )

                #iframe = driver.find_element_by_tag_name("iframe")
                driver.switch_to.frame(iframe)

                record_elem = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='packer']"))
                )
                # get metadata
                time.sleep(0.5)
                m = getMetadata(record_elem)
                metadata.append(m)

                # get back
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
                driver.switch_to.default_content()

            print(f"Page {page_num} compeleted.")
            page_num += 1

            # go to the next page
            try:
                button_next_page = driver.find_element_by_css_selector(
                    "a.yui-pg-next")
                button_next_page.click()
                time.sleep(5)
            except:
                break

        # writing metadata to JSON file
        print("Writing metadata...")
        with open(GISAID_JASON, 'w') as outfile:
            json.dump(metadata, outfile)

    # wait for download to complete
    if not os.path.isfile(GISAID_FASTA) or not os.path.isfile(GISAID_TABLE):
        time.sleep(30)
    if not os.path.isfile(GISAID_FASTA) or not os.path.isfile(GISAID_TABLE):
        time.sleep(30)
    if os.path.isfile(GISAID_FASTA) and os.path.isfile(GISAID_TABLE):
        while (os.stat(GISAID_FASTA).st_size == 0):
            time.sleep(5)
        while (os.stat(GISAID_TABLE).st_size == 0):
            time.sleep(5)

    # close driver
    driver.quit()


def getMetadata(record_elem):
    meta = {}
    table = record_elem.find_element_by_tag_name("table")
    last_attr = ""
    for tr in table.find_elements_by_tag_name("tr"):
        if tr.get_attribute("colspan") == "2":
            # skip titles
            continue
        else:
            tds = tr.find_elements_by_tag_name("td")
            if len(tds) == 2:
                attr = tds[0].text.strip(":")
                val = tds[1].text
                if attr == "Address":
                    attr = f"{last_attr} {attr.lower()}"
                    if attr == "Submission Date address":
                        attr = "Submitter address"
                meta[attr] = val
                last_attr = attr
    return meta


def main():
    argvs = parse_params()
    print(f"--- Ingest at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    download_gisaid_EpiCoV(
        argvs.username,
        argvs.password,
        argvs.headless,
        argvs.outdir,
        argvs.colstart,
        argvs.colend,
        argvs.substart,
        argvs.subend,
        argvs.meta
    )
    print("Completed.")


if __name__ == "__main__":
    main()
