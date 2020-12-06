import time
import tkinter as tk  # Module for GUI
from queue import Queue
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import re
import Scanner
import digital_signature
from threading import Thread


period_to_scan = -1
type_ext = '*'
db = './default_db.db'
dir_to_scan = './'
q = Queue()
control_q = Queue()
_sentinel = object()


# ~~~~~~ MODULES FOR MULTITHREADING ~~~~~~ #
def ret_sentinel():
    return _sentinel


def scan_task_launcher(out_q, stop_q, sleep_length, path, ext, db):
    n = 1
    while True:
        txt_prv_report.insert(tk.END, "Scan #" + str(n) + ": ")
        n += 1
        return_of_scanner = Scanner.scan_cycle(path, ext, db)
        if len(return_of_scanner) == 2:
            if return_of_scanner[0]:
                txt_prv_report.insert(tk.END, str(return_of_scanner[1]) + "\n")
                open_report(return_of_scanner[1])
            else:
                no_report()
        txt_prv_report.insert(tk.END, "\n")
        out_q.put(return_of_scanner)
        time.sleep(sleep_length)
        if stop_q.get() is _sentinel:
            break
    # this is where we sign the database, after the very last change has been made
    digital_signature.mod_dt_json(db)
    lbl_console["fg"] = "green"
    lbl_console["text"] = "Recurring Scan Stopped."


def scan_reporter(out_q, stop_q):
    while True:
        data = out_q.get()
        if data is _sentinel:
            stop_q.put(_sentinel)
            break
        else:
            stop_q.put(True)


# ~~~~~~ MODULES FOR WRITING REPORTS ON SCREEN ~~~~~~ #
def clear_report():
    txt_prv_report.delete(1.0, tk.END)


def no_report():
    txt_prv_report.insert(tk.END, "No report was generated.")


def open_report(path_report):
    with open(path_report, "r") as input_file:
        text = input_file.read()
        txt_prv_report.insert(tk.END, text)


# ~~~~~~ MODULES FOR SCANNING ~~~~~~ #
def scan_integration(path, extension, database):
    control_value, report_path = Scanner.scan_cycle(path, extension, database)
    if control_value:
        txt_prv_report.insert(tk.END, "Report generated at: " + str(report_path) + "\n")
        open_report(report_path)
    else:
        no_report()
    return


# this function starts our scanner and reporter threads.
def periodic_scan_integration(period, path, extension, database):
    scan_thread = Thread(target=scan_task_launcher,
                         args=(q, control_q, period, path, extension, database))
    reporter_thread = Thread(target=scan_reporter,
                             args=(q, control_q))
    scan_thread.start()
    reporter_thread.start()
    btn_stop["state"] = "normal"


def stop_periodic_scan():
    btn_stop["state"] = "disabled"
    q.put(_sentinel)
    btn_scan["state"] = "normal"
    lbl_console["fg"] = "red"
    lbl_console["text"] = "Console > Interrupting a periodic scan, please wait..."


# ~~~~~~ MODULES FOR USER INPUT ~~~~~~ #
def select_dir():
    dirpath = askdirectory()
    if not dirpath:
        return
    ent_directory["state"] = "normal"
    ent_directory.delete(0, tk.END)
    ent_directory.insert(tk.END, dirpath)
    ent_directory["state"] = "disabled"


def select_db():
    filepath = askopenfilename(
        filetypes=[("Database Files", "*.db")]
    )
    if not filepath:
        return
    ent_database["state"] = "normal"
    ent_database.delete(0, tk.END)
    ent_database.insert(tk.END, filepath)
    ent_database["state"] = "disabled"


def pick_scan_mode(scan_period, scan_path, extension, database):
    if scan_period == -1:
        scan_integration(scan_path, extension, database)
        lbl_console["fg"] = "green"
        lbl_console["text"] = lbl_console["text"] + " > Scan Completed!"
        btn_scan["state"] = "normal"
    else:
        print("Running periodic scan")
        periodic_scan_integration(scan_period, scan_path, extension, database)
        lbl_console["fg"] = "green"
        lbl_console["text"] = "Console > Started a periodic scan with period " + str(period_to_scan)


# ~~~~~~ MODULE FOR A SCAN CYCLE ~~~~~~ #
def check_scan():
    global type_ext, period_to_scan, fmt, stop, no_signature
    no_signature = True
    clear_report()
    btn_scan["state"] = "disabled"
    btn_scan.update_idletasks()
    type_ext = ent_ext.get()
    if type_ext == "":
        type_ext = '.*'
    else:
        list_types = re.split(', |,', type_ext)
        type_ext = '|'.join(['.' + ext_type for ext_type in list_types])
    # Check - Period
    try:
        period_to_scan = int(ent_period.get())
    except ValueError:
        ent_period["fg"] = "red"
        lbl_console["fg"] = "red"
        lbl_console["text"] = "Console > The period must be an integer."
        btn_scan["state"] = "normal"
        return
    if period_to_scan != -1 and (period_to_scan < 1 or period_to_scan > 1400):
        ent_period["fg"] = "red"
        lbl_console["fg"] = "red"
        lbl_console["text"] = "Console > The scan period must be greater than or equal to 1 seconds.\
 To issue a single scan use -1 as argument."
        btn_scan["state"] = "normal"
    else:
        ent_period["fg"] = "black"
        lbl_console["fg"] = "black"
        db = ent_database.get()
        digital_signature.define_path_json(db)
        if digital_signature.check_db_exist(db):
            # check the signature
            if not digital_signature.check_db(db):
                # stop the scan if the signature doesn't match
                lbl_console["fg"] = "red"
                lbl_console["text"] = f"Console > The digital signature of the db does not match"
                btn_scan["state"] = "normal"
                return
        else:
            # database file not present in the signature list, adding it
            digital_signature.add_db_to_json(db)
        lbl_console["text"] = f"Console > ReScan -d {ent_directory.get()}\
-b {ent_database.get()} -t {type_ext}"
        # this function will determine the type of scan (single or continuous) based on the period
        # it will then launch the appropriate function
        pick_scan_mode(period_to_scan, ent_directory.get(), type_ext, ent_database.get())
        # In the case of a single scan we can sign the database instantly
        # while in case of a continuous scan this step runs during the thread_manager.scan_task_launcher cleanup
        if period_to_scan == -1:
            digital_signature.mod_dt_json(db)


main_window = tk.Tk()  # Create main window
main_window.title("ReScan")  # Set main window title


# Size
main_window.geometry("900x480")
main_window.resizable(0, 0)


# Configure rows and columns
main_window.columnconfigure(0, minsize=500, weight=1)


# Description
# main_window.rowconfigure(0, minsize=5, weight=1)
# Description label
frm_descr = tk.Frame(master=main_window)
lbl_descr = tk.Label(master=frm_descr,
                     text="ReScan is an antivirus software designed during the "
                          "'System and data security' course by:\n"
                          "Emanuele Urselli, Giuseppe Crea and Gabriele Baschieri")
frm_descr.grid(row=0, column=0, sticky="ns")
lbl_descr.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)


# Input
# main_window.rowconfigure(1, minsize=10, weight=1)
frm_input = tk.Frame(master=main_window)
frm_input.rowconfigure([0, 1, 2, 3], weight=1)
# First input - Directory
lbl_directory = tk.Label(master=frm_input, text="Directory:", font="Verdana 15 bold")
ent_directory = tk.Entry(master=frm_input, width=50)
ent_directory.insert(tk.END, dir_to_scan)
ent_directory["state"] = "disabled"
btn_directory = tk.Button(master=frm_input, text="Browse", width=10, command=select_dir)
lbl_directory.grid(row=0, column=0, sticky="ne", padx=5, pady=5)
ent_directory.grid(row=0, column=1, sticky="nw", padx=5, pady=5)
btn_directory.grid(row=0, column=2, sticky="nw", padx=5, pady=5)
# Second input - Database
lbl_database = tk.Label(master=frm_input, text="Database:", font="Verdana 15 bold")
ent_database = tk.Entry(master=frm_input, width=50)
ent_database.insert(tk.END, db)
ent_database["state"] = "disabled"
btn_database = tk.Button(master=frm_input, text="Browse", width=10, command=select_db)
lbl_database.grid(row=1, column=0, stick="ne", padx=5, pady=5)
ent_database.grid(row=1, column=1, sticky="nw", padx=5, pady=5)
btn_database.grid(row=1, column=2, sticky="nw", padx=5, pady=5)
# Third and Fourth input - Extensions and Period
frm_input_2 = tk.Frame(master=frm_input)
lbl_ext = tk.Label(master=frm_input_2, text="Extension(s):", font="Verdana 15 bold")
ent_ext = tk.Entry(master=frm_input_2, width=20)
ent_ext.insert(tk.END, type_ext)
lbl_period = tk.Label(master=frm_input_2, text="Period:", font="Verdana 15 bold")
ent_period = tk.Entry(master=frm_input_2, width=20)
ent_period.insert(tk.END, period_to_scan)
lbl_ext.grid(row=0, column=0, stick="ne", padx=5)
ent_ext.grid(row=0, column=1, sticky="nw", padx=5)
lbl_period.grid(row=0, column=2, stick="nw", padx=5)
ent_period.grid(row=0, column=3, sticky="nw", padx=5)
ent_period["state"] = "normal"
frm_input_2.grid(row=2, columnspan=3, pady=5)
# Scan button
btn_scan = tk.Button(master=frm_input, text="Start Scan!", height=2,
                     width=29, font="Verdana 15 bold", command=check_scan)
btn_scan.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="nsw") 
# Stop button
btn_stop = tk.Button(master=frm_input, text="Stop!", height=2,
                     width=29, font="Verdana 15 bold", command=stop_periodic_scan)
btn_stop.grid(row=3, column=1, columnspan=2, padx=10, pady=20, sticky="nse")
frm_input.grid(row=1, column=0, sticky="n")
btn_stop["state"] = "disabled"


# Preview Report
frm_prv_report = tk.Frame(master=main_window)
frm_prv_report.columnconfigure(0, minsize=500, weight=1)
lbl_prv_report = tk.Label(master=frm_prv_report, text="Report Preview: ",
                          font="Verdana 15 bold")
lbl_prv_report.grid(row=0, sticky="nw")
frm_prv_report.grid(sticky="nsew", padx=20, pady=5, row=2)
txt_prv_report = tk.Text(master=frm_prv_report, relief=tk.RAISED, bd=1, height=10)
txt_prv_report.grid(row=1, column=0, sticky="nsew")


# Console
lbl_console = tk.Label(master=main_window, text='Console > ')
lbl_console.place(relx=0.0, rely=1.0, anchor="sw")


# mainloop
main_window.mainloop()
