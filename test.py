import input_logger as keylogger
import log_parser
import dt
import tkinter as tk
import pathlib

classifier = dt.LANDIS_classifier("MARSOL", 100)
print(classifier.predict("./logs/JON/SPY/keyboard_actions.log"))