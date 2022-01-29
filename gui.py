"""
Simple User Interface for keylogger
We may consider routing all future project functionality through this GUI

Dependencies:
- None

Known issues:
- Changing the log location while program is running is unreliable
  (May just write to previous location until UI is restarted)
- Unable to capture keystroke combinations for pausing (eg. ctrl+c)
"""

import input_logger as keylogger
import tkinter as tk
from tkinter import ttk 
import pathlib

import log_parser
import classifier

# Names of output files
keylog_filename = "key.log"
mouselog_filename = "mouse.log"

# Profiles to choose from
profiles = [
    "JON",
    "MAR",
    "ZIR",
    "JOS",
    "HEN",
    "MIT",
    "OTH"
]

characters = [
    "SCO",
    "SOL",
    "PYR",
    "DEM",
    "HEA",
    "ENG",
    "MED",
    "SNI",
    "SPY"
]

methods = [
    "RF",
    "KNN",
    "ANN"
]

class CollapsableFrame(tk.Frame):

    def __init__(self, parent, text="", *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.text = text
        self.show = False

        # Frames
        self.title_frame = tk.Frame(self)
        self.sub_frame = tk.Frame(self)

        self.title_frame.rowconfigure(0, minsize=35)
        self.title_frame.columnconfigure(0, minsize=335)

        self.title_frame.grid(sticky='e')

        self.lbl_title = tk.Label(self.title_frame, text="Show "+self.text, font=("Helvetica", 9, "italic"), pady=5, padx=15)
        self.lbl_title.grid(sticky='se')

        self.lbl_title.bind('<Enter>', self.highlight)
        self.lbl_title.bind('<Leave>', self.unhighlight)
        self.lbl_title.bind('<Button-1>', self.toggle)
        

    def toggle(self, event):
        self.show = not self.show
        if self.show:
            self.sub_frame.grid(row=1, column=0, sticky='nsew')
            self.lbl_title.configure(text="Hide "+self.text)
        else:
            self.sub_frame.grid_forget()
            self.lbl_title.configure(text="Show "+self.text)

    def highlight(self, event):
        self.lbl_title.config(font=("Helvetica", 9, "italic underline"))

    def unhighlight(self, event):
        self.lbl_title.config(font=("Helvetica", 9, "italic"))


class LandisLogger(tk.Tk):

    def __init__(self):
        super().__init__()

        # Persistent variable initial values
        self.pausekey = "`"
        self.log_dir = './'
        self.curr_profile = tk.StringVar()
        self.curr_profile.set("profile")
        self.curr_character = tk.StringVar()
        self.curr_character.set("character")
        self.curr_method = tk.StringVar()
        self.curr_method.set("method")

        # Classifier
        self.classifier = None
        self.curr_prediction = tk.StringVar()
        self.curr_prediction.set("---")

        # To keep track of logger running status
        self.started = False

        # Default to using the default log directories
        self.use_default_dir = tk.IntVar()
        self.use_default_dir.set(1)

        # Load user preferences and update logger
        self.load_preferences()
        keylogger.set_pause_key(self.pausekey)
        keylogger.set_profile(self.curr_profile.get())
        keylogger.set_character(self.curr_character.get())

        # Window dimensions
        _windowwidth = 350
        _windowheight = 75

        # Main window settings
        self.configure_window(_windowwidth, _windowheight)

        # ----- Frame widgets -----
        self.frm_status = tk.Frame(self, width=_windowwidth)
        self.collapse = CollapsableFrame(self, "settings")
        self.frm_settings = tk.Frame(self.collapse.sub_frame, width=_windowwidth)
        self.configure_frames(_windowwidth, _windowheight)


        # ----- Status widgets -----
        # Text control variable used for showing elapsed time
        self.elapsed_time = tk.StringVar()
        self.elapsed_time.set("00m 00s")

        # Create widgets
        self.lbl_running = tk.Label(self.frm_status, width=25, font=("Helvetica", 11, "bold"))
        self.btn_toggle = tk.Button(self.frm_status, text="Start", width=7)
        self.btn_stop = tk.Button(self.frm_status, text="Stop", state='disabled', width=7)

        self.lbl_prediction = tk.Label(self.frm_status, text="Prediction:")
        self.lbl_predicted = tk.Label(self.frm_status, textvariable=self.curr_prediction, width=6)

        self.lbl_profile = tk.Label(self.frm_status, text='Profile:')
        self.lbl_character = tk.Label(self.frm_status, text='Character:')
        self.lbl_method = tk.Label(self.frm_status, text='Method:')
        self.btn_profile = tk.OptionMenu(self.frm_status, self.curr_profile, *profiles)
        self.btn_character = tk.OptionMenu(self.frm_status, self.curr_character, *characters)
        self.btn_method = tk.OptionMenu(self.frm_status, self.curr_method, *methods)

        self.lbl_loglength = tk.Label(self.frm_status, text="Log length:")
        self.lbl_time = tk.Label(self.frm_status, textvariable=self.elapsed_time, width=6)

        self.configure_status_widgets()
        

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

        self.configure_settings_widgets()

        # Set default log directory for keylogger
        keylogger.set_log_directory(self.get_default_log_directory())


    """
    Classification methods
    """
    def init_classifier(self):
        # Call to initialize and train a classifier for the selected parameters
        # Important parameters are target class, profile, and the type of classifier
        # For now solution will only use decision tree
        # Training takes a few seconds, so we dont want to call it every time a gui option is changed
        # For now, we will call it when user selects start
        training_segment_length = 100
        self.classifier = classifier.LANDIS_classifier(self.curr_method.get(), self.curr_profile.get()+self.curr_character.get(), training_segment_length)

    
    def update_prediction(self):
        # Ideally we would have access to a dataframe that is being updates to by input_logger.py
        # For now this inefficient method will work
        if keylogger.running:
            self.curr_prediction.set(self.classifier.predict(self.lbl_log_dir['text']))
            self.after(60000, self.update_prediction) # Run this function every 60s

    """
    File persistence methods
    """
    # Save user preferences
    def save_preferences(self):
        with open('.preferences', 'w', encoding='utf-8') as f:
                f.write("pausekey: " + self.pausekey + '\n')
                f.write("log_dir: " + self.log_dir + '\n')
                f.write("profile: " + self.curr_profile.get() + '\n')
                f.write("character: " + self.curr_character.get() + '\n')

    # Load user preferences
    def load_preferences(self):
        # Check that .preferences file exists
        file = pathlib.Path('.preferences')
        if file.exists():
            # If any of the following operations fail, delete .preferences
            try:
                with open('.preferences', 'r', encoding='utf-8') as f:
                    data = f.readlines()
                    # First line, extract from 10th character to the newline
                    self.pausekey = data[0][10:-1]
                    # Second line, extract from 9th character to the newline
                    self.log_dir = data[1][9:-1]
                    # Third line, extract from 9th character to the newline
                    self.curr_profile.set(data[2][9:-1])
                    # Fourth line, extract from 11th character to the newline
                    self.curr_character.set(data[3][11:-1])
            except:
                file.unlink() # unlink = delete
    

    # Save logfile path to routing file
    def update_routing_table(self):
        print(f"Using default directory: {'True' if self.use_default_dir.get() else 'False'}")
        if self.use_default_dir.get():
            # Read all lines from routing file and check for matches
            with open('.routing', 'r', encoding='utf-8') as f:
                        entries = f.readlines()
                        for entry in entries:
                            if self.log_dir in entry:
                                return # Found a match, exit method
            
            # Write logfile paths to routing file
            with open('.routing', 'a', encoding='utf-8') as f:
                    f.write('./' + self.get_default_log_directory() + mouselog_filename + '\n')
                    f.write('./' + self.get_default_log_directory() + keylog_filename + '\n')


    def get_default_log_directory(self):
        return "logs/" + self.curr_profile.get() + '/' + self.curr_character.get() + '/'


    """
    Widget behavior methods
    """
    # Status widget behavior
    def update_lbl_status(self, status):
        self.lbl_running['text'] = f"Input logger status: {status}"

    # Start/pause/resume button behavior
    def toggle_status(self, event):
        # State machine of toggle button
        if self.btn_toggle['text'] == "Start":
            #self.init_classifier() not today boys
            keylogger.start()
            self.btn_toggle['text'] = "Pause"
            self.btn_stop['state'] = 'normal'
            self.started = True
            self.check_status() # Start periodic status update checks
            #self.update_prediction() nope nope nope
        elif self.btn_toggle['text'] == "Pause":
            keylogger.pause()
            self.btn_toggle['text'] = "Resume"
        elif self.btn_toggle['text'] == "Resume":
            keylogger.resume()
            self.update_lbl_status("Running")
            self.btn_toggle['text'] = "Pause"

    def stop_keylogger(self, event):
        # Stop keylogger
        keylogger.stop()
        self.btn_toggle['text'] = "Start"
        self.btn_stop['state'] = 'disabled'
        self.update_lbl_status("Stopped")
        self.update_routing_table()

    def set_profile(self, var, ix, op):
        keylogger.set_profile(self.curr_profile.get())
        self.save_preferences()
        
        if self.use_default_dir.get():
            self.update_lbl_logdir()
            keylogger.set_log_directory(self.get_default_log_directory())
        

    def set_character(self, var, ix, op):
        keylogger.set_character(self.curr_character.get())
        self.save_preferences()

        if self.use_default_dir.get():
            self.update_lbl_logdir()
            keylogger.set_log_directory(self.get_default_log_directory())
        

    # Settings widget behavior
    def update_lbl_pausekey(self, key):
        self.lbl_pausekey['text'] = f"Pause key: {key}"

    def update_lbl_logdir(self):
        if self.use_default_dir.get():
            self.lbl_log_dir['text'] = self.get_default_log_directory()
        else:
            self.lbl_log_dir['text'] = self.log_dir

    def set_pausekey(self, event):
        self.focus() # Take focus off entry widget
        userinput = self.ent_pausekey.get()
        self.ent_pausekey.delete(0, 'end')
        
        self.pausekey = userinput
        keylogger.set_pause_key(self.pausekey)
        self.update_lbl_pausekey(userinput)

        self.save_preferences()

    def ent_pausekey_update(self, event):
        # Update contents of entry widget with key pressed
        self.ent_pausekey.config(state='normal')
        self.ent_pausekey.delete(0, 'end')
        self.ent_pausekey.insert(0, event.keysym)
        self.ent_pausekey.config(state='readonly')

    def toggle_override(self, var, ix, op):
        # Default
        if self.use_default_dir.get():
            self.lbl_log_dir['text'] = self.get_default_log_directory()
            self.ent_log_dir.config(state='disabled')
            self.btn_set_log_dir.config(state='disabled')
            keylogger.set_log_directory(self.get_default_log_directory())
        # Override
        else:
            self.ent_log_dir.config(state='normal')
            self.btn_set_log_dir.config(state='normal')
            self.lbl_log_dir['text'] = self.log_dir
            keylogger.set_log_directory(self.log_dir)
        

    def set_log_directory(self, event):

        if event.widget.cget('state') == 'disabled':
            return

        self.focus() # Take focus off entry widget
        userinput = self.ent_log_dir.get()

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
            self.ent_log_dir.delete(0, 'end')
            self.lbl_settings_info['text'] = ""
            self.lbl_settings_info.configure(fg="#000000")

            self.log_dir = userinput
            keylogger.set_log_directory(self.log_dir)
            self.update_lbl_logdir()

            self.save_preferences()
        else:
            self.lbl_settings_info['text'] = f"Invalid directory: {userinput}"
            self.lbl_settings_info.configure(fg="#ff0000")


    """
    Method is called every 0.1s (10x per sec)
    """
    def check_status(self):
        if keylogger.running == False:
            self.btn_toggle['text'] = "Start"
            self.btn_stop['state'] = 'disabled'
            self.update_lbl_status("Stopped")
        else:
            if keylogger.paused == True:
                self.update_lbl_status("Paused")
                self.btn_toggle['text'] = "Resume"
            else:
                self.update_lbl_status("Running")
                self.btn_toggle['text'] = "Pause"
        
        minutes, seconds = divmod(keylogger.elapsed_time(), 60)
        self.elapsed_time.set(f"{minutes:02.0f}m {seconds:02.0f}s")

        if keylogger.running:
            self.after(100, self.check_status) # Run this function every 0.1s

    """
    Window configuration methods
    """
    def configure_window(self, width, height):
        self.title("Landis")
        self.resizable(False, False)
        self.rowconfigure(0, minsize=height/2, weight=1)
        self.rowconfigure(1, minsize=height/2, weight=1)
        self.columnconfigure(0, minsize=width, weight=1)
        self.attributes('-topmost',True)

    def configure_frames(self, windowwidth, windowheight):
        # Input logger status frame
        self.frm_status.rowconfigure(0, minsize=40)
        self.frm_status.rowconfigure(1, minsize=35)
        self.frm_status.columnconfigure(0, minsize=windowwidth/5, weight=1)
        self.frm_status.columnconfigure(4, minsize=windowwidth/5, weight=1)

        # Frame positioning
        self.collapse.grid(row=1, sticky="nsew")
        self.frm_status.grid(row=0, sticky="nsew")
        
        # Positioned within self.collapse.sub_frame
        self.frm_settings.grid(row=0, sticky="nsew")

    def configure_status_widgets(self):
        # Adjust widgets
        self.btn_profile.config(width=8)
        self.btn_character.config(width=8)
        self.btn_method.config(width=8)

        # Status widgets positioning
        self.lbl_running.grid(row=0, column=0, columnspan=5, sticky='s')

        self.lbl_loglength.grid(row=1, column=1, padx=10)
        self.lbl_time.grid(row=1, column=2, sticky='w')

        self.btn_toggle.grid(row=2, column=3, padx=1)
        self.btn_stop.grid(row=3, column=3, padx=1)

        self.lbl_profile.grid(row=2, column=0, sticky='e')
        self.btn_profile.grid(row=2, column=1, padx=5, sticky='e')

        self.lbl_character.grid(row=3, column=0, sticky='e')
        self.btn_character.grid(row=3, column=1, padx=5, sticky='e')

        self.lbl_method.grid(row=4, column=0, sticky='e')
        self.btn_method.grid(row=4, column=1, padx=5, sticky='e')

        self.lbl_prediction.grid(row=5, column=1, padx=10)
        self.lbl_predicted.grid(row=5, column=2, sticky='w')

        # Assign settings widget behavior
        self.btn_toggle.bind('<Button-1>', self.toggle_status)
        self.btn_stop.bind('<Button-1>', self.stop_keylogger)
        self.curr_profile.trace('w', self.set_profile)
        self.curr_character.trace('w', self.set_character)

        # Fill text fields with initial values
        self.update_lbl_status("Not started")

    def configure_settings_widgets(self):
        # Settings widgets positioning
        self.lbl_settings_info.grid(row=5, columnspan=2) # Along the bottom

        # Position pausekey widgets
        self.lbl_pausekey.grid(row=0, column=0)
        self.ent_pausekey.grid(row=1, column=0)
        self.btn_setpausekey.grid(row=2, column=0, padx=15)

        # Log directory label
        self.lbl_log_dir.grid(row=0, column=1)

        # Enter logfile directory
        self.chk_override.grid(row=3, column=1)
        self.ent_log_dir.grid(row=1, column=1)
        self.btn_set_log_dir.grid(row=2, column=1)

        # Assign settings widget behavior
        self.use_default_dir.trace('w', self.toggle_override)

        self.btn_setpausekey.bind('<Button-1>', self.set_pausekey)
        self.ent_pausekey.bind('<Return>', self.set_pausekey)

        self.btn_set_log_dir.bind('<Button-1>', self.set_log_directory)
        self.ent_log_dir.bind('<Return>', self.set_log_directory)

        # Capture special keys in entry widget
        self.ent_pausekey.bind('<Key>', self.ent_pausekey_update)

        # Fill text fields with initial values
        self.update_lbl_pausekey(self.pausekey)
        self.update_lbl_logdir()



# Create main window
gui = LandisLogger()

# Block until window closes
gui.mainloop()