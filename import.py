
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
    Imports the data to the database - movies, stars, and people
    '''
    path_name = 'small'
    load_data(path_name)
    print('Loaded')

    # Uploads stars data to db
    stars_reader = csv.reader(open(f'{path_name}/stars.csv', encoding='utf-8'))
    for star_id, movie_id in stars_reader:
        db.execute('INSERT INTO stars (star_id, movie_id) VALUES (:star_id, :movie_id)',
                    {
                        'star_id': star_id,
                        'movie_id': movie_id
                    })
    db.commit()
    print('Loaded stars to db')

    # # Uploads people data to the db
    people_reader = csv.reader(open(f'{path_name}/people.csv', encoding='utf-8'))
    for star_id, name, birth in people_reader:
        movies_person_in = ''
        for movie in people[star_id]['movies']:
            movies_person_in += movie + ' '
        db.execute('INSERT INTO people (star_id, star_name, movies, birth) VALUES (:star_id, :star_name, :movies, :birth)',
                {
                    'star_id': star_id,
                    'star_name': name,
                    'movies': movies_person_in,
                    'birth': birth
                })
    db.commit()
    print('Loaded people to db')

    # # Uploads the movies data to the db
    movies_reader = csv.reader(open(f'{path_name}/movies.csv', encoding='utf-8'))
    for movie_id, title, year in movies_reader:
        stars_in_movie = ''
        for person_id in movies[movie_id]['stars']:
            stars_in_movie += person_id + ' '
        db.execute('INSERT INTO movies (movie_id, movie_title, stars, year) VALUES (:movie_id, :movie_title, :stars, :year)',
                {
                    'movie_id': movie_id,
                    'movie_title': title,
                    'stars': stars_in_movie,
                    'year': year
                })
    db.commit()
    print('Loaded movies to db')


if __name__ == "__main__":
    main()
