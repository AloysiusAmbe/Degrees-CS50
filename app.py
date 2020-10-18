
from selenium import webdriver
import time

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("main_page.html")

@app.route("/loader")
def loader():
    return render_template("loader.html")

# # Chrome path
# PATH = 'C:\Program Files (x86)\Chromedriver.exe'
# driver = webdriver.Chrome(PATH)

# url = 'https://www.google.com/search?q=%22'

# search_query = 'Michael Jordan'
# search_query = search_query.split()
# query = ''
# for substring in search_query:
#     query += substring
#     query += '+'
# url += query
# url2 = '%22&tbm=isch&tbs=ic:color,islt:4mp,itp:face'
# url += url2

# driver.get(url)
