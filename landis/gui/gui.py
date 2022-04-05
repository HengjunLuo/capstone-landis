"""
LANDIS GUI
"""

import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from backend import keylogger
from backend import classifier
from backend import keyboard_heatmap

from gui import config
from gui import actions
from gui import values
from gui import frames

# TkAgg backend is made to integrate matplotlib to TKinter
matplotlib.use('TkAgg')


class LandisLogger(tk.Tk):

    def __init__(self):
        super().__init__()

        # Window dimensions
        _windowwidth = 800
        _windowheight = 550

        # Setup actions module
        actions.gui_app = self

        # Load user preferences and update logger
        actions.load_preferences()

        # Persistent variable initial values
        self.pausekey = "`"
        self.log_dir = './'
        self.curr_profile = tk.StringVar()
        self.curr_profile.set("Profile")
        self.curr_character = tk.StringVar()
        self.curr_character.set("Character")
        self.curr_method = tk.StringVar()
        self.curr_method.set("None")
        self.curr_target = tk.StringVar()
        self.curr_target.set("None")

        # Classifier
        self.classifier = None
        self.curr_prediction = tk.StringVar()
        self.curr_prediction.set("---")

        # To keep track of logger running status
        self.started = False
        # Text control variable used for showing elapsed time
        self.elapsed_time = tk.StringVar()
        self.elapsed_time.set("00m 00s")

        # Default to using the default log directories
        self.use_default_dir = tk.IntVar()
        self.use_default_dir.set(1)

        # Initialize main window settings
        config.configure_window(self, _windowwidth, _windowheight)

        # ----- Frame widgets -----
        self.frm_logger     = tk.Frame(self)
        self.frm_classifier = tk.Frame(self)
        self.frm_status     = tk.Frame(self)
        self.frm_settings   = tk.Frame(self)
        self.heatmap_canvas = tk.Canvas(self, bg='#eee', width=750)

        # Load heatmap background images
        self.kb_image = tk.PhotoImage(file="images/qwerty-kb.gif")
        self.ms_image = tk.PhotoImage(file="images/mouse.gif")

        # Position frames in window
        config.configure_frames(self, _windowwidth, _windowheight)

        # ----- Logger widgets -----
        self.lbl_running   = tk.Label(self.frm_logger, width=25, font=('Helvetica', 20, 'bold'))
        self.lbl_loglength = tk.Label(self.frm_logger, text="Log length:",font=('Helvetica',9,'bold'))
        self.lbl_time      = tk.Label(self.frm_logger, textvariable=self.elapsed_time, width=6)

        # ----- Classifier widgets -----
        self.lbl_method = tk.Label(self.frm_classifier, text='Method:')
        self.btn_method = tk.OptionMenu(self.frm_classifier, self.curr_method, *values.methods)
        self.lbl_target = tk.Label(self.frm_classifier, text='Target:')
        self.btn_target = tk.OptionMenu(self.frm_classifier, self.curr_target, *values.targets)
        self.btn_verify = tk.Button(self.frm_classifier, text='Verify', width=11, state='disabled')

        # ----- Status widgets -----
        # Logger control
        self.btn_toggle     = tk.Button(self.frm_status, text='Start', width=7,bg='lightskyblue')
        self.btn_stop       = tk.Button(self.frm_status, text='Stop',  width=7, state='disabled')
        self.btn_save       = tk.Button(self.frm_status, text='Save',  width=7, state='disabled')
        # Classifier results
        self.lbl_results     = tk.Label(self.frm_status, text="Result:",width=7)
        self.lbl_prediction = tk.Label(self.frm_status, text="Prediction:")
        self.lbl_pred       = tk.Label(self.frm_status, text = "---", width=25)
        self.lbl_pred_conf1  = tk.Label(self.frm_status, text = "---", width=25)
        self.lbl_pred_conf2  = tk.Label(self.frm_status, text = "---", width=25)
        self.lbl_pred_conf3  = tk.Label(self.frm_status, text = "---", width=25)
        self.lbl_pred_conf4  = tk.Label(self.frm_status, text = "---", width=25)
        self.lbl_pred_conf5  = tk.Label(self.frm_status, text = "---", width=25)
        self.lbl_pred_conf6  = tk.Label(self.frm_status, text = "---", width=25)
        self.lbl_pred_conf7  = tk.Label(self.frm_status, text = "---", width=25)
        
        # ----- Settings widgets -----
        # Profile modification
        self.lbl_profile = tk.Label(self.frm_settings, text='Profile:')
        self.btn_profile = tk.OptionMenu(self.frm_settings, self.curr_profile, *values.profiles)
        # Pause key modification
        self.lbl_pausekey = tk.Label(self.frm_settings, width=10)
        self.ent_pausekey = tk.Entry(self.frm_settings, width=10, state='readonly', 
                readonlybackground='white', justify='center')
        self.btn_setpausekey = tk.Button(self.frm_settings, text="Set pause key")
        # Log directories modification
        self.chk_override = tk.Checkbutton(self.frm_settings, text="Override default directory", variable=self.use_default_dir)
        self.lbl_log_dir = tk.Label(self.frm_settings, width=30)
        self.ent_log_dir = tk.Entry(self.frm_settings, state='disabled')
        self.btn_set_log_dir = tk.Button(self.frm_settings, text="Set directory", width=11, state='disabled')
        # Info bar (along bottom, hidden initially)
        self.lbl_settings_info = tk.Label(self.frm_settings, font=("Helvetica", 10, "italic"))

        # Position widgets
        config.configure_logger_widgets(self)
        config.configure_classifier_widgets(self)
        config.configure_status_widgets(self)
        config.configure_settings_widgets(self)

        # Initialize keylogger values
        keylogger.set_pause_key(self.pausekey)
        keylogger.set_profile(self.curr_profile.get())
        keylogger.set_character(self.curr_character.get())
        keylogger.set_log_directory(actions.get_default_log_directory())

        # Bind actions to inputs
        actions.bind()


# Entry point for the gui
def start():
    # Create main window
    gui = LandisLogger()
    # Block until window closes
    gui.mainloop()

# Run when module is not being initialized from an import statement
if __name__ == '__main__':
    start()
