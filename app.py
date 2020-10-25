
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from flask import Flask, render_template, redirect, url_for, request, jsonify
import connections

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
connections.load_data('large')

@app.route("/")
def index():
    return render_template("main_page.html")

@app.route("/connection", methods=["POST", "GET"])
def find_connection():
    # Get request redirects user to homepage
    if request.method == 'GET':
        return redirect(url_for('index'))

    # Post request
    else:
        # Selenium setup
        PATH = 'C:\Program Files (x86)\Chromedriver.exe'
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(PATH, options=options)

        # Getting start and endpoints
        star1 = request.form.get('star1')
        star2 = request.form.get('star2')

        # Calls function to find the connection between the two actors
        path = connections.find_connection(start=star1, end=star2)
        if path == None:
            return 'No path'

        connection = dict()
        actors = list()
        counter = 1
        for p in path:
            connection[counter] = {
                'star1': connections.people[p.star_1_id]["name"],
                'star2': connections.people[p.star_2_id]["name"],
                'movie': connections.movies[p.movie_id]["title"]
                }
            actors.append(connections.people[p.star_1_id]["name"])
            actors.append(connections.movies[p.movie_id]["title"])
            actors.append(connections.people[p.star_2_id]["name"])
            counter += 1

        # Stores the url of the images
        scraped_images = dict()
        for actor in actors:
            # Formatting the search query
            search_query = actor
            search_query = search_query.split()
            query = ''
            for substring in search_query:
                query += substring
                query += '+'

            # Making the search url
            url = f'https://www.google.com/search?q={query}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947'
            driver.get(url)

            # Scraping the images
            img_url = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
            img_url.click()
            time.sleep(2)
            images = driver.find_elements_by_class_name("n3VNCb")
            for image in images:
                image_url = image.get_attribute('src')
                if ('jpg' in image_url) or ('png' in image_url) or ('jpeg' in image_url):
                    scraped_images[actor] = image_url
                    break
        driver.close()
        print(scraped_images)
        return jsonify(scraped_images)


@app.route("/gethint", methods=["POST", "GET"])
def hint():
    # Get request redirects user to homepage
    if request.method == 'GET':
        return redirect(url_for('index'))

    else:
        names = connections.names

        # Getting the values entered in the webpage
        user_input = request.form.get('input').lower()
        suggestions = get_hint(user_input=user_input, names=names)

        return jsonify(suggestions)


def get_hint(user_input: str, names: dict):
    suggestions = dict()
    input_length = len(user_input)
    counter = 1
    for key in names.keys():
        if user_input in key[:input_length]:
            suggestions[counter] = key.title()
            counter += 1

        if counter == 10:
            break

    if len(suggestions) == 0:
        suggestions[1] = 'No suggestions.'
    
    return suggestions