import time
import Scanner
import digital_signature

_sentinel = object()


def ret_sentinel():
    return _sentinel


def scan_task_launcher(out_q, stop_q, sleep_length, path, ext, db):
    while True:
        return_of_scanner = Scanner.scan_cycle(path, ext, db)
        out_q.put(return_of_scanner)
        if stop_q.get() is _sentinel:
            break
        time.sleep(sleep_length)
    print("SCANNER quitting")
    # this is where we sign the database, after the very last change has been made
    digital_signature.mod_dt_json(db)


def scan_reporter(out_q, stop_q):
    while True:
        data = out_q.get()
        if data is _sentinel:
            stop_q.put(_sentinel)
            break
        else:
            stop_q.put(True)
    print("REPORTER quitting")
