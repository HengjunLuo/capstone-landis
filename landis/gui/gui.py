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

        # Default to using the default log directories
        self.use_default_dir = tk.IntVar()
        self.use_default_dir.set(1)


        # Window dimensions
        _windowwidth = 800
        _windowheight = 450

        # Main window settings
        config.configure_window(self, _windowwidth, _windowheight)

        # ----- Frame widgets -----
        self.frm_status = tk.Frame(self, width=_windowwidth)
        self.collapse = frames.CollapsableFrame(self, "settings")
        self.frm_settings = tk.Frame(self.collapse.sub_frame, width=_windowwidth)
        config.configure_frames(self, _windowwidth, _windowheight)


        # ----- Status widgets -----
        # Text control variable used for showing elapsed time
        self.elapsed_time = tk.StringVar()
        self.elapsed_time.set("00m 00s")

        # Create widgets
        self.lbl_running = tk.Label(self.frm_status, width=25, font=('Helvetica', 20, 'bold'))
        self.btn_toggle = tk.Button(self.frm_status, text='Start', width=7,bg='lightskyblue')
        self.btn_stop   = tk.Button(self.frm_status, text='Stop',  width=7, state='disabled')
        self.btn_save   = tk.Button(self.frm_status, text='Save',  width=7, state='disabled')
        self.btn_verify = tk.Button(self.frm_status, text='Verify', width=11, state='disabled')
        self.lbl_result = tk.Label(self.frm_status, text="Result:",width=7)

        self.lbl_prediction = tk.Label(self.frm_status, text="Prediction:")
        self.lbl_predicted = tk.Label(self.frm_status, textvariable=self.curr_prediction, width=20)

        self.lbl_profile = tk.Label(self.frm_status, text='Profile:')
        self.lbl_character = tk.Label(self.frm_status, text='Character:')
        self.lbl_method = tk.Label(self.frm_status, text='Method:')
        self.lbl_target = tk.Label(self.frm_status, text='Target:')
        self.btn_profile = tk.OptionMenu(self.frm_status, self.curr_profile, *values.profiles)
        self.btn_character = tk.OptionMenu(self.frm_status, self.curr_character, *values.characters)
        self.btn_method = tk.OptionMenu(self.frm_status, self.curr_method, *values.methods)
        self.btn_target = tk.OptionMenu(self.frm_status, self.curr_target, *values.targets)

        self.lbl_loglength = tk.Label(self.frm_status, text="Log length:",font=('Helvetica',9,'bold'))
        self.lbl_time = tk.Label(self.frm_status, textvariable=self.elapsed_time, width=6)

        # ------------------
        # ------------------
        # ------------------
        # ------------------
        # PLACEHOLDER FIGURE FOR KEYBOARD HEATMAP
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=6, column=0)
        # ------------------
        # ------------------
        # ------------------
        # ------------------

        # ----- Settings widgets -----
        # Title and info bar
        self.lbl_settings_info = tk.Label(self.frm_settings, font=("Helvetica", 10, "italic"))

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

        config.configure_status_widgets(self)
        config.configure_settings_widgets(self)

        keylogger.set_pause_key(self.pausekey)
        keylogger.set_profile(self.curr_profile.get())
        keylogger.set_character(self.curr_character.get())

        # Set default log directory for keylogger
        keylogger.set_log_directory(actions.get_default_log_directory())

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
