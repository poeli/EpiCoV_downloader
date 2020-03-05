#!/usr/bin/env python

import argparse as ap
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

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

    p.add_argument('--headless',
            action='store_true', help='turn on headless mode')

    args_parsed = p.parse_args()
    if not args_parsed.outdir:
        args_parsed.outdir = os.getcwd()
    return args_parsed

def download_gisaid_EpiCoV(uname, upass, headless, wd=None):
    # output directory
    if not os.path.exists(wd):
        os.makedirs(wd, exist_ok=True)

    wd = os.path.abspath(wd)
    GISAID_FASTA = f'{wd}/gisaid_cov2020_sequences.fasta'
    GISAID_TABLE = f'{wd}/gisaid_cov2020_acknowledgement_table.xls'

    # start fresh
    try:
        os.remove(GISAID_FASTA)
        os.remove(GISAID_TABLE)
    except OSError:
        pass

    # start firefox driver
    print("Open browser...")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList",2)
    profile.set_preference("browser.download.manager.showWhenStarting",False)
    profile.set_preference("browser.download.dir", wd)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/excel,application/vnd.ms-excel")
    #profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_profile=profile,options=options)
    #driver = webdriver.Firefox(firefox_profile=profile)

    # open GISAID
    print("Open GISAID...")
    driver.get('https://platform.gisaid.org/epi3/frontend')
    time.sleep(7)
    print(driver.title)
    assert 'GISAID' in driver.title

    # login
    print("Login to GISAID...")
    username = driver.find_element_by_name('login')
    username.send_keys(uname)
    password = driver.find_element_by_name('password')
    password.send_keys(upass)
    driver.execute_script("return doLogin();")

    # navigate to EpiFlu
    print("Navigate to EpiCoV...")
    time.sleep(7)
    epicov_tab = driver.find_element_by_xpath("//div[@id='main_nav']//li[3]/a")
    epicov_tab.click()
    time.sleep(7)
    browse_tab = driver.find_element_by_xpath("//div[@class='sys-actionbar-bar']/div[2]")
    browse_tab.click()

    # download
    print("Downloading...")
    time.sleep(7)
    button = driver.find_element_by_xpath("/html/body/form/div[5]/div/div[2]/div/div[2]/div[2]/table/tbody/tr/td[3]/button")
    button.click()
    elem = driver.find_element_by_xpath("/html/body/form/div[5]/div/div[3]/div[1]/div/center[1]/a")
    script = elem.get_attribute("onclick")
    driver.execute_script(f"return {script}")

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

def main():
    argvs = parse_params()
    print("--- Ingest at " + time.strftime("%H:%M:%S") + " ---")
    download_gisaid_EpiCoV(argvs.username, argvs.password, argvs.headless, argvs.outdir)
    print("Completed.")

if __name__ == "__main__":
    main()
