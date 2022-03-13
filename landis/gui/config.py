from gui import actions

"""
Window configuration methods
"""
def configure_window(gui_app, width, height):
    gui_app.title("Landis")
    gui_app.resizable(False, False)
    gui_app.rowconfigure(0, minsize=height/2, weight=1)
    gui_app.rowconfigure(1, minsize=height/2, weight=1)
    gui_app.columnconfigure(0, minsize=width, weight=1)
    gui_app.attributes('-topmost',True)

def configure_frames(gui_app, windowwidth, windowheight):
    # Input logger status frame
    gui_app.frm_status.rowconfigure(0, minsize=40)
    gui_app.frm_status.rowconfigure(1, minsize=35)
    gui_app.frm_status.columnconfigure(0, minsize=windowwidth/5, weight=1)
    gui_app.frm_status.columnconfigure(4, minsize=windowwidth/5, weight=1)

    # Frame positioning
    gui_app.collapse.grid(row=1, sticky="nsew")
    gui_app.frm_status.grid(row=0, sticky="nsew")
    
    # Positioned within gui_app.collapse.sub_frame
    gui_app.frm_settings.grid(row=0, sticky="nsew")

def configure_status_widgets(gui_app):
    gui_app.title("test")
    # Adjust widgets
    gui_app.btn_profile.config(width=8)
    gui_app.btn_character.config(width=8)
    gui_app.btn_method.config(width=8)
    gui_app.btn_target.config(width=8)

    # Status widgets positioning
    gui_app.lbl_running.grid(row=0, column=0, columnspan=5, sticky='s')

    gui_app.lbl_loglength.grid(row=1, column=1, padx=10)
    gui_app.lbl_time.grid(row=1, column=2, sticky='w')

    gui_app.lbl_result.grid(row=5,column=3,padx=1)
    gui_app.btn_toggle.grid(row=2, column=3, padx=1)
    gui_app.btn_stop.grid(row=3, column=3, padx=1)
    gui_app.btn_save.grid(row=4, column=3, padx=1)

    gui_app.lbl_profile.grid(row=2, column=0, sticky='e')
    gui_app.btn_profile.grid(row=2, column=1, padx=5, sticky='e')

    gui_app.lbl_character.grid(row=3, column=0, sticky='e')
    gui_app.btn_character.grid(row=3, column=1, padx=5, sticky='e')

    gui_app.lbl_method.grid(row=4, column=0, sticky='e')
    gui_app.btn_method.grid(row=4, column=1, padx=5, sticky='e')

    gui_app.lbl_target.grid(row=5, column=0, sticky='e')
    gui_app.btn_target.grid(row=5, column=1, padx=5, sticky='e')

    gui_app.btn_verify.grid(row=6, column=1, padx=1)

    #gui_app.lbl_prediction.grid(row=5, column=1, padx=10)
    gui_app.lbl_predicted.grid(row=6, column=2, columnspan=3, sticky='w')

    # Fill text fields with initial values
    actions.update_lbl_status("Not started")

def configure_settings_widgets(gui_app):
    # Settings widgets positioning
    gui_app.lbl_settings_info.grid(row=5, columnspan=2) # Along the bottom

    # Position pausekey widgets
    gui_app.lbl_pausekey.grid(row=0, column=0)
    gui_app.ent_pausekey.grid(row=1, column=0)
    gui_app.btn_setpausekey.grid(row=2, column=0, padx=15)

    # Log directory label
    gui_app.lbl_log_dir.grid(row=0, column=1)

    # Enter logfile directory
    gui_app.chk_override.grid(row=3, column=1)
    gui_app.ent_log_dir.grid(row=1, column=1)
    gui_app.btn_set_log_dir.grid(row=2, column=1)

    

    # Fill text fields with initial values
    actions.update_lbl_pausekey(gui_app.pausekey)
    actions.update_lbl_logdir()