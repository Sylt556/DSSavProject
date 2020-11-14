import sqlite3


def table_exists(table_name):
    c.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE='table' AND name='{}' '''.format(table_name))
    if c.fetchone()[0] == 1:
        return True
    return False


def insert_movie(movie_id, name, release_year, genre, rating):
    c.execute('''
        INSERT INTO movies (movie_id, name, release_year, genre, rating)
        VALUES(?, ?, ?, ?, ?)
    ''', (movie_id, name, release_year, genre, rating))
    conn.commit()


def get_movies():
    c.execute('''
        SELECT * FROM movies
    ''')
    data = []
    for row in c.fetchall():
        data.append(row)
    return data


def get_movie(movie_id):
    c.execute('''
        SELECT *
        FROM movies
        WHERE movie_id = {}
    '''.format(movie_id))
    data = []
    for row in c.fetchall():
        data.append(row)
    return data


def update_movie(movie_id, update_dict):
    valid_keys = ['name', 'release_year', 'genre', 'rating']
    for key in update_dict.keys():
        if key not in valid_keys:
            raise Exception('Invalid field name!')
    for key in update_dict.keys():
        stmt = '''UPDATE movies SET {} = '{}' where movie_id = {}'''.format(key, update_dict[key], movie_id)
        c.execute(stmt)
    conn.commit()


def delete_movie(movie_id):
    c.execute('''DELETE FROM movies WHERE movie_id = {}'''.format(movie_id))
    conn.commit()


conn = sqlite3.connect('hashValues.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS movies(
        movie_id INTEGER,
        name TEXT,
        release_year INTEGER,
        genre TEXT,
        rating REAL
    )
''')
