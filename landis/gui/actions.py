
import pathlib
import numpy as np

from backend import classifier
from backend import keylogger
from backend import keyboard_heatmap

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
    if keylogger.running:
        # Get the current session data as a DataFrame
        session_df = keylogger.get_session_dataframe('keyboard')
        
        # Get predictions
        prediction = gui_app.classifier.predict(session_df, seglength)
        
        # Update prediction in gui
        gui_app.curr_prediction.set(
            f"{gui_app.curr_method.get()}: {prediction}")

        # Re-run this function every [seglength] seconds
        #gui_app.after(seglength * 1000, gui_app.update_prediction, seglength)

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
        check_status()        # Start periodic status update checks
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

def verify(event):
    seglength = min(60, keylogger.elapsed_time())
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
        plot()
        gui_app.after(100, check_status) # Run this function every 0.1s


def plot():
    gui_app.ax.imshow(keyboard_heatmap.KeyboardHeatmap.heatmap_data_gui(keylogger.get_session_dataframe('keyboard')))
    gui_app.canvas.draw_idle()

    

def bind():
    # Assign settings widget behavior
    gui_app.btn_toggle.bind('<ButtonRelease-1>', toggle_status)
    gui_app.btn_stop.bind('<ButtonRelease-1>', stop_keylogger)
    gui_app.btn_save.bind('<ButtonRelease-1>', save_log)
    gui_app.btn_verify.bind('<ButtonRelease-1>', verify)
    gui_app.curr_profile.trace('w', set_profile)
    gui_app.curr_character.trace('w', set_character)
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