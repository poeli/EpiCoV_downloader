#!/usr/bin/env python

import argparse as ap
import os
import time
from selenium import webdriver

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

    args_parsed = p.parse_args()
    if not args_parsed.outdir:
        args_parsed.outdir = os.getcwd()
    return args_parsed

def download_gisaid_EpiCoV(uname, upass, wd=None):
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
    driver = webdriver.Firefox(firefox_profile=profile)

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
    driver.execute_script("return sys.call('c_q6ksdw_4p','Go',new Object({'page':'corona2020'}));")
    time.sleep(7)
    driver.execute_script("return sys.getC('c_q6ksdw_1db').onclick('ce_q6ksdw_187', '', 'page_corona2020.Corona2020BrowsePage', false)")

    # download
    print("Downloading...")
    time.sleep(7)
    driver.execute_script("return sys.getC('c_q6ksdw_1dp').buttonClick('DownloadAllSequences')")
    driver.execute_script("return sys.getC('c_q6ksdw_1dr').call('DownloadACKTable',{})")

    # wait for download to complete
    if not os.path.isfile(GISAID_FASTA) or not os.path.isfile(GISAID_TABLE):
        time.sleep(30)
    if not os.path.isfile(GISAID_FASTA) or not os.path.isfile(GISAID_TABLE):
        time.sleep(30)
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
    download_gisaid_EpiCoV(argvs.username, argvs.password, argvs.outdir)
    print("Completed.")

if __name__ == "__main__":
    main()
