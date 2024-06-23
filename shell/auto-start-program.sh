#!/bin/bash
git pull tor develop &
##nohup /home/rahul/00-tor/02-data/00-tor_crawl_data/INPUT/TOR/tor > /dev/null 2>&1 &
nohup /home/rahul/00-tor/02-data/00-tor_crawl_data/INPUT/TOR/tor  &
python3 tor_crawler.py -d /home/rahul/00-tor/02-data/00-tor_crawl_data/ -t 120

