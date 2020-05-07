# GISAID EpiCoV Downloader

This is a GISAID downloader to retrieve all EpiCoV sequences and the table. The script utilizes Selenium to acess the GISAID website through a Firefox webdriver.

## Requirements

Following python libraries are required for the downloader:
 - selenium
 - geckodriver
 - firefox

Below is an example of installation using conda:

```bash
$ conda install -c conda-forge selenium geckodriver firefox
```

## Example

The username (-u) and password (-p) are required arguments for the script.
If you do not specify a range of submission and/or collection dates, the nextfasta and nextmeta provided in GISAID/EpiCoV/Downloads will be downloaded.

Downloading nextfasta and nextmeta provided in GISAID/EpiCoV/Downloads:
`./gisaid_EpiCoV_downloader.py -u $UNAME -p $PASSWD`

Downloading sequences and acknowledgement table for high quality genomes collected between 2019-12-26 and 2019-12-30:
`./gisaid_EpiCoV_downloader.py -u $UNAME -p $PASSWD -cs 2019-12-26 -ce 2019-12-30 -hc -le -cg`

Downloading sequences and acknowledgement table for genomes collected between from the USA:
`./gisaid_EpiCoV_downloader.py -u $UNAME -p $PASSWD -ss 2019-12-26 -se 2019-12-30 -l USA`

## Usage
```bash
usage: gisaid_EpiCoV_downloader.py [-h] -u [STR] -p [STR] [-o [STR]]
                                   [-l [STR]] [-cs [YYYY-MM-DD]]
                                   [-ce [YYYY-MM-DD]] [-ss [YYYY-MM-DD]]
                                   [-se [YYYY-MM-DD]] [-cg] [-hc] [-le]
                                   [-t [INT]] [-r [INT]] [-i [INT]] [-m]
                                   [--headless]

Download EpiCoV sequences from GISAID

optional arguments:
  -h, --help            show this help message and exit
  -u [STR], --username [STR]
                        GISAID username
  -p [STR], --password [STR]
                        GISAID password
  -o [STR], --outdir [STR]
                        Output directory
  -l [STR], --location [STR]
                        sample location
  -cs [YYYY-MM-DD], --colstart [YYYY-MM-DD]
                        collection starts date
  -ce [YYYY-MM-DD], --colend [YYYY-MM-DD]
                        collection ends date
  -ss [YYYY-MM-DD], --substart [YYYY-MM-DD]
                        submitssion starts date
  -se [YYYY-MM-DD], --subend [YYYY-MM-DD]
                        submitssion ends date
  -cg, --complete       complete genome only
  -hc, --highcoverage   high coverage only
  -le, --lowcoverageExcl
                        low coverage excluding
  -t [INT], --timeout [INT]
                        set action timeout seconds. Default is 90 secs.
  -r [INT], --retry [INT]
                        retry how many times when the action fails. Default is
                        5 times.
  -i [INT], --interval [INT]
                        time interval between retries in second(s). Default is
                        3 seconds.
  -m, --meta            download detail metadata (experimental, very slow)
  --headless            turn on headless mode (no x-window needs)
```
