# GISAID EpiCoV Downloader

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4323561.svg)](https://doi.org/10.5281/zenodo.4323561)
[![gisaid](https://github.com/poeli/EpiCoV_downloader/workflows/gisaid/badge.svg)](https://github.com/poeli/EpiCoV_downloader/actions?query=workflow%3Agisaid) 

This is a GISAID downloader to retrieve all EpiCoV sequences and the table. The script utilizes Selenium to acess the GISAID website through a Firefox webdriver.

## Installation

We provide a package file (environment.yml) to create a new environment (gisaid) using conda:

```bash
$ git clone https://github.com/poeli/EpiCoV_downloader.git
$ cd EpiCoV_downloader/
$ conda env create -f environment.yml
$ conda activate gisaid
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
                                   [-l [STR]] [-ht [STR]] [-cs [YYYY-MM-DD]]
                                   [-ce [YYYY-MM-DD]] [-ss [YYYY-MM-DD]]
                                   [-se [YYYY-MM-DD]] [-cg] [-hc] [-le]
                                   [-t [INT]] [-r [INT]] [-i [INT]] [-m]
                                   [--normal]

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
  -ht [STR], --host [STR]
                        Specify a host of the sample. Default is human.
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
  --normal              run firefox in normal mode.
```
