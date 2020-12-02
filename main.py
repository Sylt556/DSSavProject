import shlex
import os.path
import Scanner
import time

import db_management
import digital_signature

# Global variables
dir_to_scan = './'
type_ext = '.*'
db = 'default_db.db'
period_to_scan = -1


def proc_param(param_name, param_value):
    if param_name == '-d':
        global dir_to_scan
        if not os.path.isdir(param_value):
            return 11
        dir_to_scan = param_value
    elif param_name == '-t':
        global type_ext
        list_types = param_value.split(',')
        type_ext = '|'.join(['.' + ext_type for ext_type in list_types])
    elif param_name == '-p':
        global period_to_scan
        try:
            period_to_scan = int(param_value)
            if period_to_scan < 1:
                return 31
        except ValueError:
            return 32
    elif param_name == '-b':
        global db
        if os.path.isfile(param_value):
            if os.path.splitext(param_value)[1] == '.db':
                db = param_value
            else:
                return 41
        else:
            return 42
    else:
        return 51
    return 0


def main():
    while True:
        try:
            global dir_to_scan, type_ext, db, period_to_scan
            dir_to_scan = './'
            type_ext = '.*'
            db = 'default_db.db'
            period_to_scan = -1

            scan_cmd = input('\n\nrescan > ')
            split_cmd = shlex.split(scan_cmd)

            if len(split_cmd) % 2 != 0:
                print('Incorrect command!')
                continue

            result_code = 0
            for token in split_cmd[::2]:
                result_code = proc_param(token, split_cmd[split_cmd.index(token) + 1])
            if result_code != 0:
                if result_code == 11:
                    print('The path indicated is not a directory from which you can scan.')
                elif result_code == 31:
                    print('The scan period must be greater than or equal to 1 minute.')
                elif result_code == 32:
                    print('The period must be an integer.')
                elif result_code == 41:
                    print('The indicated file is not a database.')
                elif result_code == 42:
                    print('The indicated database does not exist.')
                else:
                    print('Incorrect parameter.')
                continue
            else:
                print(f'\nDirectory: {dir_to_scan}')
                print(f'Type(s) of file to scan: {type_ext}')
                print(f'Database: {db}')
                db_management.create_connection(db)
                digital_signature.define_path_json(db)
                #controllo se db è presente nel json per il controllo della firme del db
                if digital_signature.check_db_exist(db):
                    #controllo che la firma corrisponda
                    if not digital_signature.check_db(db):
                        #firma non corrisponde
                        print('the digital signature of the db does not match')
                        continue
                else:
                    #db non ancora aggiunto nel json,lo aggiungo
                    digital_signature. add_db_to_json(db)
                        
                if period_to_scan == -1:
                    print('\nScanned files:')
                    Scanner.scan_cycle(dir_to_scan, type_ext, db)
                else:
                    print(f'Scan period: {period_to_scan} min')
                    n = 1
                    while True:
                        print(f'\nScan number: {n}')
                        print('Scanned files:')
                        Scanner.scan_cycle(dir_to_scan, type_ext, db)
                        time.sleep(period_to_scan * 60)
                        n += 1
                #Aggiorno la firma        
                digital_signature.mod_dt_json(db)
                
        except KeyboardInterrupt:
            continue


main()
