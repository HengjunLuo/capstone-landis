"""
Input logging module
One thread for each input device (keyboard, mouse)

Dependencies:
- pynput

Considerations:
- Better way to log mouse movement actions?
"""

from pynput import mouse, keyboard
import time
import logging
import re
import random

# Escape key code
# A widely used option is the grave key
# Alt+` " ` " is also the button for " ~ ". Should be the button above tab
pause_keycode = r"'`'"
# Code for ctrl+c
#pause_keycode = r"'\x03'"

# Keep track of logger state
running = False
paused = False

# Declare loggers
mouse_logger = None
keyboard_logger = None
logname = 0 # Increments for each new log

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

# Keep track of currently pressed keys (remove repeated presses)
pressed_keys = set()

"""
Logging mechanism:
    Record all keystrokes to "key.log"
    Record all mouse actions to "mouse.log"
    Records are logged as csv files for easy parsing
    Overwrites existing log files in save location
"""
def setup_logger(name, log_filename):
    # File handler manages i/o to the logfile
    handler = logging.FileHandler(log_filename, mode='w')
    
    # This line determines the general log format ([elapsed time]: [action])
    handler.setFormatter(logging.Formatter('%(elapsed_time).4f,%(message)s')) # the '.4' determines how many decimal places to log

    # Initialize the logger and attach the handler
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

# Initialize loggers and create logging files
def create_loggers():
    global mouse_logger, keyboard_logger, logname

    # Reset loggers if logger is being re-started
    mouse_logger = None
    keyboard_logger = None

    # Create keyboard logger and increment name
    keyboard_logger = setup_logger(str(logname), log_dir + keylog_filename)
    logname += 1 # Ensure unique names

    # Create mouse logger and increment name
    mouse_logger = setup_logger(str(logname), log_dir + mouselog_filename)
    logname += 1 # Ensure unique names


# Change directory where logs are saved
def set_log_directory(new_dir):
    global log_dir
    log_dir = new_dir


# Change the pause key
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

def set_profile(selection):
    global profile
    profile = selection

def set_character(selection):
    global character
    character = selection

"""
Functions defining the specific formats in which inputs are logged
"""
def log_move(x, y):
    log_action( mouse_logger, "{0},None,None,{1}".format(f"{x:04},{y:04}", profile + character) )

def log_click(x, y, button, pressed):
    click_type = 'pressed' if pressed else 'released'
    log_action( mouse_logger, "{0},{1},{2},{3}".format(f"{x:04},{y:04}", str(button)[7:], click_type, profile + character) )

def log_scroll(x, y, dx, dy):
    scroll_dir = 'down' if dy < 0 else 'up'
    log_action( mouse_logger, "{0},scroll,{1},{2}".format(f"{x:04},{y:04}", str(scroll_dir), profile + character) )

def log_key_press(key):
    if str(key) == pause_keycode:
        if paused: resume()
        else: pause()
    else:
        # Special case: comma key (since logfile is commma separated)
        str_key = str(key)
        if str_key == "','":
            str_key = 'Key.comma'

        if key not in pressed_keys:
            log_action( keyboard_logger, "{0},pressed,{1}".format(str_key, profile + character) )
            pressed_keys.add(key)

def log_key_release(key):
    if str(key) != pause_keycode:
        # Special case: comma key (since logfile is commma separated)
        str_key = str(key)
        if str_key == "','":
            str_key = 'Key.comma'
            
        log_action( keyboard_logger, "{0},released,{1}".format(str_key, profile + character) )
        pressed_keys.discard(key)

"""    
Intermediary logging function
Make the script more readable and less error-prone
"""
def log_action(logger, message):
    if not paused:
        logger.info(message, 
            extra={'elapsed_time': time.perf_counter() - logging_start_time})

# Declare listeners
mouse_listener = None
keyboard_listener = None

# "Start" threads (more importantly start the counter)
def start():
    global mouse_listener, keyboard_listener, logging_start_time, running, paused
    logging_start_time = time.perf_counter()

    #Create new event listener threads
    mouse_listener = mouse.Listener(
        on_move=log_move,
        on_click=log_click,
        on_scroll=log_scroll)
    keyboard_listener = keyboard.Listener(
        on_press=log_key_press,
        on_release=log_key_release)

    create_loggers()

    mouse_listener.start()
    keyboard_listener.start()

    running = True
    paused = False

# Stop listener threads
def stop():
    global running, paused, mouse_logger, keyboard_logger

    mouse_listener.stop()
    keyboard_listener.stop()
    mouse_logger.handlers[0].close()
    keyboard_logger.handlers[0].close()
    mouse_logger = None
    keyboard_logger = None

    running = False
    paused = False

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