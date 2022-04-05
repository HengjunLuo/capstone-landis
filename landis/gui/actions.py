
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import time
import tkinter as tk


from backend import classifier
from backend import keylogger
from backend import keyboard_heatmap
from backend import log_parser

from gui import values


gui_app = None


"""
Classification methods
"""
def set_classifier(var, ix, op):
    # Call to initialize and train a classifier for the selected parameters
    # Important parameters are target class, profile, and the type of classifier
    # For now solution will only use decision tree
    # Training takes a few seconds, so we dont want to call it every time a gui option is changed
    # For now, we will call it when user selects start
    gui_app.classifier = classifier.LANDIS_classifier(
        gui_app.curr_target.get(),
        gui_app.curr_method.get()
    )


def update_prediction(seglength):
    # Get the current session data as a DataFrame
    session_df = keylogger.get_session_dataframe('keyboard')
    
    # Get prediction matrix 
    prediction = gui_app.classifier.predict(session_df, seglength)
    # Print prediction matrix, 2 indices for binary and 6 for non binary
    gui_app.lbl_pred_conf1['text'] = prediction
    #gui_app.lbl_pred['text'] = prediction

    i = 0
    # binary
    if len(prediction) == 2:
        if prediction[1] > 0.5:
            gui_app.lbl_pred.config(bg="green")
            gui_app.lbl_pred['text'] = "Non-Fraudulent"
            gui_app.lbl_pred_conf1['text'] = str(round(prediction[1]*100, 0)) + "% Confident" 
        else:
            gui_app.lbl_pred.config(bg="red")
            gui_app.lbl_pred['text'] = "Fraudulent"
            gui_app.lbl_pred_conf1['text'] = str(round(prediction[1]*100, 0)) + "% Confident"
    # non binary, chose yellow as display color as the classifier is making a prediction (guess). We can tune this 50% value as we see fit
    elif gui_app.classifier.target == "GRP":
        gui_app.lbl_pred_conf1['text'] = values.profilesGRP[0] + " " + str(round(prediction[0]*100, 0)) + "%"
        gui_app.lbl_pred_conf2['text'] = values.profilesGRP[1] + " " + str(round(prediction[1]*100, 0)) + "%"
        gui_app.lbl_pred_conf3['text'] = values.profilesGRP[2] + " " + str(round(prediction[2]*100, 0)) + "%"
        gui_app.lbl_pred_conf4['text'] = values.profilesGRP[3] + " " + str(round(prediction[3]*100, 0)) + "%"
        gui_app.lbl_pred_conf5['text'] = values.profilesGRP[4] + " " + str(round(prediction[4]*100, 0)) + "%"
        gui_app.lbl_pred_conf6['text'] = values.profilesGRP[5] + " " + str(round(prediction[5]*100, 0)) + "%"
        # Made code cleaner
        for x in range(len(values.profiles)-1):
            if max(prediction) == prediction[x]:
                gui_app.lbl_pred.config(bg="yellow")
                gui_app.lbl_pred['text'] = values.profilesGRP[x] + " " + str(int(prediction[x]*100)) + "% Confident"
    # non binary, chose yellow as display color as the classifier is making a prediction (guess). We can tune this 50% value as we see fit
    elif gui_app.classifier.target == "NON":
        gui_app.lbl_pred_conf1['text'] = values.profilesOTH[0] + " " + str(round(prediction[0]*100, 0)) + "%"
        gui_app.lbl_pred_conf2['text'] = values.profilesOTH[1] + " " + str(round(prediction[1]*100, 0)) + "%"
        gui_app.lbl_pred_conf3['text'] = values.profilesOTH[2] + " " + str(round(prediction[2]*100, 0)) + "%"
        gui_app.lbl_pred_conf4['text'] = values.profilesOTH[3] + " " + str(round(prediction[3]*100, 0)) + "%"
        gui_app.lbl_pred_conf5['text'] = values.profilesOTH[4] + " " + str(round(prediction[4]*100, 0)) + "%"
        gui_app.lbl_pred_conf6['text'] = values.profilesOTH[5] + " " + str(round(prediction[5]*100, 0)) + "%"
        # Made code cleaner
        for x in range(len(values.profiles)-1):
            if max(prediction) == prediction[x]:
                gui_app.lbl_pred.config(bg="yellow")
                gui_app.lbl_pred['text'] = values.profilesOTH[x] + " " + str(int(prediction[x]*100)) + "% Confident"
                i = 1
        if i == 0:
            gui_app.lbl_pred.config(bg="red")
            gui_app.lbl_pred['text'] = "Unrecognized Player"
    
    # Old code left here in case we don't like change

    #gui_app.curr_prediction.set(
        #f"{gui_app.curr_method.get()}: {prediction}")

    # Re-run this function every [seglength] seconds
    #gui_app.after(seglength * 1000, gui_app.update_prediction, seglength)


# Emulates a loading screen with three dots (...)
def loading(dots):
    gui_app.lbl_pred.config(bg="white")
    gui_app.lbl_pred_conf1['text'] = "---"
    gui_app.lbl_pred_conf2['text'] = "---"
    gui_app.lbl_pred_conf3['text'] = "---"
    gui_app.lbl_pred_conf4['text'] = "---"
    gui_app.lbl_pred_conf5['text'] = "---"
    gui_app.lbl_pred_conf6['text'] = "---"
    # gui_app.lbl_pred_conf7['text'] = "---"
    for x in dots:
        gui_app.lbl_pred['text'] = x
        gui_app.update_idletasks()
        time.sleep(0.5)

"""
File persistence methods
"""
# Save user preferences
def save_preferences():
    with open('.preferences', 'w', encoding='utf-8') as f:
            f.write("pausekey: " + gui_app.pausekey + '\n')
            f.write("log_dir: " + gui_app.log_dir + '\n')
            f.write("profile: " + gui_app.curr_profile.get() + '\n')
            f.write("character: " + gui_app.curr_character.get() + '\n')

# Load user preferences
def load_preferences():
    # Check that .preferences file exists
    file = pathlib.Path('.preferences')
    if file.exists():
        # If any of the following operations fail, delete .preferences
        try:
            with open('.preferences', 'r', encoding='utf-8') as f:
                data = f.readlines()
                # First line, extract from 10th character to the newline
                gui_app.pausekey = data[0][10:-1]
                # Second line, extract from 9th character to the newline
                gui_app.log_dir = data[1][9:-1]
                # Third line, extract from 9th character to the newline
                gui_app.curr_profile.set(data[2][9:-1])
                # Fourth line, extract from 11th character to the newline
                gui_app.curr_character.set(data[3][11:-1])
        except:
            file.unlink() # unlink = delete


# Save logfile path to routing file
def update_routing_table():
    if gui_app.use_default_dir.get():
        # Read all lines from routing file and check for matches
        with open('.routing', 'r', encoding='utf-8') as f:
                    entries = f.readlines()
                    for entry in entries:
                        if get_default_log_directory() in entry:
                            return # Found a match, exit method
        
        # Write logfile paths to routing file
        with open('.routing', 'a', encoding='utf-8') as f:
                f.write('./' + get_default_log_directory() + values.mouselog_filename + '\n')
                f.write('./' + get_default_log_directory() + values.keylog_filename + '\n')


def get_default_log_directory():
    return "logs/" + gui_app.curr_profile.get() + '/' + gui_app.curr_character.get() + '/'


"""
Widget behavior methods
"""
# Status widget behavior
def update_lbl_status(status):
    gui_app.lbl_running['text'] = f"Input logger status: {status}"

# Start/pause/resume button behavior
def toggle_status(event):
    # State machine of toggle button
    if gui_app.btn_toggle['text'] == "Start":
        update_lbl_status("Training...")
        gui_app.update()
        keylogger.start()
        gui_app.btn_toggle['text']  = 'Pause'
        gui_app.btn_stop['state']   = 'normal'
        gui_app.btn_save['state']   = 'disabled'
        gui_app.btn_verify['state'] = 'normal'
        gui_app.started = True
        check_status()   # Start periodic status update checks
        plot()          # Start periodic plot updates
        # gui_app.update_prediction(60) # Start periodic predictions every 60s

    elif gui_app.btn_toggle['text'] == "Pause":
        keylogger.pause()
        gui_app.btn_toggle['text'] = "Resume"

    elif gui_app.btn_toggle['text'] == "Resume":
        keylogger.resume()
        update_lbl_status("Running")
        gui_app.btn_toggle['text'] = "Pause"

def stop_keylogger(event):
    # Stop keylogger
    keylogger.stop()
    gui_app.btn_toggle['text'] = "Start"
    gui_app.btn_stop['state'] = 'disabled'
    gui_app.btn_save['state'] = 'normal'
    update_lbl_status("Stopped")
    # Reset prediction labels
    gui_app.lbl_pred['text'] = "---"
    gui_app.lbl_pred_conf1['text'] = "---"
    gui_app.lbl_pred_conf2['text'] = "---"
    gui_app.lbl_pred_conf3['text'] = "---"
    gui_app.lbl_pred_conf4['text'] = "---"
    gui_app.lbl_pred_conf5['text'] = "---"
    gui_app.lbl_pred_conf6['text'] = "---"
    #gui_app.lbl_pred_conf7['text'] = "---"
    gui_app.lbl_pred.config(bg="white")

def verify(event):
    seglength = min(60, keylogger.elapsed_time())
    loading([".", ". .", ". . ."])
    update_prediction(seglength)

def save_log(event):
    update_lbl_status("Saving...")
    gui_app.update()
    keylogger.save_log()
    update_routing_table()
    update_lbl_status("Stopped")

def set_profile(var, ix, op):
    keylogger.set_profile(gui_app.curr_profile.get())
    save_preferences()
    
    if gui_app.use_default_dir.get():
        update_lbl_logdir()
        keylogger.set_log_directory(get_default_log_directory())
    

def set_character(var, ix, op):
    keylogger.set_character(gui_app.curr_character.get())
    save_preferences()

    if gui_app.use_default_dir.get():
        update_lbl_logdir()
        keylogger.set_log_directory(get_default_log_directory())

# Settings widget behavior
def update_lbl_pausekey(key):
    gui_app.lbl_pausekey['text'] = f"Pause key: {key}"

def update_lbl_logdir():
    if gui_app.use_default_dir.get():
        gui_app.lbl_log_dir['text'] = get_default_log_directory()
    else:
        gui_app.lbl_log_dir['text'] = gui_app.log_dir

def set_pausekey(event):
    gui_app.focus() # Take focus off entry widget
    userinput = gui_app.ent_pausekey.get()
    gui_app.ent_pausekey.delete(0, 'end')
    
    gui_app.pausekey = userinput
    keylogger.set_pause_key(gui_app.pausekey)
    update_lbl_pausekey(userinput)

    save_preferences()

def ent_pausekey_update(event):
    # Update contents of entry widget with key pressed
    gui_app.ent_pausekey.config(state='normal')
    gui_app.ent_pausekey.delete(0, 'end')
    gui_app.ent_pausekey.insert(0, event.keysym)
    gui_app.ent_pausekey.config(state='readonly')

def toggle_override(var, ix, op):
    # Default
    if gui_app.use_default_dir.get():
        gui_app.lbl_log_dir['text'] = get_default_log_directory()
        gui_app.ent_log_dir.config(state='disabled')
        gui_app.btn_set_log_dir.config(state='disabled')
        keylogger.set_log_directory(get_default_log_directory())
    # Override
    else:
        gui_app.ent_log_dir.config(state='normal')
        gui_app.btn_set_log_dir.config(state='normal')
        gui_app.lbl_log_dir['text'] = gui_app.log_dir
        keylogger.set_log_directory(gui_app.log_dir)
    

def set_log_directory(event):

    if event.widget.cget('state') == 'disabled':
        return

    gui_app.focus() # Take focus off entry widget
    userinput = gui_app.ent_log_dir.get()

    # some input checking...
    valid = True

    # If string is non-empty
    if userinput:
        # Replace any back slashes with forward slashes
        userinput = userinput.replace('\\', '/')

        # Append forward slash if necessary
        if userinput[-1] != '/':
            userinput += '/'

        if not pathlib.Path(userinput).exists():
            valid = False
    else:
        valid = False

    if valid:
        gui_app.ent_log_dir.delete(0, 'end')
        gui_app.lbl_settings_info['text'] = ""
        gui_app.lbl_settings_info.configure(fg="#000000")

        gui_app.log_dir = userinput
        keylogger.set_log_directory(gui_app.log_dir)
        update_lbl_logdir()

        save_preferences()
    else:
        gui_app.lbl_settings_info['text'] = f"Invalid directory: {userinput}"
        gui_app.lbl_settings_info.configure(fg="#ff0000")


"""
Method is called every 0.1s (10x per sec)
"""
def check_status():
    if keylogger.running == False:
        gui_app.btn_toggle['text'] = "Start"
        gui_app.btn_stop['state'] = 'disabled'
        update_lbl_status("Stopped")
    else:
        if keylogger.paused == True:
            update_lbl_status("Paused")
            gui_app.btn_toggle['text'] = "Resume"
        else:
            update_lbl_status("Running")
            gui_app.btn_toggle['text'] = "Pause"
    
    minutes, seconds = divmod(keylogger.elapsed_time(), 60)
    gui_app.elapsed_time.set(f"{minutes:02.0f}m {seconds:02.0f}s")

    if keylogger.running:
        gui_app.after(100, check_status)


def plot():
    # Get entire session as a dataframe
    session_df = keylogger.get_session_dataframe('keyboard')
    # Get last 60s of gameplay
    segment = session_df
    if not session_df.empty:
        segment = session_df[session_df.time > (session_df.time.iloc[-1] - 60.0)]
    # Extract relevant features
    data = keyboard_heatmap.KeyboardHeatmap.heatmap_data_gui(segment)
    
    # Clear the canvas
    gui_app.heatmap_canvas.delete("all")

    # Draw keyboard and mouse images
    gui_app.heatmap_canvas.create_image(0, 10, anchor=tk.NW, image=gui_app.kb_image)
    gui_app.heatmap_canvas.create_image(580, 25, anchor=tk.NW, image=gui_app.ms_image)

    # Draw highlights for each key
    for key in keyboard_heatmap.KeyboardHeatmap.keyBindings:
        highlight_key(key, 
            data[0][keyboard_heatmap.KeyboardHeatmap.keyBindings.index(key)],
            data[1][keyboard_heatmap.KeyboardHeatmap.keyBindings.index(key)])

    if keylogger.running:
        gui_app.after(250, plot)


# Mapping of coordinates for each key
g_key_coords = {
    "w": (113, 67 ),  "a": (85 , 104),  "s": (122, 104),  "d": (159, 104),
    ".": (403, 141),  "q": (75 , 66 ),  "v": (215, 141),  "b": (253, 141),
    "r": (188, 67 ),  "1": (56 , 29 ),  "2": (94 , 29 ),  "3": (131, 29 ),
    "4": (169, 29 ),  "5": (206, 29 ),  "6": (243, 29 ),  "7": (281, 29 ),
    "8": (319, 29 ),  "9": (356, 29 ),  "0": (394, 29 ),  
    "Key.tab":   (28 , 67 ), "Key.space":  (258, 178), "Key.ctrl_l":  (24 , 178), 
    "Key.comma": (366, 141), "Mouse.left": (640, 60 ), "Mouse.right": (682, 60 )
}

def highlight_key(key, frequency, duration):
    x, y = g_key_coords[key]
    size = frequency * 25
    r = hex(min(int(duration * 200), 255))[2:]
    if len(r) == 1: 
        r = '0' + r
    g = hex(max(int(255 - (duration * 650)), 0))[2:]
    if len(g) == 1: 
        g = '0' + g
    draw_circle(x, y, size, f"#{r[0:2]}{g[0:2]}ff")

def draw_circle(x, y, size, color):
    if size != 0:
        size += 8 # Minimum circle size
        gui_app.heatmap_canvas.create_oval(x - (size / 2), y - (size / 2), 
            x + (size / 2), y + (size / 2), fill=color, outline='')

def bind():
    # Assign settings widget behavior
    gui_app.btn_toggle.bind('<ButtonRelease-1>', toggle_status)
    gui_app.btn_stop.bind('<ButtonRelease-1>', stop_keylogger)
    gui_app.btn_save.bind('<ButtonRelease-1>', save_log)
    gui_app.btn_verify.bind('<ButtonRelease-1>', verify)
    gui_app.curr_profile.trace('w', set_profile)
    gui_app.curr_method.trace('w', set_classifier)
    gui_app.curr_target.trace('w', set_classifier)

    # Assign settings widget behavior
    gui_app.use_default_dir.trace('w', toggle_override)

    gui_app.btn_setpausekey.bind('<Button-1>', set_pausekey)
    gui_app.ent_pausekey.bind('<Return>', set_pausekey)

    gui_app.btn_set_log_dir.bind('<Button-1>', set_log_directory)
    gui_app.ent_log_dir.bind('<Return>', set_log_directory)

    # Capture special keys in entry widget
    gui_app.ent_pausekey.bind('<Key>', ent_pausekey_update)

    # Actually end the program when the window closes
    gui_app.protocol("WM_DELETE_WINDOW", lambda : exit())