
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
    path = find_connection(102, 158)
    print(path)


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

    for movie_id, star_id in neighbors:
        # Checks if a connection has been found
        if star_id == end_id:
            path = {
                'start': start_id,
                'movie': movie_id,
                'end': end_id
            }
            return path

        # Stores each connection between actors
        node = Node(start_id, movie_id, star_id)
        queue.push(node)

    while not queue.isEmpty():
        path = []


def get_neighbors(star_id: int, visited: set):
    '''
    Gets all the stars who are in the same movie as the star passed into the function.
    '''
    neighbors = set()
    movies = db.execute('SELECT movies.movie_id FROM movies JOIN stars ON movies.movie_id = stars.movie_id WHERE stars.star_id = :star_id',
            {
                'star_id': star_id
            })
    for movie_id in movies:
        neighboring_stars = db.execute('SELECT people.star_id FROM people JOIN stars ON stars.star_id = people.star_id  WHERE stars.movie_id = :movie_id',
        {
            'movie_id': movie_id[0]
        })

        for star in neighboring_stars:
            star_id = star[0]
            if star_id not in visited:
                neighbors.add((movie_id[0], star_id))
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
