#-------------------------------------------------------------------------
# AUTHOR: Evelyn Vu
# FILENAME: parser.py
# SPECIFICATION: Parse faculty members' name, title, office, phone, email, and website, and persist this data in MongoDB
# FOR: CS 4250- Assignment #4
# TIME SPENT: 2.5
#-----------------------------------------------------------*/\

from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

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


def updateDatabase(doc):
    professor = professors.find_one({"_id": doc["name"]})
    if (professor):
        professors.delete_one({"_id": doc["name"]})
        professors.insert_one(doc)
    else:
        professors.insert_one(doc)



def parser():

    # use the target page URL to find the Permanent Faculty page in the database
    url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
    page = pages.find_one({"_id": url})
    html = page.get('text')

    # create beautiful soup object
    bs = BeautifulSoup(html, 'html.parser')
    
    # professors info is under text-images section -> clearfix div -> h2 and p
    # but not all clearfix div have info
    # get section -> h2 containing name -> div for container
    section = bs.find('section', {'class':{'text-images'}})
    headers = section.find_all('h2')
    containers = []
    for i in headers:
        containers.append(i.parent)

# for each professor
    for prof in containers:
        # get name
        name = prof.h2.get_text().strip()

        # get title
        title = prof.find("strong", string=re.compile('(Title){1,1}')).next_sibling.get_text()
        title = title.strip(": ").strip()

        # get office
        office = prof.find("strong", string=re.compile('(Office){1,1}')).next_sibling.get_text()
        office = office.strip(":").strip()

        # get email
        email = prof.find('a', {'href': re.compile("^(mailto:)")}).get('href')
        email = email.split(":")[1]

        #get website
        website = prof.find('a', {'href': re.compile(r"^https?:\/\/www\.cpp\.edu\/faculty")}).get('href')


        # create professor document
        doc = {
            "_id": name,
            "name": name,
            "title": title,
            "office": office,
            "email": email,
            "website": website
        }

        # update doc in db or insert url if not in db yet
        updateDatabase(doc)


db = connectDataBase()
professors = db.professors
pages = db.pages
parser()