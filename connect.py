
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from util import Node, Stack, Queue

# DATABASE_URL=postgres://postgres:test@localhost:5432/degrees

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    path = find_connection(420, 398)
    if path == None:
        print(None)
    else:
        for i in path:
            print(i.star_1_id, i.movie_id, i.star_2_id)
        print()
        pass


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
    paths = Queue()

    for movie_id, star_id in neighbors:
        # Checks if a connection has been found
        if star_id == end_id:
            path_node = [Node(start_id, movie_id, star_id)]
            return path_node

        # Stores each connection between actors
        node = Node(start_id, movie_id, star_id)
        queue.push(node)

        list_node = list()
        list_node.append(node)
        paths.push(list_node)

    print(f'getting neighbors for {start_id}')
    print(neighbors)
    print()

    while not queue.isEmpty():
        # Gets/pops the node values in the queue
        current_node = queue.pop()
        current_star_id = current_node.star_2_id
        visited.add(current_star_id)

        # Gets the neighbors of the current node's second star
        neighbors = get_neighbors(current_star_id, visited)

        print(f'getting neighbors for {current_star_id}')
        print(neighbors)
        print()

        for movie_id, star_id in neighbors:
            print(f'{movie_id}: {star_id}')
            # Gets the current path
            current_path = paths.pop()
            node = Node(current_path[-1].star_2_id, movie_id, star_id)
            current_path.append(node)
            paths.push(current_path)

            # Checks if the connection has been found
            if star_id == end_id:
                # Gets the lastest node added to the queue - the correct path
                return paths.get_path()
            
            node = Node(current_node.star_2_id, movie_id, star_id)
            queue.push(node)

    else:
        return None # No path found


def get_neighbors(star_id: int, visited: set):
    '''
    Gets all the stars who are in the same movie as the star passed into the function.
    '''
    neighbors = list()
    movies = db.execute('SELECT movies.movie_id FROM movies JOIN stars ON movies.movie_id = stars.movie_id WHERE stars.star_id = :star_id',
            {
                'star_id': star_id
            })
    for movie_id in movies:
        neighboring_stars = db.execute('SELECT people.star_id FROM people JOIN stars ON stars.star_id = people.star_id WHERE stars.movie_id = :movie_id',
        {
            'movie_id': movie_id[0]
        })

        for star in neighboring_stars:
            star_id = star[0]
            if star_id not in visited:
                neighbors.append((movie_id[0], star_id))
                visited.add(star_id)
    return neighbors


def get_person_id(star_name: str):
    '''
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    '''
    rows = db.execute('SELECT star_id, birth FROM people WHERE star_name=:star_name',
    {
        'star_name': star_name
    })
    rowcount = rows.rowcount
    if rowcount == 0:
        return None
    elif rowcount > 1:
        star_ids = dict()
        results = rows.fetchall()
        for result in results:
            star_id = result[0]
            birth = result[1]
            star_ids = {
                'name': star_name,
                'person_id': star_id,
                'birth': birth
            }
        return star_ids
    else:
        star_id = rows.fetchall()
        return star_id[0][0]


if __name__ == "__main__":
    main()
