# About Project

This project is done by Rahul Singh and Anurag Singh under the guidance of Dr Rakshit Tandon. This project is done in Gurugram Police Cyber Security Summer Internship 2024.

# Onion Crawler

Onion Crawler is a tool designed to navigate and extract information from the Tor network. It uses
various techniques to interact with .onion websites and gather data, making it useful for researchers
and analysts interested in the dark web.

## Features

- Crawls .onion websites
- Extracts and stores information
- Provides a web interface for data visualization

## Requirements

- Python 3.8+
- Tor
- MongoDB

## Installation

1. Clone the Repository
 git clone https://github.com/rahulsingh7105/onion-crawler.git
 cd onion-crawler
2. Set Up Python Environment
 python3 -m venv venv
 source venv/bin/activate # On Windows use `venv\Scripts\activate`
3. Install Dependencies
 pip install -r requirements.txt
4. Configure Tor
 Ensure that Tor is installed and running on your system. You can download Tor from
(https://www.torproject.org/download/).
5. Start MongoDB
 Ensure that MongoDB is installed and running. You can download MongoDB from
(https://www.mongodb.com/try/download/community).

## Configuration

1. Update Configuration File
 Edit the `config.py` file to suit your needs. Ensure that the MongoDB connection string and Tor
proxy settings are correct.
 MONGO_URI = 'mongodb://localhost:27017'
 TOR_PROXY = 'socks5h://127.0.0.1:9050'

## Usage

1. Start the Crawler
 python crawler.py
2. Access the Web Interface
 Open your web browser and navigate to `http://localhost:5000` to view the collected data.

## Directory Structure

- `crawler.py`: Main script to start the crawler
- `config.py`: Configuration file
- `webapp/`: Flask web application for data visualization
- `requirements.txt`: List of dependencies

# tor-crawler

- Tor-based Dark Web Crawler

## Requirements Install

pip3 install --upgrade -r requirement.txt

### Usage

- Search Onion address using Out of band scrapper
 python3 01-oob_google.py
- Crawl Deep Web Data using Crawler
 python3 02-cli_crawler_mp.py
 python3 02-gui_crawler_mp.py
- Analyzing Crawled Data
 python3 03-analyzer_1.py

### Reference

- [Dark Web Links](https://www.thedarkweblinks.com/)
