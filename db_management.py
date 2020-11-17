import sqlite3


# TODO: everything
def table_exists(table_name, cur):
    cur.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE='table' AND name='{}' '''.format(table_name))
    if cur.fetchone()[0] == 1:
        return True
    return False


def entry_exists(full_path, cur):
    cur.execute("""SELECT full_path
                   FROM hashes
                   WHERE full_path=?""",
                (full_path))
    result = cur.fetchone()
    return result


def insert_hash(full_path, timestamp, hash_val, cur, conne):
    cur.execute('''
        INSERT INTO hashes (full_path, timestamp, hash_val)
        VALUES(?, ?, ?)
        ''', (full_path, timestamp, hash_val))
    conne.commit()


def get_hashes(cur):
    cur.execute('''
        SELECT * FROM hashes
    ''')
    data = []
    for row in cur.fetchall():
        data.append(row)
    return data


def get_hash(full_path, cur):
    cur.execute('''
        SELECT *
        FROM hashes
        WHERE full_path = {}
    '''.format(full_path))
    data = []
    for row in cur.fetchall():
        data.append(row)
    return data


def delete_hash(full_path, cur, conne):
    cur.execute('''DELETE FROM hashes WHERE full_path = {}'''.format(full_path))
    conne.commit()


def update_hash(full_path, update_dict, cur, conne):
    valid_keys = ['timestamp', 'hash_value']
    for key in update_dict.keys():
        if key not in valid_keys:
            raise Exception('Invalid field name!')
    for key in update_dict.keys():
        stmt = '''UPDATE hashes SET {} = '{}' where full_path = {}'''.format(key, update_dict[key], full_path)
        cur.execute(stmt)
    conne.commit()


def create_connection(database_path):
    conn = sqlite3.connect(database_path)
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
    return c, conn
