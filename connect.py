
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from util import Node, Stack, Queue

# set DATABASE_URL=postgres://postgres:test@localhost:5432/degrees

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    get_neighbors(102)
    # path = find_connection(129, 102)
    # if path == None:
    #     print(None)
    # else:
    #     print(path)


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

    for movie_id, star_id in neighbors:
        # Checks if a connection has been found
        if star_id == end_id:
            return [(movie_id, star_id)]

        # Stores each connection between actors
        node = Node(start_id, movie_id, star_id)
        queue.push(node)

        paths.append([(movie_id, star_id)])

    print(neighbors)

    while not queue.isEmpty():
        # Gets/pops the node values in the queue
        current_node = queue.pop()
        current_star_id = current_node.star_2_id
        visited.add(current_star_id)

        # Gets the neighbors of the current node's second star
        neighbors = get_neighbors(current_star_id, visited)

        for movie_id, star_id in neighbors:
            # Gets the current path
            current_path = paths[0]
            paths = paths[1:]
            current_path.append((movie_id, star_id))
            paths.append(current_path)

            # Checks if the connection has been found
            if star_id == end_id:
                # Gets the lastest path added to the list - the correct path
                return paths[-1]
            
            node = Node(current_node.star_2_id, movie_id, star_id)
            queue.push(node)

    else:
        return None # No path found


def get_neighbors(star_id: int):
    '''
    Gets all the stars who are in the same movie as the star passed into the function.
    '''
    neighbors = list()
    rows = db.execute('SELECT movies, star_id FROM people WHERE star_id = :star_id',
            {
                'star_id': star_id
            })

    for movie_ids, star_id in rows:
        for movie_id in movie_ids.split():
            stars = db.execute('SELECT stars FROM movies WHERE movie_id = :movie_id',
                {
                    'movie_id': movie_id
                })
            for star in stars:
                for s in star:
                    print(s)
    return neighbors


def get_person_id(star_name: str):
    '''
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    '''
    rows = db.execute('SELECT star_id, birth FROM people WHERE star_name = :star_name',
    {
        'star_name': star_name
    })
    rowcount = rows.rowcount
    if rowcount == 0:
        return None
    elif rowcount > 1:
        star_ids = dict()
        key = 0
        for star_id, birth in rows.fetchall():
            star_ids[key] = {
                'person_id': star_id,
                'birth': birth
            }
            key += 1
        return star_ids
    else:
        star_id = rows.fetchall()
        return star_id[0][0]


if __name__ == "__main__":
    main()
