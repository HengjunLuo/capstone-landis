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


# Escape key code
# A widely used option is the grave key
# Alt+` " ` " is also the button for " ~ ". Should be the button above tab
pause_keycode = r"'`'"
# Code for ctrl+c
#pause_keycode = r"'\x03'"

running = False
paused = False

logging_start_time = 0

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


# Create a logger to handle output to each file
mouse_logger = setup_logger("mouse_logger", "mouse_actions.log")
keyboard_logger = setup_logger("keyboard_logger", "keyboard_actions.log")

# Change directory where logs are saved
def set_log_directory(dir):
    global mouse_logger, keyboard_logger
    mouse_logger = setup_logger("mouse_logger", dir + "mouse_actions.log")
    keyboard_logger = setup_logger("keyboard_logger", dir + "keyboard_actions.log")


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
    log_action( keyboard_logger, "{0},pressed".format(str(key)) )
    if str(key) == pause_keycode:
        if paused: resume()
        else: pause()

def log_key_release(key):
    log_action( keyboard_logger, "{0},released".format(str(key)) )

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

    mouse_listener.start()
    keyboard_listener.start()

    running = True
    paused = False

# Stop listener threads
def stop():
    global running, paused

    mouse_listener.stop()
    keyboard_listener.stop()

    running = False
    paused = False

# Set pause flag true (stop logging)
def pause():
    global paused
    paused = True

# Set pause flag to false and continue logging
def resume():
    global paused
    paused = False
    


"""
Block main thread until escape key is pressed

def escape_key_press(key):
    if str(key) == pause_keycode:
        exit(0)

with keyboard.Listener(on_press=escape_key_press) as el:
    try:
        el.join() # Main thread blocks until Listener thread finishes
    except:
        ... # Suppress annoying error messages when program terminates
"""