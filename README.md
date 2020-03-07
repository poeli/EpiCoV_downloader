# GISAID EpiCoV Downloader

This is a GISAID downloader to retrieve all EpiCoV sequences and the table. The script utilies selenium to acess GISAID website through a Firefox webdriver.

## Requirements
You may need to install firefox and geckodriver to run the downloader other than selenium. Below is an example using conda:

```bash
$ conda install -c conda-forge selenium geckodriver firefox
```

## Usage
```bash
usage: gisaid_EpiCoV_download.py [-h] -u [STR] -p [STR] [-o [STR]]
                                 [-cs [YYYY-MM-DD]] [-ce [YYYY-MM-DD]]
                                 [-ss [YYYY-MM-DD]] [-se [YYYY-MM-DD]] [-m]
                                 [--headless]

Download all EpiCoV sequcnes from GISAID

optional arguments:
  -h, --help            show this help message and exit
  -u [STR], --username [STR]
                        GISAID username
  -p [STR], --password [STR]
                        GISAID password
  -o [STR], --outdir [STR]
                        Output directory
  -cs [YYYY-MM-DD], --colstart [YYYY-MM-DD]
                        collection starts date
  -ce [YYYY-MM-DD], --colend [YYYY-MM-DD]
                        collection ends date
  -ss [YYYY-MM-DD], --substart [YYYY-MM-DD]
                        submitssion starts date
  -se [YYYY-MM-DD], --subend [YYYY-MM-DD]
                        submitssion ends date
  -m, --meta            download metadata
  --headless            turn on headless mode
```
