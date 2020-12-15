
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import Flask, render_template, redirect, url_for, request, jsonify
from bs4 import BeautifulSoup
import time, connections, requests

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

connections.load_data('large') # Loads data into memory

@app.route("/")
def index():
    return render_template("main_page.html")


@app.route("/connection", methods=["POST", "GET"])
def find_connection():
    # Get request redirects user to homepage
    if request.method == 'GET':
        return redirect(url_for('index'))

    # Post requests
    else:
        # Getting front-end data
        query_by_star_name = request.form.get('by_star_name')
        speed_option = request.form.get('speed_option')

        # Gets the start and end ids for the inputed stars
        if query_by_star_name == 'false':
            start_id = request.form.get('star1_id')
            end_id = request.form.get('star2_id')

        else:
            star1 = request.form.get('star1')
            star2 = request.form.get('star2')
            start_id = connections.get_person_id(star1)
            end_id = connections.get_person_id(star2)

        # Checks if no star exists for the inputted name
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

        # Checks if there are more than one star with the same name
        # then asks the user to enter the id to be specific
        combined_dict = dict()
        if type(start_id) == dict and type(end_id) == dict:
            combined_dict['status'] = 'both'
            combined_dict['first_star'] = start_id
            combined_dict['second_star'] = end_id
            return jsonify(combined_dict)

        if type(start_id) == dict:
            combined_dict['status'] = 'has_multiple_first'
            combined_dict['first_star'] = start_id
            combined_dict['second_star'] = end_id
            return jsonify(combined_dict)

        if type(end_id) == dict:
            combined_dict['status'] = 'has_multiple_second'
            combined_dict['first_star'] = start_id
            combined_dict['second_star'] = end_id
            return jsonify(combined_dict)

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
            key = 0
            previous_star_id = None
            for movie_id, star_id in path:
                if key == 0:
                    connection['route0'] = {
                        'star1': connections.people[start_id]['name'],
                        'movie': connections.movies[movie_id]["title"],
                        'star2': connections.people[star_id]["name"]
                    }
                    previous_star_id = star_id
                else:
                    connection[f'route{key}'] = {
                        'star1': connections.people[previous_star_id]['name'],
                        'movie': connections.movies[movie_id]["title"],
                        'start': connections.people[star_id]["name"]
                    }
                    previous_star_id = star_id
                key += 1
            return jsonify(connection)

        scraped_images = dict()
        key = 0
        previous_url = None
        previous_star_name = None

        # Selenium setup
        PATH = 'C:\Program Files (x86)\Chromedriver.exe'
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(PATH, options=options)

        # Gets images from wikipedia
        if speed_option == 'wiki':
            for movie_id, star_id in path:
                star = connections.people[star_id]["name"]
                movie = connections.movies[movie_id]["title"]
                year = connections.movies[movie_id]['year']

                # Gets the star's image and movie poster
                url = get_wiki_images(star)
                movie_url = get_poster(movie, year, driver)

                if key == 0:
                    star1_url = get_wiki_images(connections.people[start_id]['name'])
                    scraped_images['route0'] = {
                        connections.people[start_id]['name']: star1_url,
                        movie: movie_url,
                        star: url
                    }

                else:
                    scraped_images[f'route{key}'] = {
                        previous_star_name: previous_url,
                        movie: movie_url,
                        star: url
                    }

                previous_url = url
                previous_star_name = star
                key += 1
            
            driver.close()
            return jsonify(scraped_images)

        # Uses selenium to get images from google
        for movie_id, star_id in path:
            # Gets the star's name and movie title
            movie = connections.movies[movie_id]["title"]
            movie_year = connections.movies[movie_id]['year']
            star = connections.people[star_id]["name"]
            birth = connections.people[star_id]['birth']

            # Gets the image urls for the stars and movie
            movie_url = get_google_images(movie, movie_year, driver, 'movie')
            star2_url = get_google_images(star, birth, driver, 'actor')

            if key == 0:
                star1_url = get_google_images(connections.people[start_id]['name'], connections.people[start_id]['birth'], driver, 'actor')
                scraped_images['route0'] = {
                    connections.people[start_id]['name']: star1_url,
                    movie: movie_url,
                    star: star2_url
                }
            
            else:
                scraped_images[f'route{key}'] = {
                    previous_star_name: previous_url,
                    movie: movie_url,
                    star: star2_url
                }
            
            previous_url = star2_url
            previous_star_name = star
            key += 1

        driver.close()
        return jsonify(scraped_images)


def get_google_images(search_query, year, driver, search_filter):
    '''
    Scrapes for the image from google based on the search query entered.
    Returns the image's url.
    '''

    # Gets movie poster
    if search_filter == 'movie':
        poster = get_poster(search_query, year, driver)
        return poster

    # Gets star's image
    else:
        # Formatting the search query
        search_query = search_query.split()
        query = ''
        for substring in search_query:
            query += substring
            query += '+'
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
            return image_url
    return None


def get_wiki_images(actor):
    '''
    User opsts to get images from wikipedia.
    Is fast but the images are not guarenteed to be displayed.
    '''

    url = 'https://en.wikipedia.org/wiki/'

    # Formats the actor's name into url
    name_substrings = actor.split()
    for substring in name_substrings:
        url += substring
        url += "_"
    response = requests.get(url)

    img = None

    # Checks to make sure the response was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Scraps the actor's image
        images = soup.find_all('img')
        for image in images:
            if image['src'][-3:].lower() == 'jpg':
                img = image['src']
                break
    return img


def get_poster(movie, year, driver):
    '''
    Gets the movie poster using the Movie Database API.
    If the response failed, we'll get the image using google images.
    '''
    
    url = f'https://api.themoviedb.org/3/search/movie?api_key=15d2ea6d0dc1d476efbca3eba2b9bbfb&query='

    # Formats the actor's name into url
    substrings = movie.split()
    for substring in substrings:
        url += substring
        url += "+"

    response = requests.get(url)

    # Makes sure response was successful
    if response.status_code == 200:
        data = response.json()
        try:
            poster = 'http://image.tmdb.org/t/p/w500/' + data['results'][0]['poster_path']
            return poster
        except IndexError:
            poster = get_google_images(movie, year, driver, 'movie')
            print('Error raised')
            print(poster)
            return poster

    else:
        # Uses google images if request is unsuccessful
        poster = get_google_images(movie, year, driver, 'movie')
        return poster


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