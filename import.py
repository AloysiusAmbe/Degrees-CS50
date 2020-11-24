
import csv
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
    '''
    Imports the data to the database - movies, stars, and people
    '''
    path_name = 'small'

    # Uploads stars data to db
    # stars_reader = csv.reader(open(f'{path_name}/stars.csv', encoding='utf-8'))
    # for star_id, movie_id in stars_reader:
    #     db.execute('INSERT INTO stars (star_id, movie_id) VALUES (:star_id, :movie_id)',
    #                 {
    #                     'star_id': star_id,
    #                     'movie_id': movie_id
    #                 })
    #     print(f'Added star_id: {star_id} and movie_id: {movie_id}')
    #     db.commit()

    # # Uploads people data to the db
    # people_reader = csv.reader(open(f'{path_name}/people.csv', encoding='utf-8'))
    # for star_id, name, birth in people_reader:
    #     db.execute('INSERT INTO people (star_id, star_name, birth) VALUES (:star_id, :star_name, :birth)',
    #             {
    #                 'star_id': star_id,
    #                 'star_name': name,
    #                 'birth': birth
    #             })
    #     print(f'Added {name} to db.')
    #     db.commit()

    # # Uploads the movies data to the db
    # movies_reader = csv.reader(open(f'{path_name}/movies.csv', encoding='utf-8'))
    # for movie_id, title, year in movies_reader:
    #     db.execute('INSERT INTO movies (movie_id, movie_title, year) VALUES (:movie_id, :movie_title, :year)',
    #             {
    #                 'movie_id': movie_id,
    #                 'movie_title': title,
    #                 'year': year
    #             })
    #     print(f'Added {title} to db.')
    #     db.commit()


if __name__ == "__main__":
    main()
