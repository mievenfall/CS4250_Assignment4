#-------------------------------------------------------------------------
# AUTHOR: Evelyn Vu
# FILENAME: crawler.py
# SPECIFICATION: Crawl the CS website until the Permanent Faculty page is found
# FOR: CS 4250- Assignment #4
# TIME SPENT: 3
#-----------------------------------------------------------*/


from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re 
from collections import deque 


def connectDataBase():

    # Create a database connection object using pymongo
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client.corpus
        return db
    
    except Exception as e:
        print("Connect database error: " + str(e))


def updateDataBase(url, html):
    page = pages.find_one({'_id': url})
    if (page):
        pages.delete_one({'_id': url})       
        pages.insert_one({'_id': url, 'text': str(html)})

    else:
        pages.insert_one({'_id': url, 'text': str(html)})


def crawlerThread(frontier: deque):

    # stores visited urls
    visited = set()

    # while not frontier.done() do
    while len(frontier) > 0:
         
        # url <— frontier.nextURL()
        url = frontier.popleft()
        visited.add(url)

        # html <— retrieveURL(url)  
        try:
            html = urlopen(url)
        except HTTPError as e:
            print("Retrieve URL error: " + str(e))
            visited.add(url)
            continue
        except URLError as e:
            print("Retrieve URL error: " + str(e))
            visited.add(url)
            continue
            
        html = BeautifulSoup(html, 'html.parser')

        # update url in db or insert url if not in db yet
        updateDataBase(url, html)

       
        # if target_page (html) 
        if (html.find('h1', string=re.compile('(Permanent Faculty)+'))): # crawler found Permanent Faculty

            # clear_frontier()
            frontier.clear()
        
        else:

            # get all urls in html
            anchors = html.find_all('a')
            urls = []
            for anchor in anchors:
                href = anchor.get('href')
                urls.append(urljoin(url, href))

            # for each not visited url in parse (html) do
            for url in urls:
                if url not in visited:

                    # frontier.addURL(url)
                    frontier.append(url)
                    visited.add(url)


db = connectDataBase()
pages = db.pages
crawlerThread(deque(["https://www.cpp.edu/sci/computer-science/"]))