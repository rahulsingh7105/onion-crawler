from time import strftime, localtime, time, sleep
from datetime import datetime
import csv
import os
import subprocess
import traceback
from pyvirtualdisplay import Display

import requests
from selenium.common.exceptions import TimeoutException as SelTimeExcept
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchWindowException as SelWindowExcept
from selenium.common.exceptions import WebDriverException as SelWebDriverExcept

from tbselenium.tbdriver import TorBrowserDriver
from tor_pageCrawler_enum import RequestsErrorCode as torReqEnum
from tor_pageCrawler_enum import tbSeleniumErrorCode as torSelEnum

import codecs

OUTPUT_PATH = dict()
INPUT_PATH = dict()

ACCESS_TIMEOUT = 120
MAX_TAB_NUM = 5
MAX_QUEUE_NUM = 1

DEFAULT_XVFB_WIN_W = 1280
DEFAULT_XVFB_WIN_H = 800
XVFB_DISPLAY = Display(visible=0, size=(DEFAULT_XVFB_WIN_W, DEFAULT_XVFB_WIN_H))
digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def make_input_dir(path):
    input_path = path + 'INPUT/'
    INPUT_PATH["TBB_PATH"] = input_path + 'TBB/tor-browser_en-US'
    INPUT_PATH["ONION_PATH"] = input_path + 'ONION_LINK/machine_1/'

def make_output_dir(path):
    out_path = make_dirs(path + 'OUTPUT/')
    OUTPUT_PATH["LOG_PATH"] = make_dirs(path + 'LOG/')
    OUTPUT_PATH["SERVER_LIVE_PATH"] = make_dirs(out_path + 'SERVER_LIVE_SET/')
    OUTPUT_PATH["HTML_PATH"] = make_dirs(out_path + 'HTML_SET/')
    OUTPUT_PATH["LOG_PATH"] = make_dirs(out_path + 'LOG_SET/')
    OUTPUT_PATH["HEADER_PATH"] = make_dirs(out_path + 'HEADER_SET/')
    
    OUTPUT_PATH["LOG_PATH"] = OUTPUT_PATH["LOG_PATH"]
    OUTPUT_PATH["SERVER_LIVE_PATH"] = OUTPUT_PATH["SERVER_LIVE_PATH"] + "output_1_" + cur_date() + ".tsv"
    OUTPUT_PATH["HTML_PATH"] = OUTPUT_PATH["HTML_PATH"] + "html_source_dir_" + cur_date()
    OUTPUT_PATH["HEADER_PATH"] = OUTPUT_PATH["HEADER_PATH"] + "hidden_service_header1.tsv"

def make_path_dir(path):
    make_input_dir(path)
    make_output_dir(path)

def make_dirs(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def cur_date():
    return datetime.today().strftime("%Y-%m-%d")

def open_tor_browser():
    open_tor_browser = False
    try_count = 0
    driver = None

    while not open_tor_browser and try_count < 5:
        try_count += 1
        driver = TorBrowserDriver(INPUT_PATH["TBB_PATH"], tbb_logfile_path='./tor_browser_log.txt')
        open_tor_browser = True
        print("[DRIVER OPEN SUCCESS]", driver)
        return driver

def read_input():
    all_csv_file = os.listdir(INPUT_PATH['ONION_PATH'])
    reader_list = list()

    for csv_file in all_csv_file:
        with open(INPUT_PATH['ONION_PATH'] + csv_file, 'r') as read_file:
            reader = csv.reader(read_file, delimiter='\t')
            for row in reader:
                reader_list.append(row)
    return reader_list

def request_setup():
    session = requests.Session()
    session.proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}
    session.headers = {'User-Agent': 'Mozilla/5.0(Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0'}
    return session

def crawler_logging(mode, log):
    file_name = cur_date() + ".txt"
    with open(OUTPUT_PATH['LOG_PATH'] + "/" + file_name, mode) as crawler_logger:
        crawler_logger.write(log)

def hs_main_page_get(driver, onion_address):
    print("hs_main_page_get")
    status_code = torSelEnum.TB_SEL_SUCCESS.value
    try:
        driver.load_url(onion_address, wait_on_page=ACCESS_TIMEOUT, wait_for_page_body=True)
        print("wait_for_page_body")
    except SelWebDriverExcept as e:
        print("SelWebDriverException", e)
        status_code = torSelEnum.TB_SEL_WEBDRIVER_EXCEPT.value
    except SelTimeExcept as e:
        print("SelTimeExcept", e)
        status_code = torSelEnum.TB_SEL_TIME_EXCEPT.value
    except Exception as e:
        print("ERROR:", e)
        e_log = traceback.format_exc()
        crawler_logging("a", "[TB_SEL_UNDEFINED_EXCEPT] : " + strftime("%Y/%m/%d-%H%M:%S", localtime(time())) + "\nin" + onion_address + "\n" + e_log)
        status_code = torSelEnum.TB_SEL_UNDEFINED_EXCEPT.value
    return status_code

def write_status_code(status_code, row):
    if status_code < 400 or status_code == torReqEnum.REQ_UNDEFINED_EXCEPT.value:
        return 'a', row
    elif status_code not in [404, 410] and status_code < 500:
        return 'w', [cur_date(), "live", str(status_code)]
    elif status_code == torReqEnum.REQ_CONNECT_TIMEOUT.value:
        return 'w', [cur_date(), "dead", "REQ_connectionTimeout", "write_dead"]
    elif status_code == torReqEnum.REQ_READ_TIMEOUT.value:
        return 'w', [cur_date(), "dead", "REQ_readTimeout"]
    elif status_code == torReqEnum.REQ_CONNECTION_ERROR.value:
        return 'w', [cur_date(), "dead", "REQ_connectionError"]
    else:
        return 'w', [cur_date(), "dead", status_code]

def write_output_file(row):
    with open(OUTPUT_PATH["SERVER_LIVE_PATH"], 'a') as output_file:
        writer = csv.writer(output_file, delimiter='\t')
        writer.writerow(row)

def write_header_list(header):
    file_name = 'hidden_service_header.csv'
    with open(OUTPUT_PATH['HEADER_PATH'] + file_name, 'a') as hs_header_list_file:
        hs_header_list_file.write(header)

def hs_request_status_code(session, onion_address):
    print("hs_request_status_code")
    try:
        response = session.get(onion_address, timeout=ACCESS_TIMEOUT)
        hs_status_code = response.status_code
        hs_header = str(response.headers)
        write_header_list(onion_address + '\t' + hs_header + '\n')
    except requests.ConnectTimeout:
        return torReqEnum.REQ_CONNECT_TIMEOUT.value
    except requests.ReadTimeout:
        return torReqEnum.REQ_READ_TIMEOUT.value
    except requests.ConnectionError:
        return torReqEnum.REQ_CONNECTION_ERROR.value
    except Exception as e:
        print(e)
        return torReqEnum.REQ_UNDEFINED_EXCEPT.value
    return hs_status_code

def tor_crawling(address_queue, driver, idx, leng):
    print("ADDRESS LENGTH: ", len(address_queue))
    if len(address_queue) == MAX_QUEUE_NUM or idx == leng - 1:
        print("QUEUE IS MAX")
        tab_list = open_tab(address_queue, driver)
        crawl_tab(tab_list, driver)
        reset_other_tabs(driver)

def reset_other_tabs(driver):
    other_tab_idx = driver.window_handles
    while len(other_tab_idx) > 1:
        for tab_idx_num in range(1, len(other_tab_idx)):
            driver.switch_to_window(other_tab_idx[tab_idx_num])
            driver.close()
        other_tab_idx = driver.window_handles
    driver.switch_to_window(other_tab_idx[0])

def open_tab(address_queue, driver):
    for address in address_queue:
        open_tab_script = "window.open(\"" + address[0] + "\",\"_blank\");"
        driver.execute_script(open_tab_script)
        sleep(5)

    tab_idx_list = driver.window_handles
    return zip(tab_idx_list, address_queue)

def crawl_tab(tab_list, driver):
    for tab_idx_num in range(len(tab_list)):
        tab_idx = tab_list[tab_idx_num]
        switch_tab(driver, tab_idx)
        page_title = driver.title
        page_write(driver, page_title, tab_idx_num)

def page_write(driver, page_title, tab_idx_num):
    address_queue = list()
    if page_title != 'Problem loading page':
        address_queue.append(cur_date())
        address_queue.append("live")
        address_queue.append(str(torSelEnum.TB_SEL_SUCCESS.value))
        write_output_file(address_queue)
        write_html_file(driver, tab_idx_num[1])
    else:
        address_queue.append(cur_date())
        address_queue.append("dead")
        address_queue.append(str(torSelEnum.TB_SEL_UNDEFINED_EXCEPT.value))
        write_output_file(address_queue)

def write_html_file(driver, file_name):
    file_name = file_name + ".html"
    with codecs.open(OUTPUT_PATH["HTML_PATH"] + "/" + file_name, "w", "utf-8") as html_writer:
        html_writer.write(driver.page_source)
    print("write complete", OUTPUT_PATH["HTML_PATH"] + "/" + file_name)

def switch_tab(driver, tab_idx):
    try:
        driver.switch_to_window(tab_idx)
    except SelWindowExcept:
        crawler_logging("a", "[TB_SEL_NO_SUCH_WINDOW_EXCEPT] : Current tab idx " + str(tab_idx) + "\n Current Queue \n")

def exit_crawler(driver, output_file):
    if driver:
        driver.close()
    if XVFB_DISPLAY.is_alive():
        XVFB_DISPLAY.stop()
    if output_file:
        output_file.close()

def open_write_file():
    output_file = open(OUTPUT_PATH["SERVER_LIVE_PATH"], 'w')
    writer = csv.writer(output_file, delimiter='\t')
    return writer

def open_header_path():
    return open(OUTPUT_PATH["HEADER_PATH"], 'a')

def main(path, timeout):
    make_path_dir(path)
    driver = open_tor_browser()
    session = request_setup()
    print("SESSION:", session)

    writer = open_write_file()
    header_path = open_header_path()

    reader_list = read_input()

    for address_idx in range(len(reader_list)):
        address_queue = list()
        row = reader_list[address_idx]
        onion_address = row[0]
        print("onion_address:", onion_address)
        hs_main_page_get(driver, onion_address)

        hs_status_code = hs_request_status_code(session, onion_address)
        print("hs_status_code:", hs_status_code)
        w_mode, status = write_status_code(hs_status_code, row)
        print("mode:", w_mode, "status:", status)

        if w_mode == 'a':
            address_queue.append(status)
        elif w_mode == 'w':
            write_output_file(status)

        tor_crawling(address_queue, driver, address_idx, len(reader_list))
    exit_crawler(driver, writer)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rootdirectory", "-d", help="root directory")
    parser.add_argument("--timeout", "-t", help="timeout")
    args = parser.parse_args()
    main(args.rootdirectory, args.timeout)
