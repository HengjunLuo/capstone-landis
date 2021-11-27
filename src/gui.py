"""
Simple User Interface for keylogger
We may consider routing all future project functionality through this GUI

Dependencies:
- None

Known issues:
- Changing the log location while program is running is unreliable
  (May just write to previous location until UI is restarted)
- Unable to capture keystroke combinations for pausing (eg. ctrl+c)
"""

import input_logger as keylogger
import tkinter as tk
import pathlib

# Profiles to choose from
profiles = [
    "JON",
    "MAR",
    "ZIR",
    "JOS",
    "HEN",
    "MIT",
    "OTH"
]

characters = [
    "SCO",
    "SOL",
    "PYR",
    "DEM",
    "HEA",
    "ENG",
    "MED",
    "SNI",
    "SPY"
]

# Create main window
gui = tk.Tk()

# Persistent variable initial values
pausekey = "`"
keylog_filename = "keyboard_actions.log"
mouselog_filename = "mouse_actions.log"
curr_profile = tk.StringVar()
curr_profile.set("profile")
curr_character = tk.StringVar()
curr_character.set("character")

started = False

# Window settings
_windowwidth  = 375
_windowheight = 250

def get_log_directory():
    return "./src/logs/" + curr_profile.get() + '/' + curr_character.get() + '/'

# Save user preferences
def save_preferences():
    with open('./src/.preferences', 'w', encoding='utf-8') as f:
            f.write("pausekey: " + pausekey + '\n')
            f.write("profile: " + curr_profile.get() + '\n')
            f.write("character: " + curr_character.get() + '\n')

# Save logfile path to routing file
def update_routing_table():

    # Copy logfile paths into convenient variables
    keylog_dir = lbl_keylog_dir['text'] + '\n'
    mouselog_dir = lbl_mouselog_dir['text'] + '\n'
    
    # Read all lines from routing file and check for matches
    with open('./src/.routing', 'r', encoding='utf-8') as f:
                entries = f.readlines()
                for entry in entries:
                    if entry == keylog_dir or entry == mouselog_dir:
                        return
    
    # Write logfile paths to routing file
    with open('./src/.routing', 'a', encoding='utf-8') as f:
            f.write(mouselog_dir)
            f.write(keylog_dir)

# Load user preferences
def load_preferences():
    global pausekey
    # Check that .preferences file exists
    file = pathlib.Path('./src/.preferences')
    if file.exists():
        # If any of the following operations fail, delete .preferences
        try:
            with open('./src/.preferences', 'r', encoding='utf-8') as f:
                data = f.readlines()
                # First line, extract from 10th character to the newline
                pausekey = data[0][10:-1]
                # Second line, extract from 9th character to the newline
                curr_profile.set(data[1][9:-1])
                # Third line, extract from 11th character to the end
                curr_character.set(data[2][11:-1])
        except:
            file.unlink() # unlink = delete

# Load user preferences and update logger
load_preferences()
keylogger.set_pause_key(pausekey)
keylogger.set_profile(curr_profile.get())
keylogger.set_character(curr_character.get())

# Main window
gui.title("Landis")
gui.resizable(False, False)
gui.rowconfigure(0, minsize=_windowheight/2, weight=1)
gui.rowconfigure(1, minsize=_windowheight/2, weight=1)
gui.columnconfigure(0, minsize=_windowwidth, weight=1)

# ----- Frame widgets -----
# Input logger status frame
frm_status = tk.Frame(gui, width=_windowwidth)
frm_status.rowconfigure(0, minsize=40)
frm_status.rowconfigure(1, minsize=35)
frm_status.columnconfigure(0, minsize=_windowwidth/5, weight=1)
frm_status.columnconfigure(4, minsize=_windowwidth/5, weight=1)

# Settings frame
frm_settings = tk.Frame(gui, width=_windowwidth)

# Frame positioning
frm_status.grid(row=0, sticky="ns")
frm_settings.grid(row=1, sticky="ns")

# ----- Status widgets -----
# Text control variable used for showing elapsed time
elapsed_time = tk.StringVar()
elapsed_time.set("00m 00s")

# Create widgets
lbl_running = tk.Label(frm_status, width=25, font=("Helvetica", 11, "bold"))
btn_toggle = tk.Button(frm_status, text="Start", width=7)
btn_stop = tk.Button(frm_status, text="Stop", state='disabled', width=7)

lbl_profile = tk.Label(frm_status, text='Profile:')
lbl_character = tk.Label(frm_status, text='Character:')
btn_profile = tk.OptionMenu(frm_status, curr_profile, *profiles)
btn_character = tk.OptionMenu(frm_status, curr_character, *characters)

lbl_loglength = tk.Label(frm_status, text="Log length:")
lbl_time = tk.Label(frm_status, textvariable=elapsed_time, width=6)

# Adjust widgets
btn_profile.config(width=8)
btn_character.config(width=8)

# Status widgets positioning
lbl_running.grid(row=0, column=0, columnspan=5, sticky='s')

lbl_loglength.grid(row=1, column=1, padx=10)
lbl_time.grid(row=1, column=2, sticky='w')

btn_toggle.grid(row=2, column=3, padx=1)
btn_stop.grid(row=3, column=3, padx=1)

lbl_profile.grid(row=2, column=0, sticky='e')
btn_profile.grid(row=2, column=1, padx=5, sticky='e')

lbl_character.grid(row=3, column=0, sticky='e')
btn_character.grid(row=3, column=1, padx=5, sticky='e')

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
    update_routing_table()

def set_profile(var, ix, op):
    update_lbl_logdirs()
    keylogger.set_profile(curr_profile.get())
    keylogger.set_mouselog_directory(lbl_mouselog_dir['text'])
    keylogger.set_keylog_directory(lbl_keylog_dir['text'])
    save_preferences()

def set_character(var, ix, op):
    update_lbl_logdirs()
    keylogger.set_character(curr_character.get())
    keylogger.set_mouselog_directory(lbl_mouselog_dir['text'])
    keylogger.set_keylog_directory(lbl_keylog_dir['text'])
    save_preferences()

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
    
    minutes, seconds = divmod(keylogger.elapsed_time(), 60)
    elapsed_time.set(f"{minutes:02.0f}m {seconds:02.0f}s")

    if keylogger.running:
        gui.after(100, check_status) # Run this function every 0.1s

# Assign settings widget behavior
btn_toggle.bind('<Button-1>', toggle_status)
btn_stop.bind('<Button-1>', stop_keylogger)
curr_profile.trace('w', set_profile)
curr_character.trace('w', set_character)

# Fill text fields with initial values
update_lbl_status("Not started")

# ----- Settings widgets -----
# Title and info bar
lbl_settings = tk.Label(frm_settings, text="Settings", font=("Helvetica", 14, "bold underline"))
lbl_settings_info = tk.Label(frm_settings, font=("Helvetica", 10, "italic"))

# Pause key modification
lbl_pausekey = tk.Label(frm_settings, width=10)
ent_pausekey = tk.Entry(frm_settings, width=10, state='readonly', 
        readonlybackground='white', justify='center')
btn_setpausekey = tk.Button(frm_settings, text="Set pause key")

# Log directories modification
lbl_keylog_dir = tk.Label(frm_settings, width=25)
lbl_mouselog_dir = tk.Label(frm_settings, width=25)
ent_keylog_dir = tk.Entry(frm_settings)
ent_mouselog_dir = tk.Entry(frm_settings)

# Settings widgets positioning
lbl_settings.grid(row=0, columnspan=4, pady=10) # Along the top
lbl_settings_info.grid(row=5, columnspan=4) # Along the bottom

# Position pausekey widgets
lbl_pausekey.grid(row=2, column=0)
ent_pausekey.grid(row=3, column=0)
btn_setpausekey.grid(row=4, column=0, padx=15)

# Log directory labels
lbl_keylog_dir.grid(row=1, column=2, columnspan=2)
lbl_mouselog_dir.grid(row=2, column=2, columnspan=2)

# Enter keyboard logfile directory
ent_keylog_dir.grid(row=3, column=2)

# Enter mouse logfile directory
ent_mouselog_dir.grid(row=4, column=2)

# Settings widget behavior

def update_lbl_pausekey(key):
    lbl_pausekey['text'] = f"Pause key: {key}"

def update_lbl_logdirs():
    lbl_keylog_dir['text'] = get_log_directory() + keylog_filename
    lbl_mouselog_dir['text'] = get_log_directory() + mouselog_filename

def set_pausekey(event):
    global pausekey

    gui.focus() # Take focus off entry widget
    userinput = ent_pausekey.get()
    ent_pausekey.delete(0, 'end')
    
    pausekey = userinput
    keylogger.set_pause_key(pausekey)
    update_lbl_pausekey(userinput)

    save_preferences()

def ent_pausekey_update(event):
    # Update contents of entry widget with key pressed
    ent_pausekey.config(state='normal')
    ent_pausekey.delete(0, 'end')
    ent_pausekey.insert(0, event.keysym)
    ent_pausekey.config(state='readonly')

# Assign settings widget behavior
btn_setpausekey.bind('<Button-1>', set_pausekey)
ent_pausekey.bind('<Return>', set_pausekey)

# Capture special keys in entry widget
ent_pausekey.bind('<Key>', ent_pausekey_update)

# Fill text fields with initial values
update_lbl_pausekey(pausekey)
update_lbl_logdirs()

# Set log directory for keylogger
keylogger.set_mouselog_directory(lbl_mouselog_dir['text'])
keylogger.set_keylog_directory(lbl_keylog_dir['text'])

# Block until window closes
gui.mainloop()