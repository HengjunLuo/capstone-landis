"""
TODO:
- Integrate file system control for:
  - Validating paths
  - Moving logfiles when path changes
  - Loading and saving user preferences
"""


import input_logger as keylogger

import tkinter as tk

# Variables editable by gui
pausekey = "`"
root_logdir = "./"
started = False

# Non-editable names of log files
mouse_logdir = "mouse_actions.log"
kb_logdir = "keyboard_actions.log"

# Window settings
_windowwidth  = 400
_windowheight = 300

# Main window
gui = tk.Tk()
#gui.geometry(f"{_windowwidth}x{_windowheight}")
gui.resizable(False, False)
gui.rowconfigure(0, minsize=_windowheight/2, weight=1)
gui.rowconfigure(1, minsize=_windowheight/2, weight=1)
gui.columnconfigure(0, minsize=_windowwidth, weight=1)

# ----- Frame widgets -----
# Input logger status frame
frm_status = tk.Frame(gui, width=400)
frm_status.rowconfigure(0, minsize=50)
frm_status.columnconfigure(0, minsize=100, weight=1)
frm_status.columnconfigure(3, minsize=100, weight=1)

# Settings frame
frm_settings = tk.Frame(gui, width=400)

# Frame positioning
frm_status.grid(row=0, sticky="ns")
frm_settings.grid(row=1, sticky="ns")


# ----- Status widgets -----
lbl_running = tk.Label(frm_status, width=30)
btn_toggle = tk.Button(frm_status, text="Start", width=7)
btn_stop = tk.Button(frm_status, text="Stop", state='disabled', width=7)

# Status widgets positioning
lbl_running.grid(row=0, column=1, columnspan=2)
btn_toggle.grid(row=1, column=1, padx=5)
btn_stop.grid(row=1, column=2, padx=5)


# Status widget behavior
def update_lbl_status(status):
    lbl_running['text'] = f"Input logger status: {status}"

def toggle_status(event):
    global started
    # State machine of toggle button
    if btn_toggle['text'] == "Start":
        keylogger.start()
        btn_toggle['text'] = "Pause"
        btn_stop['state'] = 'normal'
        started = True
        check_status() # Start periodic status update checks
    elif btn_toggle['text'] == "Pause":
        keylogger.pause()
        btn_toggle['text'] = "Resume"
    elif btn_toggle['text'] == "Resume":
        keylogger.resume()
        update_lbl_status("Running")
        btn_toggle['text'] = "Pause"

def stop_keylogger(event):
    global started
    # Stop keylogger
    keylogger.stop()
    btn_toggle['text'] = "Start"
    btn_stop['state'] = 'disabled'
    update_lbl_status("Stopped")

def check_status():
    if keylogger.running == False:
        btn_toggle['text'] = "Start"
        btn_stop['state'] = 'disabled'
        update_lbl_status("Stopped")
    else:
        if keylogger.paused == True:
            update_lbl_status("Paused")
            btn_toggle['text'] = "Resume"
        else:
            update_lbl_status("Running")
            btn_toggle['text'] = "Pause"

    if keylogger.running:
        gui.after(1000, check_status) # Run this function every second


# Assign settings widget behavior
btn_toggle.bind('<Button-1>', toggle_status)
btn_stop.bind('<Button-1>', stop_keylogger)

# Fill text fields with initial values
update_lbl_status("Not started")


# ----- Settings widgets -----
# Title and info bar
lbl_settings = tk.Label(frm_settings, text="Settings", font=("Helvetica", 16, "bold"))
lbl_settings_info = tk.Label(frm_settings, font=("Helvetica", 10, "italic"))

# Pause key modification
lbl_pausekey = tk.Label(frm_settings)
ent_pausekey = tk.Entry(frm_settings, width=3)
btn_setpausekey = tk.Button(frm_settings, text="Set new exit key")

# Log directories modification
lbl_logdirs = tk.Label(frm_settings)
ent_logdir = tk.Entry(frm_settings)
btn_setlogdir = tk.Button(frm_settings, text="Set new directory")

# Settings widgets positioning
lbl_settings.grid(row=0, columnspan=2) # Along the top
lbl_settings_info.grid(row=4, columnspan=2) # Along the bottom

lbl_pausekey.grid(row=1, column=0)
ent_pausekey.grid(row=2, column=0)
btn_setpausekey.grid(row=3, column=0)

lbl_logdirs.grid(row=1, column=1)
ent_logdir.grid(row=2, column=1)
btn_setlogdir.grid(row=3, column=1)

# Settings widget behavior
def update_lbl_pausekey():
    lbl_pausekey['text'] = f"Exit key: {pausekey}"

def update_lbl_logdirs():
    lbl_logdirs['text'] = root_logdir + mouse_logdir + '\n' + root_logdir + kb_logdir

def set_pausekey(event):
    global pausekey
    userinput = ent_pausekey.get()

    # some input checking...
    valid = False



    if valid:
        ent_pausekey.delete(0, 'end')
        lbl_settings_info['text'] = ""
        lbl_settings_info.configure(fg="#000000")
        
        pausekey = userinput
        keylogger.pause_keycode = f'{pausekey}'
        update_lbl_pausekey()
    else:
        lbl_settings_info['text'] = f"Invalid key: {userinput}"
        lbl_settings_info.configure(fg="#ff0000")

    

def set_log_directory(event):
    global root_logdir
    userinput = ent_logdir.get()
    
    # some input checking...
    valid = True
    if userinput[-1] != '/':
        userinput += '/' # Append forward slash if necessary

    # Check if path is valid...
    
    if valid:
        ent_logdir.delete(0, 'end')
        lbl_settings_info['text'] = ""
        lbl_settings_info.configure(fg="#000000")
        
        root_logdir = userinput
        update_lbl_logdirs()
    else:
        lbl_settings_info['text'] = f"Invalid directory: {userinput}"
        lbl_settings_info.configure(fg="#ff0000")


# Assign settings widget behavior
btn_setpausekey.bind('<Button-1>', set_pausekey)
ent_pausekey.bind('<Return>', set_pausekey)
btn_setlogdir.bind('<Button-1>', set_log_directory)
ent_logdir.bind('<Return>', set_log_directory)

# Fill text fields with initial values
update_lbl_pausekey()
update_lbl_logdirs()


# Block until window closes
gui.mainloop()