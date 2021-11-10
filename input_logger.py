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

running = False
paused = False

log_dir = None

logging_start_time = 0
pause_time = 0

# Keep track of currently pressed keys (remove repeated presses)
pressed_keys = set()

"""
Logging mechanism:
    Record all keystrokes to "keyboard_actions.log" (same directory)
    Record all mouse actions to "mouse_actions.log" (same directory)
    Records are logged as csv files for easy parsing
    Clears old log files every time keylogger is run
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


# Declare loggers
mouse_logger = None
keyboard_logger = None

# Initialize loogers and create logging files
def create_loggers():
    global mouse_logger, keyboard_logger
    # Create a logger to handle output to each file
    mouse_logger = None
    keyboard_logger = None
    mouse_logger = setup_logger(str(random.randrange(1000)), log_dir + "mouse_actions.log")
    keyboard_logger = setup_logger(str(random.randrange(1000)), log_dir + "keyboard_actions.log")

# Change directory where logs are saved
def set_log_directory(dir):
    global log_dir
    log_dir = dir

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


"""
Functions defining the specific formats in which inputs are logged
"""
def log_move(x, y):
    log_action( mouse_logger, f"{x:04},{y:04},None,None" )

def log_click(x, y, button, pressed):
    click_type = 'pressed' if pressed else 'released'
    log_action( mouse_logger, "{0},{1},{2}".format(f"{x:04},{y:04}", str(button)[7:], click_type) )

def log_scroll(x, y, dx, dy):
    scroll_dir = 'down' if dy < 0 else 'up'
    log_action( mouse_logger, "{0},scroll,{1}".format(f"{x:04},{y:04}", str(scroll_dir)) )

def log_key_press(key):
    if str(key) == pause_keycode:
        if paused: resume()
        else: pause()
    else:
        if key not in pressed_keys:
            log_action( keyboard_logger, "{0},pressed".format(str(key)) )
            pressed_keys.add(key)

def log_key_release(key):
    if str(key) != pause_keycode:
        log_action( keyboard_logger, "{0},released".format(str(key)) )
        pressed_keys.remove(key)

"""    
Intermediary logging function
Make the script more readable and less error-prone
"""
def log_action( logger, message):
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
    