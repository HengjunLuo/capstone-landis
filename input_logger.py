"""
Input logging script
One thread for each input device (keyboard, mouse)
Main thread blocks until escape key is pressed (grave key `)

Dependencies:
- pynput

Considerations:
- Better way to log mouse movement actions?
- Should there be an escape key at all or should the process be stopped through
another method? (e.g. Task manager)
"""

from pynput import mouse, keyboard
import time
import logging

# Escape key code
# A widely used option is the grave key
# Alt+` " ` " is also the button for " ~ ". Should be the button above tab

escape_keycode = r"'`'"
#escape_keycode = r"'\x03'" # Code for ctrl+c

prog_start_time = time.perf_counter()

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

def log_key_release(key):
    log_action( keyboard_logger, "{0},released".format(str(key)) )
    
# Intermediary logging function
# Make the script more readable and less error-prone
def log_action(logger, message):
    logger.info(message, extra={'elapsed_time': time.perf_counter() - prog_start_time})

"""
Create event listener threads
"""
mouseListener = mouse.Listener(
    on_move=log_move,
    on_click=log_click,
    on_scroll=log_scroll)

keyboardListener = keyboard.Listener(
    on_press=log_key_press,
    on_release=log_key_release)

# Start threads
mouseListener.start()
keyboardListener.start()

"""
Block main thread until escape key is pressed
"""
def escape_key_press(key):
    if str(key) == escape_keycode:
        exit(0)

with keyboard.Listener(on_press=escape_key_press) as el:
    try:
        el.join() # Main thread blocks until Listener thread finishes
    except:
        ... # Suppress annoying error messages when program terminates
