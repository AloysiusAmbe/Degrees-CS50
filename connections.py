import csv

from Node import Node, Stack, Queue

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, and a set of movie_ids
people = {}

# Maps movie_ids to a dictionary of title, year, and a set of person_ids
movies = {}

def load_data(path_name: str):
    '''
    Loads the data fron the CSV files into memory.
    '''
    # Loads movies
    movies_reader = csv.reader(open(f'{path_name}/movies.csv', encoding='utf-8'))
    for id, title, year in movies_reader:
        movies[id] = {
            'title': str(title),
            'year': year,
            'stars': set()
        }

    # Loads people
    people_reader = csv.reader(open(f'{path_name}/people.csv', encoding='utf-8'))
    for id, name, birth in people_reader:
        people[id] = {
            'name': str(name),
            'birth': birth,
            'movies': set()
        }
        if name.lower() not in names:
            names[name.lower()] = {id}
        else:
            names[name.lower()].add(id)

    # Loads stars
    stars_reader = csv.reader(open(f'{path_name}/stars.csv', encoding='utf-8'))
    for person_id, movie_id in stars_reader:
        try:
            people[person_id]['movies'].add(movie_id)
            movies[movie_id]['stars'].add(person_id)
        except:
            pass


def main():
    '''
    Main function call
    '''
    print('Loading data...')
    load_data(path_name='large')
    print('Data Loaded!\n')

    find_connection()


def find_connection():
    '''
    Finds and returns the connection between two actors
    '''

    # Prompts for the first star
    start = str(input('Enter start name: ')).title()
    start_id = get_person_id(name=start)
    if start_id == None:
        print(f'{start} is not in our dataset.')
        return

    # Prompts for the second star
    end = str(input('Enter start name: ')).title()
    end_id = get_person_id(name=end)
    if end_id == None:
        print(f'{end} is not in our dataset.')
        return

    # Keeps track of all the star ids which have been visited
    visited_ids = set()
    visited_ids.add(start_id)

    # Gets all the stars who are in the same movie as the starting actor
    neighbors = get_neighbors(person_id=start_id)
    queue = Queue()

    # Checking all the neighbors of the start and adds them to the queue
    for movie_id, star_id in neighbors:
        if star_id == end_id:
            print(f'{people[start_id]["name"]} in "{movies[movie_id]["title"]}" with {people[end_id]["name"]}')
            return

        print(f'{people[start_id]["name"]} "{movies[movie_id]["title"]}" {people[star_id]["name"]}')
        if star_id not in visited_ids:
            print('Added')
            node = Node(star_1_id=start_id, movie_id=movie_id, star_2_id=star_id)
            queue.push(node=node)
            visited_ids.add(star_id)
        print()

    # Loops till queue is empty
    while(not queue.isEmpty()):
        # Get the current node and add it to the visited set
        current_node = queue.pop()
        current_star_id = current_node.star_2_id
        visited_ids.add(current_star_id)
        print(f"{people[current_node.star_1_id]['name']}   '{movies[current_node.movie_id]['title']}'   {people[current_star_id]['name']}")

        # Gets the neighbors of the current node's second star and adds them to the queue
        neighbors = get_neighbors(person_id=current_star_id)

        for movie_id, star_id in neighbors:
            # Checks if connection has been found
            if star_id == end_id:
                print('found')
                return

            # Adds a star's id to the queue only if it has not been visited
            if star_id not in visited_ids:
                node = Node(star_1_id=current_node.star_2_id, movie_id=movie_id, star_2_id=star_id)
                queue.push(node=node)
    
    else:
        print('No connection found!')


def get_neighbors(person_id):
    '''
    Gets all the stars who are in the same movie as the starting actor
    '''
    movie_ids = people[person_id]['movies']
    neighbors = set()
    for movie_id in movie_ids:
        movie = movies[movie_id]['title']
        stars_in_movie = movies[movie_id]['stars']
        for star_id in stars_in_movie:
            if star_id != person_id:
                neighbors.add((movie_id, star_id))
    return neighbors


def get_person_id(name: str):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


if __name__ == '__main__':
    main()