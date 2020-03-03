# GISAID EpiCoV Downloader

This is a GISAID downloader to retrieve all EpiCoV sequences and the table. The script utilies selenium to acess GISAID website through a Firefox webdriver.

You may need install firefox and geckodriver to run the downloader.

```conda install -c conda-forge geckodriver firefox```

```
usage: gisaid_EpiCoV_download.py [-h] -u [STR] -p [STR] [-o [STR]]

Download all EpiCoV sequcnes from GISAID

optional arguments:
  -h, --help            show this help message and exit
  -u [STR], --username [STR]
                        GISAID username
  -p [STR], --password [STR]
                        GISAID password
  -o [STR], --outdir [STR]
                        Output directory
  --headless            Turn on headless mode
```
