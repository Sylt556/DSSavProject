import shlex
import os.path
import Scanner
import time

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
                print('Comando non corretto!')
                continue

            result_code = 0
            for token in split_cmd[::2]:
                result_code = proc_param(token, split_cmd[split_cmd.index(token) + 1])
            if result_code != 0:
                if result_code == 11:
                    print('Il path indicato non è una directory dalla quale è possibile eseguire la scansione.')
                elif result_code == 31:
                    print('Il periodo di scansione deve essere maggiore o uguale a 1.')
                elif result_code == 32:
                    print('Il periodo deve essere un intero.')
                elif result_code == 41:
                    print('Il database indicato non è un database.')
                elif result_code == 42:
                    print('Il file indicato non esiste.')
                else:
                    print('Parametro non corretto.')
                continue
            else:
                print(f'\nDirectory: {dir_to_scan}')
                print(f'Tipo(i) di file da scansionare: {type_ext}')
                print(f'Periodo di scansione: {period_to_scan} min')
                print(f'Database: {db}')

                if period_to_scan == -1:
                    print('\nFile scansionati:')
                    Scanner.scan_cycle(dir_to_scan, type_ext, db)
                else:
                    n = 1
                    while True:
                        print(f'\nScansione: {n}')
                        print('File scansionati:')
                        Scanner.scan_cycle(dir_to_scan, type_ext, db)
                        time.sleep(period_to_scan * 60)
                        n += 1
        except KeyboardInterrupt:
            continue


main()
