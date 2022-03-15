"""
Input logging module
One thread for each input device (keyboard, mouse)

Dependencies:
- pynput

Considerations:
- Better way to log mouse movement actions?
"""

from pynput import mouse, keyboard
import pandas as pd
import time
import re


# Convenience structs to clarify code
# Object containing keyboard action information
class KeyboardAction:
    def __init__(self, time, key, action, profile, character):
        self.time = time
        self.key = key
        self.action = action
        self.profile = profile
        self.character = character

# Object containing mouse action information
class MouseAction:
    def __init__(self, time, x, y, button, action, profile, character):
        self.time = time
        self.x = x
        self.y = y
        self.button = button
        self.action = action
        self.profile = profile
        self.character = character

# Dicts of recorded input actions (basically the entire log but in RAM)
session_kb = {
    'time':   [],
    'key':    [],
    'action': [],
    'class':  []
}

session_ms = {
    'time':   [],
    'x':      [],
    'y':      [],
    'button': [],
    'action': [],
    'class':  []
}

# Pause key code
# A widely used option is the grave key
# Alt+` " ` " is also the button for " ~ ". Should be the button above tab
pause_keycode = r"'`'"

# Keep track of logger state
running = False
paused = False

# Keep track of logging time
logging_start_time = 0
pause_time = 0

# Default directory to save log files in
log_dir = "./"
keylog_filename = "key.log"
mouselog_filename = "mouse.log"

# Default class values when uninitialized
profile = "---"
character = "---"

# Keep track of currently pressed keys (ignore held repeated presses)
pressed_keys = set()

# Declare listeners
mouse_listener = None
keyboard_listener = None


# --------------------------- Public Interface ------------------------------- #

# Start threads (more importantly start the counter)
def start():
    global mouse_listener, keyboard_listener
    global logging_start_time, running, paused
    global session_kb, session_ms

    logging_start_time = time.perf_counter()

    # Reset recorded session data
    session_kb = {
        'time':   [],
        'key':    [],
        'action': [],
        'class':  []
    }

    session_ms = {
        'time':   [],
        'x':      [],
        'y':      [],
        'button': [],
        'action': [],
        'class':  []
    }

    # Create new event listener threads
    mouse_listener = mouse.Listener(
        on_move=log_move,
        on_click=log_click,
        on_scroll=log_scroll)
    keyboard_listener = keyboard.Listener(
        on_press=log_key_press,
        on_release=log_key_release)

    mouse_listener.start()
    keyboard_listener.start()

    running = True
    paused = False


# Stop listener threads
def stop():
    global running, paused

    running = False
    paused = False

    mouse_listener.stop()
    keyboard_listener.stop()


# Set pause flag true (stop logging)
def pause():
    global paused, pause_time
    paused = True
    pause_time = time.perf_counter()


# Set pause flag to false and continue logging
def resume():
    global paused, logging_start_time
    paused = False
    logging_start_time += (time.perf_counter() - pause_time)


# Get the amount of time the logger has been active for
def elapsed_time():
    if not paused:
        return time.perf_counter() - logging_start_time
    else:
        return pause_time - logging_start_time


# Change directory where logs are saved
def set_log_directory(new_dir):
    global log_dir
    log_dir = new_dir


# Set logging profile
def set_profile(selection):
    global profile
    profile = selection


# Set logging character
def set_character(selection):
    global character
    character = selection


# Set the key used to pause the logger
def set_pause_key(key):
    global pause_keycode

    if re.fullmatch("\S", key):
        pause_keycode = '\'' + key + '\''
    elif re.fullmatch("quoteleft", key):
        pause_keycode = r"'`'"
    elif re.fullmatch("Control_L", key):
        pause_keycode = "Key.ctrl_l"
    elif re.fullmatch("Control_R", key):
        pause_keycode = "Key.ctrl_r"
    elif re.fullmatch("Escape", key):
        pause_keycode = "Key.esc"
    elif re.fullmatch("Shift_L", key):
        pause_keycode = "Key.shift"
    elif re.fullmatch("Shift_R", key):
        pause_keycode = "Key.shift_r"
    elif re.fullmatch("Prior", key):
        pause_keycode = "Key.page_up"
    elif re.fullmatch("Next", key):
        pause_keycode = "Key.page_down"
    else:
        pause_keycode = f"Key.{key.lower()}"


# Save recorded data to logfile
def save_log():
    global mouse_logger, keyboard_logger

    # Create dataframes
    keybd_df = pd.DataFrame(session_kb)
    mouse_df = pd.DataFrame(session_ms)
    
    # Save dataframes to file
    keybd_df.to_csv(
        log_dir + keylog_filename,
        float_format="{:.4f}".format,
        header=False,
        index=False
    )

    mouse_df.to_csv(
        log_dir + mouselog_filename,
        float_format="{:.4f}".format,
        header=False,
        index=False
    )


# Get session dataframes
def get_session_dataframe(type = 'keyboard'):
    if type == 'keyboard':
        return pd.DataFrame(session_kb)
    elif type == 'mouse':
        return pd.DataFrame(session_ms)



# -------------------------- Internal functions ------------------------------ #

"""
Callback functions defining the specific formats in which inputs are logged
"""
def log_move(x, y):
    pass
    action = MouseAction(elapsed_time(), x, y, 'None', 'None', profile, character)
    log_action(action)

def log_click(x, y, button, pressed):
    click_type = 'pressed' if pressed else 'released'

    mouse_action = MouseAction(elapsed_time(), x, y, str(button)[7:], click_type, profile, character)
    log_action(mouse_action)

    keybd_action = KeyboardAction(elapsed_time(), f"Mouse.{str(button)[7:]}", click_type, profile, character)
    log_action(keybd_action)

def log_scroll(x, y, dx, dy):
    scroll_dir = 'down' if dy < 0 else 'up'

    action = MouseAction(elapsed_time(), x, y, 'scroll', str(scroll_dir), profile, character)
    log_action(action)

def log_key_press(key):
    if str(key) == pause_keycode:
        if paused: resume()
        else: pause()

    else:
        # Special case: comma key (since logfile is comma separated)
        str_key = str(key)
        if str_key == "','":
            str_key = 'Key.comma'

        if key not in pressed_keys:
            action = KeyboardAction(elapsed_time(), str_key, 'pressed', profile, character)
            log_action(action)
            pressed_keys.add(key)

def log_key_release(key):
    if str(key) != pause_keycode:
        # Special case: comma key (since logfile is comma separated)
        str_key = str(key)
        if str_key == "','":
            str_key = 'Key.comma'
        
        action = KeyboardAction(elapsed_time(), str_key, 'released', profile, character)
        log_action(action)
        pressed_keys.discard(key)


"""    
Intermediary logging function
Make the script more readable and less error-prone
"""
def log_action(action):
    if not paused:
        if type(action) is KeyboardAction:
            session_kb['time'].append(action.time)
            session_kb['key'].append(action.key)
            session_kb['action'].append(action.action)
            session_kb['class'].append(action.profile + action.character)
        elif type(action) is MouseAction:
            session_ms['time'].append(action.time)
            session_ms['x'].append(action.x)
            session_ms['y'].append(action.y)
            session_ms['button'].append(action.button)
            session_ms['action'].append(action.action)
            session_ms['class'].append(action.profile + action.character)
    
