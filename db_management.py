import sqlite3


# TODO: test
def table_exists(table_name):
    cursor.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE='table' AND name='{}' '''.format(table_name))
    if cursor.fetchone()[0] == 1:
        return True
    return False


def entry_exists(full_path_val):
    cursor.execute('''SELECT full_path
                   FROM hashes
                   WHERE full_path=?''',
                (full_path_val,))
    result = cursor.fetchone()
    return result


def insert_hash(full_path, timestamp, hash_val):
    cursor.execute('''
        INSERT INTO hashes (full_path, timestamp, hash_val)
        VALUES(?, ?, ?)
        ''', (full_path, timestamp, hash_val))
    connection.commit()


def get_hashes():
    cursor.execute('''
        SELECT * FROM hashes
    ''')
    data = []
    for row in cursor.fetchall():
        data.append(row)
    return data


def get_hash(full_path_val):
    cursor.execute('''SELECT hash_val FROM hashes WHERE full_path = ? ''', (full_path_val,))
    return cursor.fetchone()


def delete_hash(full_path_val):
    cursor.execute('DELETE FROM hashes WHERE full_path = ?', (full_path_val,))
    connection.commit()


def update_hash(full_path_val, update_dict):
    valid_keys = ['timestamp', 'hash_val']
    for key in update_dict.keys():
        if key not in valid_keys:
            raise Exception('Invalid field name!')
    for key in update_dict.keys():
        if type(update_dict[key]) == str:
            cursor.execute('''UPDATE hashes SET 'hash_val' = ? WHERE full_path = ?''',
                           (update_dict[key], full_path_val))
        else:
            cursor.execute('''UPDATE hashes SET 'timestamp' = ? WHERE full_path = ?''',
                           (update_dict[key], full_path_val))
    connection.commit()


def create_connection(database_path):
    global connection
    global cursor
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    if not table_exists('hashes'):
        cursor.execute('''
            CREATE TABLE hashes(
                full_path TEXT,
                timestamp LONG,
                hash_val TEXT
            )
        ''')
    return connection
