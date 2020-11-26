import csv

from util import Node, Stack, Queue

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
    for movie_id, title, year in movies_reader:
        movies[movie_id] = {
            'title': title,
            'year': year,
            'stars': set()
        }

    # Loads people
    people_reader = csv.reader(open(f'{path_name}/people.csv', encoding='utf-8'))
    for person_id, name, birth in people_reader:
        people[person_id] = {
            'name': name,
            'birth': birth,
            'movies': set()
        }
        if name.lower() not in names:
            names[name.lower()] = {person_id}
        else:
            names[name.lower()].add(person_id)

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
    load_data('small')

    path =  find_connection('200', '197')
    if path == None:
        return
    else:
        print(path)
    
    degrees = len(path)

def find_connection(start_id, end_id):
    '''
    Finds and returns the connection between two actors
    '''

    # Keeps track of all ids which have been visited
    visited = set()
    visited.add(start_id)

    # Gets all the stars who are in the same movie as the starting actor
    neighbors = get_neighbors(start_id, visited)
    queue = Queue()
    paths = list()

    # Checking all the neighbors of the start and adds them to the queue
    for movie_id, star_id in neighbors:
        if star_id == end_id:
            return [(movie_id, star_id)]

        if star_id not in visited:
            # Stores each connection between actors
            node = Node(start_id, movie_id, star_id)
            queue.push(node)

            paths.append([(movie_id, star_id)])

    while not queue.isEmpty():
        # Get the current node and add it to the visited set
        current_node = queue.pop()
        current_star_id = current_node.star_2_id
        visited.add(current_star_id)

        # Gets rhe current path
        current_path = paths[0]
        paths = paths[1:]

        neighbors = get_neighbors(current_star_id, visited)

        for movie_id, star_id in neighbors:
            path = list(current_path)
            if star_id not in visited:
                # Adds a star's id to the queue if it has not been visited
                node = Node(current_node.star_2_id, movie_id, star_id)
                queue.push(node)

                path.append((movie_id, star_id))
                paths.append(path)

            # Checks if connection has been found
            if star_id == end_id:
                return path
    
    # No path
    else:
        return None


def get_neighbors(person_id, visited: set):
    '''
    Gets all the stars who are in the same movie as the starting actor
    '''
    neighbors = list()
    movie_ids = people[person_id]['movies']
    for movie_id in movie_ids:
        stars_ids = movies[movie_id]['stars']
        for star_id in stars_ids:
            neighbors.append((movie_id, star_id))
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
        person_ids_dict = dict()
        counter = 0
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]

            person_ids_dict[counter] = {
                'name': name,
                'person_id': person_id,
                'birth': birth
            }
            counter += 1
        return person_ids_dict
    else:
        return person_ids[0]


if __name__ == '__main__':
    main()