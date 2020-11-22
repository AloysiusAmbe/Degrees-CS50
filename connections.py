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
    print('Loading data...')
    load_data(path_name='small')
    print('Data Loaded!\n')

    while True:
        path =  find_connection()
        if path == None:
            return
        
        degrees = len(path)
        for p in path:
            print(f'{people[p.star_1_id]["name"]} and {people[p.star_2_id]["name"]} in "{movies[p.movie_id]["title"]}"')

def find_connection(start_id, end_id):
    '''
    Finds and returns the connection between two actors
    '''

    # Keeps track of all the star ids which have been visited
    visited_ids = set()
    visited_ids.add(start_id)

    # Gets all the stars who are in the same movie as the starting actor
    neighbors = get_neighbors(person_id=start_id)
    queue = Queue()

    # Checking all the neighbors of the start and adds them to the queue
    for movie_id, star_id in neighbors:
        if star_id == end_id:
            print('Found')
            # print(f'{people[start_id]["name"]} in "{movies[movie_id]["title"]}" with {people[end_id]["name"]}')
            return [Node(star_1_id=start_id, movie_id=movie_id, star_2_id=star_id)]

        if star_id not in visited_ids:
            node = Node(star_1_id=start_id, movie_id=movie_id, star_2_id=star_id)
            queue.push(node=node)
            visited_ids.add(star_id)

    neighbors_of_start = neighbors

    # Loops till queue is empty
    while(not queue.isEmpty()):
        path = []
        # Get the current node and add it to the visited set
        current_node = queue.pop()
        current_star_id = current_node.star_2_id
        visited_ids.add(current_star_id)
        path.append(current_node)

        # Gets the neighbors of the current node's second star and adds them to the queue
        neighbors = get_neighbors(person_id=current_star_id)

        for movie_id, star_id in neighbors:
            # Checks if connection has been found
            if star_id == end_id:
                print('found')

                # Gets the first connection
                for start_neighbor_movie_id, start_neighbor_star_id in neighbors_of_start:
                    if (start_neighbor_star_id in [p.star_1_id for p in path]) and (start_neighbor_star_id != start_id):
                        path.insert(0, Node(star_1_id=start_id, movie_id=start_neighbor_movie_id, star_2_id=start_neighbor_star_id))
                        break

                path.append(Node(star_1_id=current_star_id, movie_id=movie_id, star_2_id=star_id))
                return path

            # Adds a star's id to the queue only if it has not been visited
            if star_id not in visited_ids:
                node = Node(star_1_id=current_node.star_2_id, movie_id=movie_id, star_2_id=star_id)
                queue.push(node=node)
    
    else:
        print('No connection found!')
        return None


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
            # if star_id != person_id:
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