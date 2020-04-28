#!/usr/bin/env python

import os
import time
import sys
import argparse as ap
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_params():
    p = ap.ArgumentParser(prog='gisaid_EpiCoV_downloader.py',
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

    p.add_argument('-cg', '--complete',
                   action='store_true', help='complete genome only')

    p.add_argument('-hc', '--highcoverage',
                   action='store_true', help='high coverage only')

    p.add_argument('-t', '--timeout',
                   metavar='[INT]', type=int, required=False, default=90,
                   help="set action timeout seconds. Default is 90 secs.")

    p.add_argument('-r', '--retry',
                   metavar='[INT]', type=int, required=False, default=5,
                   help="retry how many times when the action fails. Default is 5 times.")

    p.add_argument('-i', '--interval',
                   metavar='[INT]', type=int, required=False, default=3,
                   help="time interval between retries in second(s). Default is 3 seconds.")

    p.add_argument('-m', '--meta',
                   action='store_true', help='download metadata')

    p.add_argument('--headless',
                   action='store_true', help='turn on headless mode')

    args_parsed = p.parse_args()
    if not args_parsed.outdir:
        args_parsed.outdir = os.getcwd()
    return args_parsed


def download_gisaid_EpiCoV(uname, upass, headless, wd, cs, ce, ss, se, cg, hc, to, rt, iv, meta_dl):
    """Download sequences and metadata from EpiCoV GISAID"""

    # output directory
    if not os.path.exists(wd):
        os.makedirs(wd, exist_ok=True)

    wd = os.path.abspath(wd)
    GISAID_FASTA = f'{wd}/sequences.fasta.bz2'
    GISAID_TABLE = f'{wd}/gisaid_cov2020_acknowledgement_table.xls'
    GISAID_JASON = f'{wd}/gisaid_cov2020_metadata.json'
    GISAID_TSV   = f'{wd}/metadata.tsv.bz2'
    metadata = []

    # MIME types
    mime_types = "application/octet-stream"
    mime_types += ",application/excel,application/vnd.ms-excel"
    mime_types += ",application/pdf,application/x-pdf"
    mime_types += ",application/x-bzip2"

    # start fresh
    try:
        os.remove(GISAID_FASTA)
        os.remove(GISAID_TSV)
    except OSError:
        pass

    print("Opening browser...")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", wd)
    profile.set_preference(
        "browser.helperApps.neverAsk.saveToDisk", mime_types)
    profile.set_preference(
        "plugin.disable_full_page_plugin_for_types", mime_types)
    profile.set_preference("pdfjs.disabled", True)

    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_profile=profile, options=options)

    # driverwait
    driver.implicitly_wait(20)
    wait = WebDriverWait(driver, to)

    # open GISAID
    print("Opening website GISAID...")
    driver.get('https://platform.gisaid.org/epi3/frontend')
    waiting_sys_timer(wait)
    print(driver.title)
    assert 'GISAID' in driver.title

    # login
    print("Logining to GISAID...")
    username = driver.find_element_by_name('login')
    username.send_keys(uname)
    password = driver.find_element_by_name('password')
    password.send_keys(upass)
    driver.execute_script("return doLogin();")

    waiting_sys_timer(wait)

    # navigate to EpiFlu
    print("Navigating to EpiCoV...")
    epicov_tab = driver.find_element_by_xpath("//div[@id='main_nav']//li[3]/a")
    epicov_tab.click()

    waiting_sys_timer(wait)

    # download from partner downloads
    print("Clicking partner downloads...")
    pd_button = driver.find_element_by_xpath('//div[contains(text(), "partner downloads")]')
    driver.execute_script("arguments[0].scrollIntoView();", pd_button)

    # have to click the first row twice to start the iframe
    iframe = None
    retry = 1
    while retry <= rt:
        try:
            pd_button.click()
            iframe = driver.find_element_by_xpath("//iframe")
            if iframe:
                break
            else:
                raise
        except:
            print(f"retrying...#{retry} in {iv} sec(s)")
            if retry == rt:
                print("Failed")
                sys.exit(1)
            else:
                time.sleep(iv)
                retry += 1
    
    driver.switch_to.frame(iframe)
    waiting_sys_timer(wait)
    
    print("Downloading sequences.fasta.bz2...")
    dl_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//div[contains(text(), "sequences.fasta.bz2")]')))
    dl_button.click()
    waiting_sys_timer(wait)

    print("Downloading metadata.tsv.bz2...")
    dl_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//div[contains(text(), "metadata.tsv.bz2")]')))
    dl_button.click()
    waiting_sys_timer(wait)

    back_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[contains(text(), "Back")]')))
    back_button.click()

    while not os.path.isfile(GISAID_FASTA) or not os.path.isfile(GISAID_TSV):
        time.sleep(5)

    driver.switch_to.default_content()

    if (cs and ce) or (ss and se):
        print("Browsing EpiCoV...")
        browse_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[contains(text(), "Browse")]')))
        browse_tab.click()
        waiting_sys_timer(wait)
        waiting_table_to_get_ready(wait)

        # set dates
        date_inputs = driver.find_elements_by_css_selector(
            "div.sys-form-fi-date input")
        dates = (cs, ce, ss, se)
        for dinput, date in zip(date_inputs, dates):
            if date:
                dinput.send_keys(date)

        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        waiting_sys_timer(wait, 7)

        # complete genome only
        if cg:
            button = driver.find_element_by_xpath('//input[@value="complete"]')
            button.click()
            waiting_sys_timer(wait)

        # high coverage only
        if hc:
            button = driver.find_element_by_xpath('//input[@value="highq"]')
            button.click()
            waiting_sys_timer(wait)

        # download fasta
        retry = 0
        while retry <= rt:
            try:
                print("Selecting all sequences...")
                # select all
                button_sa = driver.find_element_by_css_selector("span.yui-dt-label input")
                button_sa.click()
                waiting_sys_timer(wait)
    
                print("Downloading the sequence file...")
                button = driver.find_element_by_xpath(
                    "//td[@class='sys-datatable-info']/button")
                button.click()
                waiting_sys_timer(wait)
                if not download_finished(GISAID_FASTA, 180):
                    raise
                break
            except:
                print(f"retrying...#{retry} in {iv} sec(s)")
                if retry == rt:
                    print("Failed")
                    sys.exit(1)
                else:
                    time.sleep(iv)
                    retry += 1

        retry = 0
        while retry <= rt:        
            try:
                print("Downloading the acknowledgement table...")
                elem = driver.find_element_by_xpath(
                    "/html/body/form/div[5]/div/div[3]/div[1]/div/center[1]/a")
                script = elem.get_attribute("onclick")
                driver.execute_script(f"return {script}")
                waiting_sys_timer(wait)
                if not download_finished(GISAID_TABLE, 180):
                    raise
                break
            except:
                print(f"retrying...#{retry} in {iv} sec(s)")
                if retry == rt:
                    print("Failed")
                    sys.exit(1)
                else:
                    time.sleep(iv)
                    retry += 1

        # iterate each pages
        if meta_dl:
            page_num = 1
            print("Retrieving metadata...")
            while True:
                print(f"Starting processing page# {page_num}...")
                # retrieve tables
                tbody = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//tbody[@class='yui-dt-data']"))
                )

                waiting_table_to_get_ready(wait)

                # interate each row
                for tr in tbody.find_elements_by_tag_name("tr"):
                    td = tr.find_element_by_tag_name("td")
                    driver.execute_script("arguments[0].scrollIntoView();", td)

                    # have to click the first row twice to start the iframe
                    iframe = None
                    record_elem = None
                    retry = 1
                    while retry <= rt:
                        try:
                            td.click()
                            waiting_sys_timer(wait)
                            iframe = driver.find_element_by_xpath("//iframe")
                            if iframe:
                                break
                            else:
                                raise
                        except:
                            print(f"retrying...#{retry} in {iv} sec(s)")
                            if retry == rt:
                                print("Failed")
                                sys.exit(1)
                            else:
                                time.sleep(iv)
                                retry += 1

                    driver.switch_to.frame(iframe)

                    # detect error: "An internal server error occurred."
                    # and "error-token: DYX47"
                    error_token = driver.find_element_by_xpath("//b")
                    if error_token:
                        error_token_text = error_token.text
                        if "error-token" in error_token.text:
                            print(
                                "[FATAL ERROR] A website internal server error occurred.")
                            print(error_token_text)
                            sys.exit(1)

                    # get the element of table with metadata
                    record_elem = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[@class='packer']"))
                    )

                    # parse metadata
                    m = getMetadata(record_elem)
                    metadata.append(m)
                    print(f"{m['Accession ID']}\t{m['Virus name']}")

                    # get back
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(1)
                    driver.switch_to.default_content()

                print(f"Compeleted page# {page_num}.")
                page_num += 1

                # go to the next page
                retry = 1
                button_next_page = None
                try:
                    button_next_page = driver.find_element_by_xpath(
                        f'//a[@page="{page_num}"]')
                except:
                    break

                if button_next_page:
                    print(f"Entering page# {page_num}...")
                    while retry <= rt:
                        try:
                            button_next_page.click()
                            time.sleep(10)
                            current_page = driver.find_element_by_xpath(
                                '//span[@class="yui-pg-current-page yui-pg-page"]').text
                            if current_page != str(page_num):
                                raise
                            else:
                                break
                        except:
                            print(f"retrying...#{retry} in {iv} sec(s)")
                            if retry == rt:
                                print("Failed")
                                sys.exit(1)
                            else:
                                time.sleep(iv)
                                retry += 1

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
    """parse out metadata from the table"""
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


def waiting_sys_timer(wait, sec=1):
    """wait for system timer"""
    wait.until(EC.invisibility_of_element_located(
        (By.XPATH,  "//div[@id='sys_timer']")))
    time.sleep(sec)


def waiting_table_to_get_ready(wait, sec=1):
    """wait for the table to be loaded"""
    wait.until(EC.invisibility_of_element_located(
        (By.XPATH,  "//tbody[@class='yui-dt-message']")))
    time.sleep(sec)


def download_finished(file, timeout=60):
    sec = 0
    while sec < timeout:
        if os.path.exists(file):
            return True
        else:
            sec += 1
    return False


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
        argvs.complete,
        argvs.highcoverage,
        argvs.timeout,
        argvs.retry,
        argvs.interval,
        argvs.meta
    )
    print("Completed.")


if __name__ == "__main__":
    main()
