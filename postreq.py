from bs4 import BeautifulSoup as bs
import requests
import mysql.connector as connector
import re

PREFIX = "CSCI"

mydb = connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="postreq"
)
print("Connected to database")

mycursor = mydb.cursor()

URL = f"https://bulletin.uga.edu/CoursesHome?Prefix={PREFIX}"

soup = bs(requests.get(URL).text, 'html.parser');

def populateCourse():
    query = 'INSERT INTO Course (CourseID, Title) VALUES (%s, %s)'
    tables = soup.find_all(class_="courseresultstable")
    for table in tables:
        id = ""
        title = ""
        bs = table.find_all('b')
        for i in range(len(bs)):
            if bs[i].string == 'Course ID:':
                id = bs[i + 1].string
            if bs[i].string == 'Course Title:':
                title = bs[i + 1].string
        if title and id:
            mycursor.execute(query, (id, title))
    mydb.commit()

def populatePrerequisite():
    query = "INSERT INTO Prerequisite (CourseID, Prerequisite) VALUES (%s, %s)"          
    tables = soup.find_all(class_="courseresultstable")
    for table in tables:
        tds = table.find_all('td')
        course = ""
        prereq = []
        for i in range(len(tds)):
            b = tds[i].find('b')
            if b and b.string == "Course ID:":
                course = tds[i + 1].find('b').string
            if b and b.string == "Prerequisite:":
                fix = tds[i+1].string.replace(' and ', ' or ')
                prereq = fix.split(" or ")

        if course and prereq and prereq != []:
            for p in prereq:
                p = p.replace("At least one of the following:  ", "")
                p = p.strip(')')
                p = p.strip('(')
                p = p.strip('[')
                p = p.strip(']')
                mycursor.execute(query, (course, p))
    mydb.commit()

#def getPostrequisites(courseid: str) -> list[str]:
#def getPrerequisites(courseid: str) -> list[str]:

#populatePrerequisite()
#populateCourse()
mydb.close()

