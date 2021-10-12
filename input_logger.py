"""
Input logging script
One thread for each input device (keyboard, mouse)
Main thread blocks until escape key is pressed (ctrl+c)

Dependencies:
- pynput

Considerations:
- Better way to log mouse movement actions?
- Should there be an escape key at all or should the process be stopped through
another method? (e.g. Task manager)
- Should log files be cleared automatically when script is run?
- Input logging format?
"""

from pynput import mouse, keyboard
import logging

# Escape key code
escape_keycode = r"'\x03'" # Code for ctrl+c

# Another widely used option is the grave key:
#escape_keycode = r"'`'"

"""
Logging mechanism:
    Record all keystrokes to "keyboard_actions.log" (same directory)
    Record all mouse actions to "mouse_actions.log" (same directory)

I basically just grabbed the setup_logger code from some stackechange thread
so I dont really know how it works but it does
"""
def setup_logger(name, log_filename):
    handler = logging.FileHandler(log_filename)
    # This line determines the overall log format
    handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger

mouse_logger = setup_logger("mouse_logger", "mouse_actions.log")
keyboard_logger = setup_logger("keyboard_logger", "keyboard_actions.log")

"""
Functions defining the specific formats in which inputs are logged
"""
def log_move(x, y):
    mouse_logger.info(str((x, y)))

def log_click(x, y, button, pressed):
    click_type = 'Pressed' if pressed else 'Released'
    mouse_logger.info("{0} {1}".format(click_type, str((x, y))))

def log_scroll(x, y, dx, dy):
    scroll_dir = 'down' if dy < 0 else 'up'
    mouse_logger.info("scroll_{0} {1}".format(str(scroll_dir), str((x, y))))

def log_key_press(key):
    keyboard_logger.info("pressed {0}".format(str(key)))

def log_key_release(key):
    keyboard_logger.info("released {0}".format(str(key)))

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

with keyboard.Listener(on_press=escape_key_press, suppress=True) as el:
    el.join() # Main thread blocks until Listener thread finishes
