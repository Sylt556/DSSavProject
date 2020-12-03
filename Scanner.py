import datetime
import hashlib
from os import walk, sep
from os.path import abspath, join
import time
import pandas as pd
import db_management
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
    db_management.create_connection(database)
    # we then create a user report
    report = pd.DataFrame(columns=['Full Path', 'Extension', 'Timestamp', 'Original Hash', 'New Hash'])
    # main work loop
    dict_positives = {}
    for i in my_list:
        # for clarity, create a str variable of i
        fullpath_var = str(i)
        # we begin hashing our files one by one
        new_hash = md5(i)
        print("Working on: " + fullpath_var)
        # if the hash exists in our db
        if db_management.entry_exists(fullpath_var):
            # if it is equal to the previous hash, we update the timestamp
            # Strip the data received from the database
            old_hash = str(db_management.get_hash(fullpath_var)).strip(",""("")""'"" ")
            check = old_hash == new_hash
            if check:
                update_dict = {"timestamp": time.time()}
                db_management.update_hash(fullpath_var, update_dict)
            # else we save the filename, timestamp and hash in the user report
            else:
                new_row = {'Full Path': fullpath_var,
                           'Extension': pathlib.Path(fullpath_var).suffix,
                           'Timestamp': datetime.datetime.now(),
                           'Original Hash': old_hash,
                           'New Hash': new_hash}
                dict_positives[fullpath_var] = new_hash
                report = report.append(new_row, ignore_index=True)
                update_dict = {"timestamp": time.time(), "hash_val": new_hash}
                db_management.update_hash(fullpath_var, update_dict)
                print("ATTENTION: File at "+fullpath_var+" was different from last scan cycle!")
        # if the hash doesn't exist we add it to the db
        else:
            db_management.insert_hash(str(i), time.time(), new_hash)
    if not report.empty:
        # sort the report by extension first, timestamps second
        report = report.sort_values(by=['Extension', 'Timestamp'], ignore_index=True)
        # build a path where to save the report, same location as database
        # and format datetime to be filename friendly
        datetime_formatted = str(datetime.datetime.now())
        datetime_formatted = datetime_formatted.replace(":", "_")
        report_path = pathlib.Path(str(pathlib.Path(database).parent.absolute()) + sep + 'Report_' +
                                   datetime_formatted + '.csv')
        # save the report as csv
        report.to_csv(report_path)
        print("A report for modified files has been generated at "+str(report_path))
        # we then return a control code and the report path
        return True, report_path
    else:
        return False, '-'
