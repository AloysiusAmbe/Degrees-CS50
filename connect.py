
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# DATABASE_URL=postgres://postgres:test@localhost:5432/degrees

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # visited = set()
    # visited.add(102)
    # neighbors = get_neighbors(102, visited)

    get_person_id('Tom Hanks')


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
    rows = db.execute('SELECT star_name, star_id, birth FROM people WHERE star_name=:star_name',
    {
        'star_name': star_name
    })
    rowcount = rows.rowcount
    if rowcount == 0:
        return None
    elif rowcount > 1:
        pass
    else:
        star_id = rows.fetchall()
        return star_id[0][1]


if __name__ == "__main__":
    main()
