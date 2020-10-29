
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from flask import Flask, render_template, redirect, url_for, request, jsonify
import connections

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

connections.load_data('large') # Select to load 'large' or 'small' data

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
        # Getting start and endpoints
        star1 = request.form.get('star1')
        star2 = request.form.get('star2')
        speed_option = request.form.get('speed_option')

        # Gets the start and end ids for the inputed stars
        start_id = connections.get_person_id(star1)
        end_id = connections.get_person_id(star2)

        if start_id == None:
            error = {
                'success': False,
                'message': f'"{star1}" is not in our dataset'
            }
            return jsonify(error)

        if end_id == None:
            error = {
                'success': False,
                'message': f'"{star2}" is not in our dataset'
            }
            return jsonify(error)

        # Calls function to find the connection between the two actors
        path = connections.find_connection(start_id, end_id)
        if path == None:
            error = {
                'success': False,
                'message': 'No path found'}
            return jsonify(error)

        # If the user opts to get the connecstion between 2 stars fast
        if speed_option == 'fast':
            connection = dict()
            counter = 0
            for p in path:
                connection[f'route{counter}'] = {
                    'start': connections.people[p.star_1_id]["name"],
                    'movie': connections.movies[p.movie_id]["title"],
                    'end': connections.people[p.star_2_id]["name"]
                }
                counter += 1
            return jsonify(connection)

        # User chooses to use wikipedia images - fast but image not guarenteed
        if speed_option == 'wiki':
            pass

        # Selenium setup
        PATH = 'C:\Program Files (x86)\Chromedriver.exe'
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(PATH, options=options)

        scraped_images = dict()
        key_index = 0
        for p in path:
            star1 = connections.people[p.star_1_id]["name"]
            movie_title = connections.movies[p.movie_id]["title"]
            star2 = connections.people[p.star_2_id]["name"]

            scraped_images[f'route{key_index}'] = {
                star1: get_google_images(star1, driver, 'actor'),
                movie_title: get_google_images(movie_title, driver, 'movie'),
                star2: get_google_images(star2, driver, 'actor')
            }
            key_index += 1

        driver.close()
        return jsonify(scraped_images)


def get_google_images(search_query, driver, search_filter):
    '''
    Scrapes for the image from google based on the search query entered.
    Returns the image's url.
    '''
    # Formatting the search query
    search_query = search_query.split()
    query = ''
    for substring in search_query:
        query += substring
        query += '+'

    # Making the search url
    if search_filter == 'movie':
        url = f'https://www.google.com/search?q={query}+movie+poster&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947'
    else:
        url = f'https://www.google.com/search?q={query}+actor&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947'
    driver.get(url)

    # Scraping the images
    img_url = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
    img_url.click()
    time.sleep(2)
    images = driver.find_elements_by_class_name("n3VNCb")
    for image in images:
        image_url = image.get_attribute('src')
        if ('jpg' in image_url) or ('png' in image_url) or ('jpeg' in image_url):
            return image_url
    return None


def get_wiki_images(search_query):
    '''
    User opsts to get images from wikipedia.
    Is fast but the images are not guarenteed to be displayed.
    '''
    pass


@app.route("/gethint", methods=["POST", "GET"])
def hint():
    # Get request redirects user to homepage
    if request.method == 'GET':
        return redirect(url_for('index'))

    else:
        # Getting the values entered in the webpage
        user_input = request.form.get('input').lower()
        suggestions = get_hint(user_input=user_input, names=connections.names)

        return jsonify(suggestions)


def get_hint(user_input: str, names: dict):
    '''
    Returns a dictionary of suggestions based on the user's
    input. Allows a maximum of 10 suggestions.
    '''
    suggestions = dict()
    input_length = len(user_input)
    counter = 1
    for actor_name in names.keys():
        if user_input in actor_name[:input_length]:
            suggestions[counter] = actor_name.title()
            counter += 1

        if counter == 10:
            break

    if len(suggestions) == 0:
        suggestions[1] = 'No suggestions.'
    
    return suggestions