import hashlib
import time

import db_management
from os import walk
from os.path import join, abspath
import pathlib
import re


# this function creates a list of files in our path with the sought after extensions
def absolute_file_paths(directory, extension):
    for dirpath, _, filenames in walk(directory):
        for f in filenames:
            # match via regex the members of our search with the extension
            if re.match(extension, pathlib.Path(f).suffix):
                yield abspath(join(dirpath, f))


# this function evaluates the MD5 hash of a given file
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def scan_cycle(my_path, my_ext, database):
    # The scan begins by creating a list of files in path of valid extension
    my_list = absolute_file_paths(my_path, my_ext)
    # we then connect to our database
    cur, con = db_management.create_connection(database)
    # main work loop
    for i in my_list:
        # we begin hashing our files one by one
        tested_md5 = md5(i)
        # if the hash exists in our db
        if db_management.entry_exists(i, cur):
            # if it is equal to the previous hash, we update the timestamp
            if db_management.get_hash(i, cur) == tested_md5:
                update_dict = {"timestamp": time.time()}
                db_management.update_hash(i, 'timestamp')
            # else we save the filename, timestamp and hash in the user report
            # TODO: write the user report system
            else:
                print("you got pwnd")
        # if the hash doesn't exist we add it to the db
        else:
            db_management.insert_hash(i, time.time(), tested_md5, cur, con)

