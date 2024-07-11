import random
import tempfile
import time
import urllib.request
import requests as request
import json
import re
import os
import urllib3
from requests import get
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from time import time
import time

CHUNK_FILE_EXTENSION = ".ts"

def fetch_response(id):
    url = "https://www.twitch.tv/videos/" + str(id)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    #for request in driver.requests:
    #    if request.response:
    #        print(
    #            request.url,
    #            request.response.status_code,
    #            request.response.headers['Content-Type'])


    # Need to download index-dvr.m3u8 and save to virtual file
    # Need to be able to specify the resolution / fps in the URL
    # Need to get how many .ts files there are
    # Need to figure out the length of the last .ts file for ffmpeg?
    # Need to create a dir to save off the .ts files
    # Need to install FFMPEG and run the .ts files through it to encode mp4
    # Move mp4 to output dir and clean up .ts files
    #driver.quit()
    return driver.requests

def create_dir(tmp_dir):
    os.makedirs(tmp_dir)

def remove_dir(tmp_dir):
    try:
        for file in os.listdir(tmp_dir):
            os.unlink(tmp_dir + "/" + file)
        os.removedirs(tmp_dir)
    except:
        print("Unable to remove file or dir")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    id = 2192808460
    temp_dir = "/tmp/." + str(id)
    #fetch_response(2174049535)
    url = "https://www.twitch.tv/videos/" + str(id)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    try:
        remove_dir(temp_dir)
    except:
        pass

    try:
        create_dir(temp_dir)

        driver.get(url)
        # for request in driver.requests:
        #    if request.response:
        #        print(
        #            request.url,
        #            request.response.status_code,
        #            request.response.headers['Content-Type'])

        # Need to download index-dvr.m3u8 and save to virtual file
        # Need to be able to specify the resolution / fps in the URL
        # Need to get how many .ts files there are
        # Need to figure out the length of the last .ts file for ffmpeg?
        # Need to create a dir to save off the .ts files
        # Need to install FFMPEG and run the .ts files through it to encode mp4
        # Move mp4 to output dir and clean up .ts files

        REQUESTED_RES = "720p60"
        m3u8_file = None
        chunk_count = 0
        request_url = None
        milliseconds_future = int(time.time() * 1000) + 30000

        # Run while request_url is None or chunk count is less than 0 or timeout after 30 seconds
        while ((request_url == None or chunk_count == 0) and milliseconds_future - int(time.time() * 1000) > 0):
            for request in driver.requests:
                if request.response:
                    #Get the file-count for the # of segments that are in the video
                    if request.url.__contains__("index-dvr.m3u8") and request.url.__contains__(REQUESTED_RES):
                        print("index: " + request.url)
                        index_req = get(request.url)
                        # fmpeg -i "https://d2vjef5jvl6bfs.cloudfront.net/a98e7b994a39553597a8_caseoh__42739049465_1718847018/720p60/index-dvr.m3u8" -c copy TS_concat.mkv
                        with tempfile.TemporaryFile() as index_file:
                            index_file.write(index_req.content)
                            index_file.seek(0)
                            for line in index_file.readlines():
                                if line.decode("utf-8").__contains__(".ts"):
                                    chunk_count = int(line.decode("utf-8").replace(".ts", "").replace("\n", ""))

                        print("chunk count: " + str(chunk_count))

                    #Pull out the URL to DL from
                    if request.url.__contains__("0.ts"):
                        print(request.url)
                        request_url = request.url
                        #save_file(temp_dir, request.url)
                        print(
                            request.url,
                            request.response.status_code,
                            request.response.headers['Content-Type'])
            if request_url == None or chunk_count == 0:
                print("Conditions not met, sleeping for 5 secs...")
                time.sleep(5)

        print("Modifying url: " + str(request_url))

        prefix_url = re.sub('(\/\d*p\d*\/\d*\.ts)', "/" + REQUESTED_RES + "/", request_url)

        print(prefix_url)

        with open(temp_dir + "/0.ts", "wb") as file:
            if file.writable():
                for i in range(0, chunk_count):
                    filename = str(i) + CHUNK_FILE_EXTENSION
                    # TODO: Add progress bar
                    print("downloading: " + prefix_url + filename + " download %" + str(round(((i / (chunk_count - 1)) * 100), 2)), end='\r')
                    resp = get(prefix_url + filename)
                    file.write(resp.content)
            else:
                print("Not writeable")
        #TODO: Finish
        done_file = temp_dir + "/0.ts"
        os.popen("ffmpeg -y -i " + done_file + " -c:v libx264 -crf 0 -c:a copy ~/Desktop/output.mp4")

    except Exception as inst:
        raise inst

    finally:
        driver.quit()

    remove_dir(temp_dir)
